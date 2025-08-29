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
__all__ = (
    "group_in_to_requests",
    "parse_application_string",
    "step_to_production_request",
)
import os
from datetime import datetime
from difflib import SequenceMatcher
from hashlib import md5
from itertools import chain, tee

import networkx as nx

from LbAPCommon.models import create_proc_pass_map
from LbAPCommon.workflow import WorkflowSolver


class InvalidAPJob(ValueError):
    pass


def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def make_sample_max_hash(fraction):
    upper_limit = (2**128) - 1
    width = int(upper_limit * fraction)
    return f"{width:032x}".upper()


def group_in_to_requests(jobs_data):
    """Build the Production Requests for the analysis productions "jobs".

    Each production request can be made up of one or more jobs, which must be
    a flat dependency chain. This function will attempt to group the "jobs" and
    raises an InvalidAPJob exception if the constraints are violated.
    """
    G = nx.DiGraph()
    for name, job_data in jobs_data.items():
        G.add_node(name)
        if "job_name" in job_data["input"]:
            G.add_edge(job_data["input"]["job_name"], name)

    # Check for cycles
    if not nx.is_directed_acyclic_graph(G):
        raise InvalidAPJob("Graph contains a cycle")

    all_paths = []
    for components in nx.weakly_connected_components(G):
        subgraph = G.subgraph(components)
        if not sum(G.in_degree(node) == 0 for node in subgraph.nodes()) == 1:
            raise InvalidAPJob("Must have only one node with zero input degrees")
        all_paths.append([job_name for job_name in nx.topological_sort(subgraph)])

    assert len(jobs_data) == sum(map(len, all_paths))
    return all_paths


def parse_application_string(string):
    """Parse the application string into a dictionary.

    The application string is in the format `name/version[@binary_tag]`.
    """
    application = {
        "name": "/".join(string.split("/")[:-1]),
        "version": string.split("/")[-1],
    }
    if "@" in application["version"]:
        app_version, binary_tag = application["version"].split("@", 1)
        application["version"] = app_version
        application["binary_tag"] = binary_tag
    return application


def is_run3_dst_mdst_output(input_step):
    app_name = input_step["application"]["name"]
    app_ver = input_step["application"]["version"]
    if app_name == "Castelao":
        return False
    if app_name == "Allen":
        return True
    if app_name == "Franklin":
        # check if the input options are lbexec-style
        if isinstance(input_step.get("options"), dict) and input_step["options"].get(
            "entrypoint"
        ):
            return True
        return False

    app_run3_min_ver = {
        "DaVinci": 50,
        "Moore": 50,
    }
    if app_name not in app_run3_min_ver:
        raise NotImplementedError(
            f"Unable to support merging MDST/DST output for {app_name}/{app_ver}"
        )
    # crudely parse the version
    app_ver_maj, _ = app_ver.removeprefix("v").split("r", 2)
    if int(app_ver_maj) >= app_run3_min_ver[app_name]:
        return True
    return False


def step_to_production_request(prod_name, jobs_data, job_names, input_spec, tag_name):
    """Convert a AnalysisProductions step object to a LHCbDIRAC production."""
    wgs = {jobs_data[n]["wg"] for n in job_names}
    if len(wgs) != 1:
        raise NotImplementedError("Found a step with multiple WGs: " + repr(job_names))
    wg = wgs.pop()

    proc_pass_map = create_proc_pass_map(job_names, tag_name)

    # Remove duplicated parts of the production name to avoid it being too long
    step_name = job_names[0]
    for a, b in pairwise(job_names):
        match = SequenceMatcher(None, a, b).find_longest_match()
        step_name += "," + b.replace(a[match.a : match.a + match.size], "")

    data = {
        "type": "AnalysisProduction",
        "name": f"AnaProd#{prod_name}#{step_name}",
        "priority": jobs_data[job_names[0]]["priority"],
        "inform": list(set(chain(*[jobs_data[n]["inform"] for n in job_names]))),
        "wg": wg,
        "comment": jobs_data[job_names[0]].get("comment", ""),
        "input_dataset": {
            k: input_spec[k]
            for k in {"conditions_dict", "conditions_description", "event_type"}
        },
        "steps": [],
    }

    data["input_dataset"]["launch_parameters"] = {
        "run_numbers": (
            list(map(str, input_spec.get("run-numbers")))
            if isinstance(input_spec.get("run-numbers"), list)
            else input_spec.get("run-numbers")
        ),
        "start_run": input_spec.get("start-run"),
        "end_run": input_spec.get("end-run"),
    }
    if input_spec.get("sample_frac") or input_spec.get("sample_seed"):
        if not (input_spec.get("sample_seed") and input_spec.get("sample_frac")):
            raise ValueError(
                "Both sample_frac and sample_seed must be set, or not set at all."
            )
        data["input_dataset"]["launch_parameters"]["sample_max_md5"] = (
            make_sample_max_hash(input_spec.get("sample_frac"))
        )
        data["input_dataset"]["launch_parameters"]["sample_seed_md5"] = (
            md5(input_spec.get("sample_seed").encode("utf-8")).hexdigest().upper()
        )

    wf = WorkflowSolver(data)

    for i, job_name in enumerate(job_names):
        job_data = jobs_data[job_name]

        options = {}
        if isinstance(job_data["options"], list):
            options["files"] = job_data["options"]
            options["format"] = "WGProd"
        elif isinstance(job_data["options"], dict) and "files" in job_data["options"]:
            if "command" in job_data["options"]:
                options["command"] = job_data["options"]["command"]
            options["files"] = job_data["options"]["files"]
            options["format"] = "WGProd"
        elif isinstance(job_data["options"], dict):
            options["entrypoint"] = job_data["options"]["entrypoint"]
            options["extra_options"] = job_data["options"]["extra_options"]
            if "extra_args" in job_data["options"]:
                options["extra_args"] = job_data["options"]["extra_args"]
        else:
            raise NotImplementedError(type(job_data["options"]), job_data["options"])

        wf.append_step(
            {
                "name": f"AnaProd#{tag_name}#{job_name}",
                "processing_pass": proc_pass_map[job_name],
                "application": parse_application_string(job_data["application"]),
                "options": options,
                "data_pkgs": [{"name": "AnalysisProductions", "version": tag_name}],
                "input": [
                    {
                        "type": filename_from_input(job_data["input"], input_spec),
                        "visible": i == 0,
                    }
                ],
                "output": [
                    {"type": ft, "visible": False} for ft in sorted(job_data["output"])
                ],
                "visible": True,
                "ready": True,
                "obsolete": True,
            }
        )
    # check the graph makes sense so far...
    # it is possible to have isolated nodes at this point
    # as we have not added any merge steps
    wf.validate_graph(allow_isolated=True)

    print(wf.G)

    # look at all the final output nodes and their filetypes
    output_leaves = wf.check_output_leaves()
    trf_ofts = []
    trf_merge_steps = set()
    for node, ofts in output_leaves.items():
        if not ofts:  # This node doesn't have any dangling OFTs - no merge step needed.
            continue
        for ft in ofts:
            if ft in trf_ofts:
                raise ValueError("Output filetype leaves per request MUST be unique!")
        trf_ofts.extend(ofts)
        # be careful that we only have one merge step per transform with output leaves.
        trf_i = wf.trf_idx_from_step_idx(node)
        if trf_i in trf_merge_steps:
            raise ValueError(
                "More than one merge step cannot be created for each transformation"
            )
        trf_merge_steps.add(trf_i)

        merge_step = {
            "name": f"AnaProd#MergeV2#{prod_name}#merge{trf_i}",
            "processing_pass": "merged",
            "application": {
                "name": "lb-conda/default",
                "version": os.environ.get("LBAP_MERGE_VERSION", "2025-02-14"),
            },
            "options": {
                "entrypoint": "LbExec:skim_and_merge",
                "extra_options": {
                    "compression": {
                        "level": int(os.environ.get("LBAP_MERGE_COMPRESSION", 6)),
                        "algorithm": "ZSTD",
                        "optimise_baskets": True,
                    }
                },
                "extra_args": [],
            },
            "input": [{"type": str(ft), "visible": False} for ft in sorted(ofts)],
            "output": [{"type": str(ft), "visible": True} for ft in sorted(ofts)],
            "visible": False,
            "ready": True,
            "obsolete": True,
        }

        # And for run 3 ...
        dst_merging_run3 = {
            "application": {
                "name": "LHCb",
                "version": "v58r2",
            },
            "data_pkgs": [],
            "options": {
                "entrypoint": "GaudiConf.mergeDST:dst",
                "extra_options": {
                    "input_process": "Hlt2",
                    "input_type": "ROOT",
                    "input_raw_format": 0.5,
                    "data_type": "Upgrade",
                    "simulation": False,
                    "geometry_version": "run3/2024.Q1.2-v00.00",
                    "conditions_version": "master",
                    "output_type": "ROOT",
                    "compression": f"ZSTD:{int(os.environ.get('LBAP_MERGE_COMPRESSION', 6))}",
                },
            },
        }

        # And for MDF
        dst_merging_run3 = {
            "application": {
                "name": "lb-conda/default",
                "version": os.environ.get("LBAP_MERGE_VERSION", "2025-02-14"),
            },
            "data_pkgs": [],
            "options": {
                "entrypoint": "LbExec.workflows:merge_mdf",
                "extra_options": {
                    # Disable compression for now as Allen doesn't support it
                    # "compression": {
                    #     "level": int(os.environ.get("LBAP_MERGE_COMPRESSION", 9)),
                    #     "algorithm": "ZSTD",
                    #     "optimise_baskets": True,
                    # },
                },
            },
        }

        for ft in ofts:
            if ft.endswith(("MDF", ".MDF")):
                merge_step.update(dst_merging_run3)
            elif ft.endswith(".MDST") or ft.endswith(".DST"):
                # Check the input steps to the merging step and determine if they are
                # run 2 or run 3 jobs
                input_step = wf.steps[node]

                if is_run3_dst_mdst_output(input_step):
                    # run 3:
                    merge_step.update(dst_merging_run3)
                else:
                    # run 1/2:
                    # Run12 DST/MDST merging
                    dst_merging_run12 = {
                        "application": {
                            "name": "DaVinci",
                            "version": "v46r13",
                        },
                        "data_pkgs": [
                            {"name": "AppConfig", "version": "v3r442"},
                        ],
                        "options": [
                            "$APPCONFIGOPTS/Merging/DVMergeDST.py",
                            # datatype here
                            "$APPCONFIGOPTS/Merging/WriteFSR.py",
                            "$APPCONFIGOPTS/Merging/MergeFSR.py",
                            # Simulation=True/False
                        ],
                        "options_format": "merge",
                    }

                    # configure conditions options as needed
                    configName = input_spec["conditions_dict"]["configName"]
                    configVersion = input_spec["conditions_dict"]["configVersion"]
                    if configName == "MC":
                        dst_merging_run12["options"].insert(
                            1, f"$APPCONFIGOPTS/DaVinci/DataType-{configVersion}.py"
                        )
                        dst_merging_run12["options"].append(
                            "$APPCONFIGOPTS/DaVinci/Simulation.py"
                        )
                    elif configName == "LHCb":
                        theYear = 2000 + int(configVersion.removeprefix("Collision"))
                        dst_merging_run12["options"].insert(
                            1, f"$APPCONFIGOPTS/DaVinci/DataType-{theYear}.py"
                        )
                    merge_step.update(dst_merging_run12)
            else:
                continue
            break

        wf.append_step(merge_step, is_merge_step=True)

    # validate once more to check sanity of the graph.
    wf.validate_graph()

    data = wf.solved_request()
    print(wf.dump_mermaid())

    # look at all APPostProc steps
    min_ok_version = os.environ.get("LBAP_POSTPROC_MINVERSION", "2024-12-12")
    for step in data["steps"]:
        if not step["application"]["name"].startswith("lb-conda/"):
            continue
        if step["application"]["name"] != "lb-conda/default":
            raise ValueError(
                "Invalid lb-conda environment used. Please only use lb-conda/default."
            )

        # Check the version is OK
        ymd = step["application"]["version"].split("_")
        if len(ymd) == 1:
            ver = datetime.strptime(step["application"]["version"], "%Y-%m-%d")
        elif len(ymd) == 2:
            ver = datetime.strptime(step["application"]["version"], "%Y-%m-%d_%H-%M")
        else:
            raise NotImplementedError(f"{step['application']!r}")

        if ver < datetime.strptime(min_ok_version, "%Y-%m-%d"):
            raise ValueError(
                f"Invalid lb-conda/default version {step['application']['version']} used."
                f"Please use a version greater than or equal to {min_ok_version}"
            )

    return [data]


def filename_from_input(input_data, input_spec):
    if "bk_query" in input_data:
        return str(input_data["bk_query"].split("/")[-1])

    if "job_name" in input_data:
        return input_data["filetype"]

    if "transform_ids" in input_data:
        return input_data["filetype"]

    if "tags" in input_data:
        return input_spec["conditions_dict"]["inFileType"]

    raise NotImplementedError(input_data)
