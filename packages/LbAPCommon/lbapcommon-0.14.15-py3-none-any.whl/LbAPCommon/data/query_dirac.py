#!/usr/bin/env python
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
import json
import re
from hashlib import md5
from pathlib import Path

import DIRAC


class AutoConfError(Exception):
    """An error occurred while generating the auto-configuration."""

    def __init__(self, message):
        """Initialise the error with a message.

        The message is intended to be a human-readable description of the problem.
        """
        self.message = message


def from_bk_query(bk_query, is_turbo, override_filetype=None):
    """Get the metadata from the bookkeeping query string for configuration applications."""
    from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery

    print("Getting info from bookkeeping", bk_query)
    result = {"input_type": parse_input_type(override_filetype or bk_query, is_turbo)}

    config_name, config_version = bk_query.split("/")[1:3]
    if config_name in {"LHCb", "validation"}:
        result["simulation"] = False

        match = re.match(r"[^0-9]+(\d\d)(?:[^\d].*)?", config_version)
        if not match:
            raise ValueError(f"Failed to parse config version ({config_version})")
        year = int(match.groups()[0])
        result["data_type"] = str(year if year > 2000 else year + 2000)
    elif config_name == "MC":
        result["simulation"] = True
        result["data_type"] = config_version
    else:
        raise NotImplementedError(f"Failed to parse config name ({bk_query})")

    if config_version not in ["Upgrade", "Dev"] and not (
        2011 <= int(result["data_type"]) <= 2025
    ):
        raise ValueError(f"Failed to parse config version ({config_version})")

    if result["simulation"]:
        from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import (
            BookkeepingClient,
        )
        from LHCbDIRAC.TransformationSystem.Client.TransformationClient import (
            TransformationClient,
        )

        dddb_tags = set()
        conddb_tags = set()
        for prodID in BKQuery(bk_query).getBKProductions():
            while isinstance(prodID, int):
                res = BookkeepingClient().getSteps(prodID)
                if not res["OK"]:
                    if "The production is Cleaned/Deleted" in res["Message"]:
                        break
                    raise RuntimeError(res)
                for _, _, _, _, dddb, conddb, _, _, _ in res["Value"]:
                    if dddb:
                        dddb_tags.add(dddb)
                    if conddb:
                        conddb_tags.add(conddb)
                # In some cases we have to inspect parent transformations to find tags
                parent = (
                    TransformationClient()
                    .getBookkeepingQuery(prodID)
                    .get("Value", {})
                    .get("ProductionID", "")
                )
                if parent:
                    print(f"Found parent production ID {parent} for {prodID}")
                prodID = parent

        if len(dddb_tags) != 1 or len(conddb_tags) != 1:
            message = (
                f"Error obtaining database tags for: {bk_query}\n"
                f"  * dddb_tags={dddb_tags!r}\n"
                f"  * conddb_tags={conddb_tags!r}\n"
                "This probably means your bookkeeping path is incorrect. If this "
                "isn't the case, Please open a bug report at https://gitlab.cern.ch/"
                "lhcb-dpa/analysis-productions/LbAnalysisProductions/-/issues"
            )
            raise NotImplementedError(message)
        assert len(dddb_tags) == 1, dddb_tags
        assert len(conddb_tags) == 1, conddb_tags
        assert dddb_tags != {None}, "Simulated database tags should never be None"
        assert conddb_tags != {None}, "Simulated database tags should never be None"

        result["dddb_tag"] = dddb_tags.pop()
        result["conddb_tag"] = conddb_tags.pop()

    return result


def parse_input_type(file_path, is_turbo):
    """Get the input type from the file path."""
    extension = file_path.split("/")[-1].split(".")[-1]
    if extension in {"DST", "LDST", "MDST", "XDST"}:
        # Turbo jobs always require MDST
        # https://twiki.cern.ch/twiki/bin/view/LHCb/MakeNTupleFromTurbo
        result = "MDST" if is_turbo else extension
    else:
        raise AutoConfError(f"Failed to parse {file_path!r} to get input type")
    print(f"Set input type of {result} for {file_path}")
    return result


def find_bk_query_from_tid(transform_ids, filetype):
    """Get the bookkeeping query from the transform IDs."""
    from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk_query = None
    for transform_id in transform_ids:
        result = returnValueOrRaise(
            BookkeepingClient().getOutputPathsForProdID(transform_id)
        )
        matches = [line for line in result if line.endswith(filetype)]
        if len(matches) != 1:
            raise NotImplementedError(transform_id, matches)
        if bk_query and bk_query != matches[0]:
            raise NotImplementedError(transform_ids, bk_query, matches[0])
        bk_query = matches[0]
    return bk_query


def find_bk_query_from_sample(input_query):
    from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from LHCbDIRAC.ProductionManagementSystem.Client.AnalysisProductionsClient import (
        AnalysisProductionsClient,
    )

    apc = AnalysisProductionsClient()
    # query APC getProductions for samples and request IDs.
    samples = returnValueOrRaise(
        apc.getProductions(
            wg=input_query["wg"],
            analysis=input_query["analysis"],
            with_lfns=False,
            with_pfns=False,
            with_transformations=True,
            at_time=input_query["at_time"],
        )
    )

    input_query_tags = input_query["tags"]
    print(f"Sample query: {json.dumps(input_query, indent=2)}")
    print(
        f"{len(samples)} samples in analysis {input_query['wg']}/{input_query['analysis']}"
    )

    selected_sample = None
    # Check if name and version tags provide an unambiguous match.
    samples = list(
        filter(
            lambda x: all(
                x.get(tag) == input_query_tags[tag]
                for tag in ["name", "version"]
                if tag in input_query_tags
            ),
            samples,
        )
    )
    if len(samples) == 1:
        selected_sample = samples[0]
    elif len(samples) > 1:
        print(
            f"Ambiguous sample query when considering name and version tags only... {len(samples)} remain ... consider other tags..."
        )

        # query APC getTags for this analysis and match a sample.
        # Retrieve sample request ID and filetype.
        samples_tags = returnValueOrRaise(
            apc.getTags(
                wg=input_query["wg"],
                analysis=input_query["analysis"],
                at_time=input_query["at_time"],
            )
        )
        samples = list(
            filter(
                lambda x: all(
                    [
                        input_query_tags.get(tag) == value
                        for tag, value in samples_tags[str(x["sample_id"])].items()
                    ]
                ),
                samples,
            )
        )

        if len(samples) == 1:
            selected_sample = samples[0]
        elif len(samples) > 1:
            for sample in samples:
                print(f"{sample['sample_id']=}")
                print(f"{sample['wg']=}")
                print(f"{sample['analysis']=}")
                print(f"{sample['name']=}")
                print(f"{sample['version']=}")
                print(f"Tags: {samples_tags[str(sample['sample_id'])]}")
                print("--")
            raise ValueError(
                f"Ambiguous sample query that returned {len(samples)} samples. Please narrow down the query by using more tags!"
            )
        else:
            raise ValueError("No samples found matching the query.")
    else:
        raise ValueError("No samples found matching the query.")

    sample_trf_id = selected_sample["transformations"][-1]["id"]
    filetype = selected_sample["filetype"]

    assert (
        filetype.upper()
        == selected_sample["transformations"][-1]["input_query"]["FileType"]
    ), "Could not match filetype to last transformation of sample."

    print(f"Matched sample: {json.dumps(selected_sample, indent=2, default=str)}")

    bk_query = None
    result = returnValueOrRaise(
        BookkeepingClient().getOutputPathsForProdID(sample_trf_id)
    )
    matches = [line for line in result if line.endswith(filetype)]
    if len(matches) != 1:
        raise NotImplementedError(
            "No output paths found for sample_trf_id and filetype",
            sample_trf_id,
            filetype,
        )
    if bk_query and bk_query != matches[0]:
        raise NotImplementedError(sample_trf_id, filetype)
    bk_query = matches[0]
    return bk_query, sample_trf_id, filetype


def format_bkquery_runs(input_data):
    """Format the runs from the input data to a list of strings."""
    runs = input_data.get("runs", None)
    if runs:
        return [str(r) for r in runs]
    return None


def make_sample_max_hash(fraction):
    upper_limit = (2**128) - 1
    width = int(upper_limit * fraction)
    return f"{width:032x}".upper()


def main(input_query, turbo):
    """Extract the information from LHCbDIRAC from the Analysis Productions input query."""
    from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery

    COMMON_KEYS = {
        "dq_flags",
        "smog2_state",
        "extended_dq_ok",
        "runs",
        "start_run",
        "end_run",
        "keep_running",
        "input_plugin",
        "n_test_lfns",
        "sample_fraction",
        "sample_seed",
    }

    bk_query = BKQuery()
    if "bk_query" in input_query:
        assert set(input_query).issubset(COMMON_KEYS | {"bk_query"})
        bk_query_string = input_query["bk_query"]
        bk_query.buildBKQuery(
            bk_query_string,
            prods="ALL",
            runs=format_bkquery_runs(input_query),
            visible=True,
        )
    elif "transform_ids" in input_query:
        assert set(input_query).issubset(COMMON_KEYS | {"filetype", "transform_ids"})
        bk_query_string = find_bk_query_from_tid(
            input_query["transform_ids"], input_query["filetype"]
        )
        bk_query.buildBKQuery(
            bk_query_string,
            prods=input_query["transform_ids"],
            fileTypes=[input_query["filetype"]],
            runs=format_bkquery_runs(input_query),
            visible=True,
        )
    elif "tags" in input_query:
        assert set(input_query).issubset(
            COMMON_KEYS | {"tags", "wg", "analysis", "at_time"}
        )
        bk_query_string, sample_trf_id, sample_filetype = find_bk_query_from_sample(
            input_query
        )
        bk_query.buildBKQuery(
            bk_query_string,
            fileTypes=[sample_filetype],
            prods=[sample_trf_id],
            visible=True,
        )
    else:
        raise NotImplementedError("Unrecogised input query", input_query)

    # sampling
    sample_frac = input_query.get("sample_fraction", None)
    sample_seed = input_query.get("sample_seed", None)

    if sample_frac:
        bk_query.setOption("SampleMax", make_sample_max_hash(sample_frac))
    if sample_seed:
        bk_query.setOption(
            "SampleSeedMD5", md5(sample_seed.encode("utf-8")).hexdigest().upper()
        )

    # Finish getting information from the input query
    bk_query.setDQFlag(input_query.get("dq_flags", ["OK"]))
    smog2_state = input_query.get("smog2_state")
    if smog2_state:
        bk_query.setOption("SMOG2", smog2_state)
    extended_dq_ok = input_query.get("extended_dq_ok")
    if extended_dq_ok:
        bk_query.setOption("ExtendedDQOK", extended_dq_ok)
    bk_query_dict = bk_query.getQueryDict()

    print(f"BKQuery dictionary: {bk_query_dict!r}")

    # Get information about the bookkeeping query
    auto_conf_data = None
    auto_conf_error = None
    try:
        auto_conf_data = from_bk_query(bk_query_string, turbo)
    except AutoConfError as e:
        auto_conf_error = e.message
    else:
        auto_conf_data["luminosity"] = not auto_conf_data["simulation"]
        if auto_conf_data["simulation"] and (
            auto_conf_data["dddb_tag"] is None or auto_conf_data["conddb_tag"] is None
        ):
            raise AutoConfError("Database tags are required for simulation")
        # TODO: Set this automatically
        auto_conf_data["root_in_tes"] = None

    input_info = bk_query.getNumberOfLFNs()
    return {
        "auto-conf-data": auto_conf_data,
        "auto-conf-error": auto_conf_error,
        "input-spec": {
            "conditions_dict": make_conditions_dict(bk_query_dict),
            "conditions_description": bk_query_dict["ConditionDescription"],
            "event_type": bk_query_dict["EventType"],
            "num-lfns": input_info["NumberOfLFNs"],
            "size": input_info["LFNSize"],
            "run-numbers": input_query.get("runs", None),
            "start-run": input_query.get("start_run", None),
            "end-run": input_query.get("end_run", None),
            "input_plugin": input_query.get("input_plugin", None),
            "keep_running": input_query.get("keep_running", None),
            "n_test_lfns": input_query.get("n_test_lfns", 1),
            "sample_frac": input_query.get("sample_fraction", None),
            "sample_seed": input_query.get("sample_seed", None),
        },
    }


def make_conditions_dict(query_dict):
    """Dictionary of conditions, suitable for use as Production input."""
    data_quality = query_dict["DataQuality"]
    if not isinstance(data_quality, str):
        data_quality = ",".join(data_quality)
    result = {
        "configName": query_dict["ConfigName"],
        "configVersion": query_dict["ConfigVersion"],
        "inFileType": query_dict["FileType"],
        "inProPass": query_dict["ProcessingPass"][1:],
        "inDataQualityFlag": data_quality,
        "inTCKs": "ALL",
    }

    if "Production" not in query_dict:
        result["inProductionID"] = "ALL"
    elif isinstance(query_dict["Production"], (str, int)):
        result["inProductionID"] = str(query_dict["Production"])
    else:
        result["inProductionID"] = ",".join(map(str, query_dict["Production"]))

    result = {k: str(v) for k, v in result.items()}

    if "SMOG2" in query_dict:
        result["inSMOG2State"] = query_dict["SMOG2"]

    if "ExtendedDQOK" in query_dict:
        result["inExtendedDQOK"] = query_dict["ExtendedDQOK"]

    return result


def parse_args():
    """Parse the command line arguments and then call main."""
    parser = argparse.ArgumentParser(description="Get info from bookkeeping")
    parser.add_argument(
        "input_query", type=json.loads, help="The input query to get info from"
    )
    parser.add_argument(
        "--turbo", action="store_true", help="The job runs over turbo data"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="The output file to write to"
    )

    parser.add_argument("--server-credentials", nargs=2)
    parser.add_argument("--debug")

    args = parser.parse_args()

    DIRAC.initialize(
        log_level="DEBUG" if args.debug else None,
        host_credentials=args.server_credentials,
    )
    result = main(
        args.input_query,
        args.turbo,
    )
    args.output.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    parse_args()
