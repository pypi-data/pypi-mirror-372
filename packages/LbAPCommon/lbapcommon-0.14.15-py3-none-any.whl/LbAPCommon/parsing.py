###############################################################################
# (c) Copyright 2021-2022 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import re
import warnings
from collections import OrderedDict
from copy import deepcopy
from os.path import isfile, join, relpath
from unittest import TestCase

import yaml
from strictyaml import (
    Any,
    Bool,
    Enum,
    Float,
    Int,
    Map,
    MapPattern,
    Optional,
    Regex,
    Seq,
    Str,
    load,
)

from LbAPCommon import config
from LbAPCommon.linting.bk_paths import validate_bk_query
from LbAPCommon.models import parse_yaml as parse_yaml_pydantic

RE_APPLICATION = r"^(([A-Za-z]+/)+v\d+r\d+(p\d+)?(\@[a-z0-9_\-\+]+)?)|(lb\-conda/[A-Za-z0-9_]+/(\d\d\d\d\-\d\d-\d\d))(_\d\d-\d\d|)"
RE_JOB_NAME = r"^[a-zA-Z0-9][a-zA-Z0-9_\-]+$"
RE_OUTPUT_FILE_TYPE = (
    r"^([A-Za-z][A-Za-z0-9_]+\.)+((ROOT|root|HIST|hist)|.?(DST|dst|mdf|MDF))$"
)
RE_OPTIONS_FN = r"^\$?[a-zA-Z0-9/\.\-\+\=_]+$"
RE_INFORM = r"^(?:[a-zA-Z]{3,}|[^@\s]+@[^@\s]+\.[^@\s]+)$"

RE_ROOT_IN_TES = r"^\/.+$"
RE_DDDB_TAG = r"^.{1,50}$"
RE_CONDDB_TAG = r"^.{1,50}$"

RE_COMMENT = r"(.{1,5000})"
DQ_FLAGS_SCHEMA = Seq(Enum(["BAD", "OK", "CONDITIONAL", "EXPRESS_OK", "UNCHECKED"]))

RE_INCLUSIVE_RUN_RANGE = r"\d+:\d+"

LEGACY_OPTIONS = {
    Optional("command"): Seq(Str()),
    "files": Seq(Regex(RE_OPTIONS_FN)),
}
LBEXEC_OPTIONS = {
    "entrypoint": Regex(r".+:.+"),
    Optional("extra_options"): MapPattern(Str(), Any()),
    Optional("extra_args"): Seq(Str()),
}

BASE_JOB_SCHEMA = {
    "application": Regex(RE_APPLICATION),
    "input": MapPattern(Str(), Any()),
    "output": Regex(RE_OUTPUT_FILE_TYPE) | Seq(Regex(RE_OUTPUT_FILE_TYPE)),
    "options": Regex(RE_OPTIONS_FN)
    | Seq(Regex(RE_OPTIONS_FN))
    | MapPattern(Str(), Any()),
    "wg": Enum(config.known_working_groups),
    "inform": Regex(RE_INFORM) | Seq(Regex(RE_INFORM)),
    # Automatic configuration
    "automatically_configure": Bool(),
    "turbo": Bool(),
    Optional("root_in_tes"): Regex(RE_ROOT_IN_TES),
    Optional("simulation"): Bool(),
    Optional("luminosity"): Bool(),
    Optional("data_type"): Enum(config.known_data_types),
    Optional("input_type"): Enum(config.known_input_types),
    Optional("dddb_tag"): Regex(RE_DDDB_TAG),
    Optional("conddb_tag"): Regex(RE_CONDDB_TAG),
    Optional("checks"): Seq(Str()),  # TODO: replace this with a regex
    Optional("extra_checks"): Seq(
        Str()
    ),  # TODO: replace this with a regex or with something like the line below
    # Production submission metadata
    Optional("comment"): Regex(RE_COMMENT),
    Optional("tags"): MapPattern(Str(), Str()),
    "priority": Enum(config.allowed_priorities),
    "completion_percentage": Float(),
}
INPUT_SCHEMAS = {
    "bk_query": Map(
        {
            "bk_query": Str(),
            Optional("n_test_lfns", default=1): Int(),
            Optional("dq_flags"): DQ_FLAGS_SCHEMA,
            Optional("smog2_state"): Seq(Str()),
            Optional("extended_dq_ok"): Seq(Str()),
            Optional("runs"): Seq(Int() | Regex(RE_INCLUSIVE_RUN_RANGE)),
            Optional("start_run"): Int(),
            Optional("end_run"): Int(),
            Optional("input_plugin", default="default"): Enum(["default", "by-run"]),
            Optional("keep_running", default=True): Bool(),
            Optional("sample_fraction"): Float(),
            Optional("sample_seed"): Str(),
        }
    ),
    "sample": Map(
        {
            "wg": Str(),
            "analysis": Str(),
            Optional("name"): Str(),
            Optional("version"): Str(),
            Optional("tags"): MapPattern(Str(), Str()),
            Optional("n_test_lfns", default=1): Int(),
            Optional("input_plugin", default="default"): Enum(["default", "by-run"]),
            Optional("keep_running", default=True): Bool(),
        }
    ),
    "job_name": Map(
        {"job_name": Str(), Optional("filetype"): Regex(RE_OUTPUT_FILE_TYPE)}
    ),
    "transform_ids": Map(
        {
            "transform_ids": Seq(Int()),
            "filetype": Regex(RE_OUTPUT_FILE_TYPE),
            Optional("n_test_lfns", default=1): Int(),
            Optional("dq_flags"): DQ_FLAGS_SCHEMA,
            Optional("smog2_state"): Seq(Str()),
            Optional("runs"): Seq(Int() | Regex(RE_INCLUSIVE_RUN_RANGE)),
            Optional("start_run"): Int(),
            Optional("end_run"): Int(),
            Optional("sample_fraction"): Float(),
            Optional("sample_seed"): Str(),
        }
    ),
}
DEFAULT_JOB_VALUES = {
    "automatically_configure": False,
    "turbo": False,
    "completion_percentage": 100.0,
    "priority": "1b",
}

CHECK_TYPE_SCHEMAS = {
    "range": {
        Optional("mode"): Enum(config.validation_modes),
        "expression": Str(),  # TODO: replace this with a regex
        "limits": Map({"min": Float(), "max": Float()}),
        Optional("n_bins"): Int(),
        Optional("blind_ranges"): Map({"min": Float(), "max": Float()})
        | Seq(Map({"min": Float(), "max": Float()})),
        Optional("exp_mean"): Float(),
        Optional("exp_std"): Float(),
        Optional("mean_tolerance"): Float(),
        Optional("std_tolerance"): Float(),
    },
    "range_nd": {
        Optional("mode"): Enum(config.validation_modes),
        "expressions": Map(
            {  # TODO: replace Str() with a regex
                "x": Str(),
                "y": Str(),
                Optional("z"): Str(),
            }
        ),
        "limits": Map(
            {
                "x": Map({"min": Float(), "max": Float()}),
                "y": Map({"min": Float(), "max": Float()}),
                Optional("z"): Map({"min": Float(), "max": Float()}),
            }
        ),
        Optional("n_bins"): Map(
            {
                "x": Int(),
                "y": Int(),
                Optional("z"): Int(),
            }
        ),
        Optional("blind_ranges"): Seq(
            Map(
                {
                    "x": Map({"min": Float(), "max": Float()}),
                    "y": Map({"min": Float(), "max": Float()}),
                    Optional("z"): Map({"min": Float(), "max": Float()}),
                }
            )
        ),
    },
    "num_entries": {
        Optional("mode"): Enum(config.validation_modes),
        "count": Int(),
    },
    "num_entries_per_invpb": {
        Optional("mode"): Enum(config.validation_modes),
        "count_per_invpb": Float(),
        Optional("lumi_pattern"): Str(),
    },
    "range_bkg_subtracted": {
        Optional("mode"): Enum(config.validation_modes),
        "expression": Str(),
        "limits": Map({"min": Float(), "max": Float()}),
        "expr_for_subtraction": Str(),
        "mean_sig": Float(),
        "background_shift": Float(),
        "background_window": Float(),
        "signal_window": Float(),
        Optional("n_bins"): Int(),
        Optional("blind_ranges"): Map({"min": Float(), "max": Float()})
        | Seq(Map({"min": Float(), "max": Float()})),
    },
    "branches_exist": {
        Optional("mode"): Enum(config.validation_modes),
        "branches": Seq(Str()),
    },
}
BASIC_VALIDATION_SCHEMAS = {
    validation_type: {"mode": Enum(config.validation_modes)}
    for validation_type in config.validation_types
}
CHECK_TYPE_SCHEMAS = {**CHECK_TYPE_SCHEMAS, **BASIC_VALIDATION_SCHEMAS}
BASE_CHECK_SCHEMA = {
    "type": Enum(list(CHECK_TYPE_SCHEMAS)),
    Optional("tree_pattern"): Str(),
}
BASE_CHECK_DEFAULT_VALUES = {
    "tree_pattern": r"(.*/DecayTree)|(.*/MCDecayTree)",
}
CHECK_TYPE_DEFAULT_VALUES = {
    "mode": "Strict",
    "num_entries": {},
    "range": {
        "n_bins": 50,
    },
    "range_nd": {
        "n_bins": {
            "x": 50,
            "y": 50,
            "z": 50,
        },
    },
    "num_entries_per_invpb": {
        "lumi_pattern": r"(.*/LumiTuple)",
    },
    "range_bkg_subtracted": {
        "n_bins": 50,
    },
    "branches_exist": {},
}
BASIC_VALIDATION_DEFAULT_VALUES = {
    validation_type: {"mode": "Strict"} for validation_type in config.validation_types
}
CHECK_TYPE_DEFAULT_VALUES = {
    **CHECK_TYPE_DEFAULT_VALUES,
    **BASIC_VALIDATION_DEFAULT_VALUES,
}


def _ordered_dict_to_dict(a):
    if isinstance(a, (OrderedDict, dict)):
        return {k: _ordered_dict_to_dict(v) for k, v in a.items()}
    elif isinstance(a, (list, tuple)):
        return [_ordered_dict_to_dict(v) for v in a]
    else:
        return a


def _validate_proc_pass_map(job_names, proc_pass_map):
    """Build processing paths and validate them from a processing pass map.

    Given a list of step job names (in correct order), and the processing pass map,
    build the processing path for each step and verify the length is below 100.

    Args:
        job_names (list[str]): a list containing step job names.
        proc_pass_map (dict): A dictionary mapping job names to processing pass

    Raises:
        ValueError: raised if the processing path length is over 100 characters
    """
    for i, job_name in enumerate(job_names):
        proc_passes = map(proc_pass_map.get, job_names[:i] + [job_name])
        pro_path = "/".join(proc_passes)
        if len(pro_path) >= 100:
            proc_pass = proc_pass_map[job_name]
            step_jobs_list = "  - " + "\n  - ".join(job_names)
            raise ValueError(
                f"The expected processing path length for the job {job_name!r} is too long.\n"
                "DIRAC requires this to be less than 100 characters.\n\n"
                f"'Step' jobs:\n{step_jobs_list!r}\n"
                f"Job name: {job_name!r}\n"
                f"Processing pass for this step: {proc_pass!r}\n"
                f"Processing path for this step ({len(pro_path)} chars): {pro_path}\n\n"
                "To recover from this issue, consider:"
                "  - Removing redundant information from your job name.\n"
                "  - Shortening your job names.\n"
                "  - If the offending job depends on output from other jobs, ensure that they have a common prefix.\n"
            )


def create_proc_pass_map(job_names, version, default_proc_pass="default"):
    """Create a job name to processing pass map.

    Given a list of step job names and the production version, produce a
    job_name --> processing pass mapping.

    Args:
        job_names (list): step job names
        version (str): LbAPproduction version
        default_proc_pass (str, optional): the default processing pass. Defaults to "default".

    Returns:
        dict: a step job name to processing pass map
    """
    proc_pass_prefix = f"AnaProd-{version}-"
    proc_pass_map = {}

    # dummy_version = "v0r0p00000000"

    def clean_proc_pass(i, original_job_name):
        # attempt to remove redundant information from the job name
        job_name = re.sub(
            r"([0-9]{8})|(MagUp|MagDown|MU|MD)|((^|[^0*9])201[125678]($|[^0*9]))",
            "",
            original_job_name,
        )
        # Remove repeated separator chatacters
        job_name = re.sub(r"([-_])[-_]+", r"\1", job_name).strip("_-")
        if i == 0:
            return f"{proc_pass_prefix}{job_name}"

        proc_pass = job_name
        for previous_job_name in job_names[:i]:
            size = 0
            previous_proc_pass = proc_pass_map[previous_job_name]
            # Remove the prefix if this is the first job
            if previous_proc_pass.startswith(proc_pass_prefix):
                previous_proc_pass = previous_proc_pass[len(proc_pass_prefix) :]
            # Look for a common prefix and remove it
            for last, this in zip(previous_proc_pass, proc_pass):
                if last != this:
                    break
                size += 1
            proc_pass = proc_pass[size:].strip("_-+")
            # If the processing pass has been entirely stripped use a default
            if not proc_pass:
                proc_pass = default_proc_pass

        return proc_pass

    for i, job_name in enumerate(job_names):
        proc_pass_map[job_name] = clean_proc_pass(i, job_name)

    _validate_proc_pass_map(job_names, proc_pass_map)

    return proc_pass_map


def is_simulation_job(prod_data: dict, job_name: str):
    """Determine if a job is using MC input or not.

    Args:
        prod_data (dict): Entire production information from yaml parsing
        job_name (str): Name of the job to determine if it's using MC input or not

    Raises:
        NotImplementedError: No bookkeeping location or job name provided.

    Returns:
        bool: True if the job is using MC input, False if it is not
    """
    job_dict = prod_data[job_name]
    if "simulation" not in job_dict:
        if "bk_query" in job_dict["input"]:
            if "/mc/" in job_dict["input"]["bk_query"].lower():
                return True
            else:
                return False
        elif "job_name" in job_dict["input"]:
            dependent_job = prod_data[job_name]["input"]["job_name"]
            return is_simulation_job(prod_data, dependent_job)
        else:
            raise NotImplementedError(
                "Input requires either a bookkeeping location or a previous job name"
            )


def parse_yaml(rendered_yaml, production_name=None, repo_root=None):
    """Parse rendered YAML text.

    Args:
        rendered_yaml (str): The rendered YAML jinja template.

    Raises:
        ValueError: raised if errors occurred during parsing.

    Returns:
        tuple: a tuple of the parsed configuration data (dict).
    """
    data1 = load(
        rendered_yaml, schema=MapPattern(Regex(RE_JOB_NAME), Any(), minimum_keys=1)
    )

    if "defaults" in data1:
        defaults_schema = {}
        for key, value in BASE_JOB_SCHEMA.items():
            if isinstance(key, Optional):
                key = key.key
            key = Optional(key, default=DEFAULT_JOB_VALUES.get(key))
            defaults_schema[key] = value

        data1["defaults"].revalidate(Map(defaults_schema))
        defaults = data1.data["defaults"]
        # Remove the defaults data from the snippet
        del data1["defaults"]
    else:
        defaults = DEFAULT_JOB_VALUES.copy()

    job_names = list(data1.data.keys())
    if len(set(n.lower() for n in job_names)) != len(job_names):
        raise ValueError(
            "Found multiple jobs with the same name but different capitalisation"
        )

    job_name_schema = Regex(r"(" + r"|".join(map(re.escape, job_names)) + r")")

    # StrictYAML has non-linear complexity when parsing many keys
    # Avoid extremely slow parsing by doing each key individually
    data2 = {}
    for k, v in data1.items():
        k = k.data
        v = _ordered_dict_to_dict(v.data)

        production_schema = {}
        if "comment" in v:
            raise ValueError(
                "comment is only allowed to be set in the defaults of the production!"
            )
        for key, value in BASE_JOB_SCHEMA.items():
            if isinstance(key, Optional):
                key = key.key
                production_schema[Optional(key, default=defaults.get(key))] = value
            elif key in defaults:
                production_schema[Optional(key, default=defaults[key])] = value
            else:
                production_schema[key] = value

        data = load(
            yaml.safe_dump({k: v}),
            MapPattern(job_name_schema, Map(production_schema), minimum_keys=1),
        )
        for input_key, input_schema in INPUT_SCHEMAS.items():
            if input_key in data.data[k]["input"]:
                data[k]["input"].revalidate(input_schema)
                break
        else:
            raise ValueError(
                (
                    "Failed to find a valid schema for %s's input. "
                    "Allowed values are: %s"
                )
                % (k, set(INPUT_SCHEMAS))
            )
        if isinstance(data.data[k]["options"], dict):
            if "files" in data.data[k]["options"]:
                data[k]["options"].revalidate(Map(LEGACY_OPTIONS))
            else:
                data[k]["options"].revalidate(Map(LBEXEC_OPTIONS))

        data_dict = data.data

        # Ensure runs is not used with start_run/end_run
        if runs := data_dict[k]["input"].get("runs"):
            if (
                "start_run" in data_dict[k]["input"]
                or "end_run" in data_dict[k]["input"]
            ):
                raise ValueError(
                    f"Both inclusive run ranges and start/end runs are specified for {k}"
                )
            # If a single run range is specified, convert it to start/end runs
            if len(runs) == 1 and isinstance(runs[0], str):
                del data_dict[k]["input"]["runs"]
                start_run, end_run = map(int, runs[0].split(":"))
                data_dict[k]["input"]["start_run"] = start_run
                data_dict[k]["input"]["end_run"] = end_run
        if "start_run" in data_dict[k]["input"] and "end_run" in data_dict[k]["input"]:
            start_run = data_dict[k]["input"]["start_run"]
            end_run = data_dict[k]["input"]["end_run"]
            if start_run >= end_run:
                raise ValueError(
                    f"Start run {start_run} must be less than end run {end_run} for {k}"
                )

        data2.update(data_dict)

    # check against pydantic
    pyd_result = parse_yaml_pydantic(rendered_yaml, production_name, repo_root)

    data3 = None

    def convert_to_warning(e):
        warning = RuntimeWarning(*e.args)
        return warning.with_traceback(e.__traceback__)

    try:
        data3 = deepcopy(data2)
        validate_yaml(data3, repo_root or None, production_name or "")
        tc = TestCase()
        tc.maxDiff = None
        tc.assertDictEqual(
            data3,
            pyd_result,
            msg="Mismatch between StrictYAML and pydantic output!",
        )
    except Exception as e:
        warnings.warn(convert_to_warning(e), stacklevel=2)

    return data2


def _normalise_filetype(prod_name, job_name, filetype):
    filetype = filetype.upper()

    errors = []
    if len(filetype) >= 50:
        errors += ["The filetype is excessively long"]
    if re.findall(r"[0-9]{8}", filetype, re.IGNORECASE):
        errors += ["It appears the event type is included"]
    if re.findall(r"Mag(Up|Down)", filetype, re.IGNORECASE):
        errors += ["It appears the magnet polarity is included"]
    if re.findall(r"(^|[^0*9])201[125678]($|[^0*9])", filetype, re.IGNORECASE):
        errors += ["It appears the data taking year is included"]

    if errors:
        _errors = "\n  * ".join(errors)
        raise ValueError(
            f"Output filetype {filetype} for {prod_name}/{job_name} is invalid "
            f"as it appears to contain redundant information.\n\n"
            f"  * {_errors}"
        )
    return filetype


def _check_name_magnet_polarity(bk_query, job_name):
    match = re.search(r"-mag(up|down)[-/]", bk_query)
    if not match:
        return [f"Failed to find magnet polarity in {bk_query}"]
    good_pol = match.groups()[0]
    bad_pol = {"down": "up", "up": "down"}[good_pol]
    if f"mag{bad_pol}" in job_name:
        raise ValueError(
            f"Found 'mag{bad_pol}' in job name {job_name!r} with"
            f"'mag{good_pol}' input ({bk_query!r}). "
            "Has the wrong magnet polarity been used?"
        )
    match = re.search(r"([^a-z0-9]|\b)m(u|d)([^a-z0-9]|\b)", job_name)
    if match and match.groups()[1] == bad_pol[0]:
        raise ValueError(
            f"Found 'm{bad_pol[0]}' in job name {job_name!r} with"
            f" 'mag{good_pol}' input ({bk_query!r}). "
            "Has the wrong magnet polarity been used?"
        )
    return []


def validate_yaml(jobs_data, repo_root, prod_name):
    """Validate YAML configuration for anything that would definitely break a job or the production.

    Args:
        jobs_data (dict): Parsed job configuration.
        repo_root (str): Repository location.
        prod_name (str): Production name.

    Raises:
        ValueError: Raised if there are showstopper issues in the parsed job configuration.
    """
    # Ensure all values that can be either a list or a string are lists of strings
    for job_name, _ in jobs_data.items():
        try:
            _validate_job_data(repo_root, prod_name, job_name, jobs_data)
        except Exception as e:
            raise ValueError(f"Failed to validate {job_name!r} with error {e!r}") from e

    # Ensure job name inputs are unambiguous
    for job_name, job_data in jobs_data.items():
        if "job_name" in job_data["input"]:
            if job_data["input"]["job_name"] not in jobs_data:
                raise ValueError(
                    f"Unrecognised job name in input: {job_data['input']['job_name']}"
                )
            input_job_data = jobs_data[job_data["input"]["job_name"]]
            input_filetype = job_data["input"].get("filetype", "").upper()
            if len(input_job_data["output"]) == 1:
                if input_filetype not in [""] + input_job_data["output"]:
                    raise ValueError(
                        f"Unrecognised {input_filetype=} for {job_name=} input, "
                        f"expected one of: {input_job_data['output']}"
                    )
            elif input_filetype == "":
                raise ValueError(
                    f"{job_name} gets its input from a job with multiple outputs. "
                    "The 'filetype' key must be specified in the 'input' section."
                )
            elif input_filetype.upper() not in input_job_data["output"]:
                raise ValueError(
                    f"Unrecognised {input_filetype=} for {job_name=} input, "
                    f"expected one of: {input_job_data['output']}"
                )


def _validate_job_data(repo_root, prod_name, job_name, jobs_data):
    job_data = jobs_data[job_name]
    # Normalise list/str fields to always be lists
    for prop in ["output", "options", "inform", "checks", "extra_checks"]:
        if not isinstance(job_data.get(prop, []), (list, dict)):
            job_data[prop] = [job_data[prop]]

    # Validate the input data
    if "bk_query" in job_data["input"]:
        validate_bk_query(job_data["input"]["bk_query"])

    # Validate the output filetype
    job_data["output"] = [
        _normalise_filetype(prod_name, job_name, s) for s in job_data["output"]
    ]

    # Normalise the options filenames if we're using a non-PyConf application
    if isinstance(job_data["options"], list):
        job_data["options"] = {"files": job_data["options"]}
    if "files" in job_data["options"]:
        normalised_options = []
        for fn in job_data["options"]["files"]:
            if fn.startswith("$"):
                normalised_options.append(fn)
                continue

            fn_normed = (
                fn
                if repo_root is None
                else relpath(join(repo_root, fn), start=repo_root)
            )
            if fn_normed.startswith("../"):
                raise ValueError(f"{fn} not found inside {repo_root}")
            if repo_root is not None and not isfile(
                join(repo_root, prod_name, fn_normed)
            ):
                raise FileNotFoundError(
                    f"Production {job_name!r} has a missing options file: "
                    f"{join(prod_name, fn_normed)!r}",
                )
            normalised_options.append(
                join("$ANALYSIS_PRODUCTIONS_BASE", prod_name, fn_normed)
            )
        job_data["options"]["files"] = normalised_options

    # Validate the completion percentage
    if not (10 <= job_data["completion_percentage"] <= 100):
        raise ValueError(
            f"Validation failed for job {job_name!r}, completion_percentage "
            f"was set to {job_data['completion_percentage']!r}, allowed "
            "values are in the interval [10, 100]."
        )
