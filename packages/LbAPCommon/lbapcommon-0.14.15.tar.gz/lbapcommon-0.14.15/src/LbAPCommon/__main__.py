###############################################################################
# (c) Copyright 2024 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import argparse
import asyncio
import datetime
import importlib.resources
import json
import logging
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from enum import StrEnum
from pathlib import Path

import jinja2
import yaml

from LbAPCommon import parse_yaml, render_yaml, validate_yaml
from LbAPCommon.dirac_conversion import (
    group_in_to_requests,
    parse_application_string,
    step_to_production_request,
)

yaml.SafeDumper.add_multi_representer(
    StrEnum,
    yaml.representer.SafeRepresenter.represent_str,
)


# Ensure that warnings are enabled
os.environ["PYTHONWARNINGS"] = "default"

# Ensure that logging captures warnings issued by warnings.warn()
logging.captureWarnings(True)

if "LBAP_COMMON_SENTRY_DSN" in os.environ:
    from importlib.metadata import version

    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    release_string = version("LbAPCommon")
    sentry_sdk.init(  # pylint: disable=abstract-class-instantiated
        os.environ["LBAP_COMMON_SENTRY_DSN"],
        integrations=[
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs (this is the default)
                event_level=logging.WARNING,  # Send warnings as events (default is logging.ERROR)
            )
        ],
        release=release_string,
    )


templates = jinja2.Environment(
    loader=jinja2.PackageLoader("LbAPCommon", "data/templates"),
    undefined=jinja2.StrictUndefined,
)


def generate_auto_configuration(prod_name, name, job_data):
    """Generate the auto-configuration for the job."""
    if "files" not in job_data["options"]:
        raise NotImplementedError(
            "generate_configuration is not yet supported for lbexec based jobs"
        )

    render_kwargs = dict(
        application_name=parse_application_string(job_data["application"])["name"],
        data_type=job_data["data_type"],
        input_type=job_data["input_type"],
        luminosity=job_data["luminosity"],
        root_in_tes=job_data["root_in_tes"],
        simulation=job_data["simulation"],
        turbo=job_data["turbo"],
    )
    if job_data["simulation"]:
        render_kwargs["conddb_tag"] = job_data["conddb_tag"]
        render_kwargs["dddb_tag"] = job_data["dddb_tag"]

    autoconf_options = templates.get_template(
        "configure-legacy-application.py.j2"
    ).render(**render_kwargs)

    dynamic_options_path = os.path.join(prod_name, f"{name}_autoconf.py")

    dynamic_options_name = os.path.join(
        "$ANALYSIS_PRODUCTIONS_DYNAMIC", dynamic_options_path
    )
    if job_data["options"].get("command") == ["python"]:
        job_data["options"]["files"].insert(1, dynamic_options_name)
    else:
        job_data["options"]["files"].insert(0, dynamic_options_name)

    return dynamic_options_path, autoconf_options


def deal_with_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


async def query_dirac(
    sem,
    query_script,
    name,
    job_data,
    output_path,
    server_credentials,
):
    """Query LHCbDIRAC to get metadata about the job's input."""
    async with sem:
        cmd = [
            "lb-dirac",
            query_script,
            json.dumps(job_data["input"], default=deal_with_datetime),
            f"--output={output_path}",
        ]
        if job_data["turbo"]:
            cmd += ["--turbo"]
        if server_credentials:
            cmd += ["--server-credentials", *server_credentials]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, _ = await proc.communicate()
        print(f"** Output from querying LHCbDIRAC for {name}:\n{stdout.decode()}")
        if proc.returncode != 0:
            raise RuntimeError(f"Query failed for {name}:\n{stdout.decode()}")
        result = json.loads(output_path.read_text())
        return name, job_data, result


async def main(
    production_name: str,
    ap_pkg_version: str,
    input_file: Path,
    output_file: Path,
    server_credentials: tuple[str, str] | None,
    only_include: str | None,
    dump_requests: bool,
):
    """Convert info.yaml into a form which can be understood by LHCbDIRAC."""
    raw_yaml = input_file.read_text()
    sem = asyncio.Semaphore(2)

    rendered = render_yaml(raw_yaml)

    jobs_data = parse_yaml(rendered, production_name, None)
    validate_yaml(jobs_data, None, production_name)  # NOOP

    if only_include:
        for job_names in group_in_to_requests(jobs_data):
            if only_include in job_names:
                to_include = job_names[:]
                break
        else:
            raise ValueError(f"Job {only_include} not found")

    dynamic_files_by_job = defaultdict(
        lambda: {
            "__init__.py": "",
        }
    )
    input_specs = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        query_script = Path(tmpdir) / "query_dirac.py"
        query_script.write_text(
            (
                importlib.resources.files("LbAPCommon.data") / "query_dirac.py"
            ).read_text()
        )
        query_script.chmod(0o700)

        tasks = []
        for job_name, job_data in jobs_data.items():
            if "job_name" in job_data["input"]:
                # We'll handle these later
                continue
            if only_include and job_name not in to_include:
                continue
            tasks.append(
                query_dirac(
                    sem,
                    query_script,
                    job_name,
                    job_data,
                    Path(tmpdir) / f"{job_name}.json",
                    server_credentials,
                )
            )

        for result in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(result, Exception):
                raise result
            job_name, job_data, result = result
            # Store the input specs for later use
            input_specs[job_name] = result["input-spec"]

            # Generate the auto-configuration options
            if job_data["automatically_configure"]:
                if result["auto-conf-error"]:
                    raise NotImplementedError(
                        "Auto-configuration failed", job_name, result["auto-conf-error"]
                    )

                job_data = result["auto-conf-data"] | job_data
                # Mutate the original value in jobs_data
                jobs_data[job_name] = job_data

                dynamic_options_path, autoconf_options = generate_auto_configuration(
                    production_name, job_name, job_data
                )
                if dynamic_options_path in dynamic_files_by_job:
                    raise ValueError(f"Duplicate dynamic file: {dynamic_options_path}")
                dynamic_files_by_job[job_name][dynamic_options_path] = autoconf_options

    # Apply auto-configuration to the jobs that depend on other jobs
    for job_names in group_in_to_requests(jobs_data):
        for job_name in job_names[1:]:
            configure_later_step(
                production_name, jobs_data, job_name, dynamic_files_by_job
            )

    # Make sure we have at least one job
    if len(jobs_data) == 0:
        raise ValueError("No jobs found")

    # Convert the jobs data to a LHCbDIRAC production in the format expected by LbAPI
    productions = {}
    for job_names in group_in_to_requests(jobs_data):
        if only_include and job_names != to_include:
            continue
        input_spec = input_specs[job_names[0]]
        dynamic_files = {}
        for job_name in job_names:
            for k, v in dynamic_files_by_job[job_name].items():
                if k in dynamic_files and v != dynamic_files[k]:
                    raise NotImplementedError(
                        f"Duplicate dynamic file with different content: {k}"
                    )
                dynamic_files[k] = v

        result = {
            "raw-yaml": yaml.safe_dump(
                {x: jobs_data[x] for x in job_names}, sort_keys=False
            ),
            "request": step_to_production_request(
                production_name, jobs_data, job_names, input_spec, ap_pkg_version
            ),
            "input-dataset": input_spec,
            "dynamic_files": dynamic_files,
        }

        name = result["request"][0]["name"].split("#", 2)[-1]
        if name in productions:
            raise ValueError(f"Duplicate production name: {name}")
        productions[name] = result

    metadata = {
        "rendered_yaml": rendered,
        "check_data": [],
        "productions": productions,
    }
    output_file.write_text(json.dumps(metadata))

    if dump_requests:
        for job, request in metadata["productions"].items():
            p = output_file.with_name(job).with_suffix(".yaml")
            with open(p, "w") as f:
                yaml.dump(request["request"], f)


def configure_later_step(production_name, jobs_data, job_name, dynamic_files_by_job):
    """Configure a job that depends on another job."""
    if "job_name" not in jobs_data[job_name]["input"]:
        raise RuntimeError("This should be impossible")

    input_job_name = jobs_data[job_name]["input"]["job_name"]
    input_job_data = jobs_data[input_job_name]

    # If no input filetype is specified, try to set it automatically
    if (
        "filetype" not in jobs_data[job_name]["input"]
        or jobs_data[job_name]["input"]["filetype"] is None
    ):
        if len(input_job_data["output"]) != 1:
            raise ValueError(
                f"No input filetype specified for {job_name} but "
                f"{input_job_name} has multiple output files"
            )
        jobs_data[job_name]["input"]["filetype"] = input_job_data["output"][0]
    jobs_data[job_name]["input"]["filetype"] = jobs_data[job_name]["input"][
        "filetype"
    ].upper()

    # Validate the input filetype
    if jobs_data[job_name]["input"]["filetype"] not in input_job_data["output"]:
        raise ValueError(
            f"Input filetype {jobs_data[job_name]['input']['filetype']} "
            f"for {job_name} not found in {input_job_name}'s output"
        )

    # If the job is not automatically configured there is nothing left to do
    if not jobs_data[job_name]["automatically_configure"]:
        return

    # Get information about the input job
    if not input_job_data["automatically_configure"]:
        raise ValueError("Can only automatically configure jobs with automatic input")

    # Copy any missing values from the input job
    jobs_data[job_name].setdefault("input_type", input_job_data["input_type"])
    jobs_data[job_name].setdefault("simulation", input_job_data["simulation"])
    jobs_data[job_name].setdefault("data_type", input_job_data["data_type"])
    if jobs_data[job_name]["simulation"]:
        jobs_data[job_name].setdefault("dddb_tag", input_job_data["dddb_tag"])
        jobs_data[job_name].setdefault("conddb_tag", input_job_data["conddb_tag"])
    jobs_data[job_name].setdefault("luminosity", not jobs_data[job_name]["simulation"])
    # TODO: Set this automatically
    jobs_data[job_name].setdefault("root_in_tes", None)

    # Generate the auto-configuration options
    dynamic_options_path, autoconf_options = generate_auto_configuration(
        production_name, job_name, jobs_data[job_name]
    )
    if dynamic_options_path in dynamic_files_by_job:
        raise ValueError(f"Duplicate dynamic file: {dynamic_options_path}")
    dynamic_files_by_job[job_name][dynamic_options_path] = autoconf_options


def production_name_type(
    value: str, pattern=re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,199}$")
) -> str:
    if not pattern.match(value):
        raise argparse.ArgumentTypeError(f"{value=} does not match {pattern=}")
    return value


def parse_args():
    """Parse the command line arguments and then call main."""
    parser = argparse.ArgumentParser()
    parser.add_argument("production_name", type=production_name_type)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ap-pkg-version", default="v999999999999")
    parser.add_argument("--server-credentials", nargs=2)
    parser.add_argument("--only-include", default=None)
    parser.add_argument("--dump-requests", action="store_true", default=False)
    args = parser.parse_args()

    asyncio.run(
        main(
            args.production_name,
            args.ap_pkg_version,
            args.input,
            args.output,
            args.server_credentials,
            args.only_include,
            args.dump_requests,
        )
    )


if __name__ == "__main__":
    parse_args()
