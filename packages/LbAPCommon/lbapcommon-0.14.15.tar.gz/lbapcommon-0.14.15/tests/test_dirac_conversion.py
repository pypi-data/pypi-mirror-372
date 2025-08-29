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
from glob import glob
from pathlib import Path

import pytest
import yaml

from LbAPCommon import parse_yaml, render_yaml
from LbAPCommon.__main__ import configure_later_step
from LbAPCommon.dirac_conversion import (
    InvalidAPJob,
    group_in_to_requests,
    step_to_production_request,
)


def test_simple():
    data = {
        "A": {"input": {"bk_query": ...}},
        "B": {"input": {"bk_query": ...}},
        "C": {"input": {"bk_query": ...}},
    }
    assert group_in_to_requests(data) == [["A"], ["B"], ["C"]]


def test_valid():
    data = {
        "A": {"input": {"bk_query": ...}},
        "B": {"input": {"bk_query": ...}},
        "C": {"input": {"bk_query": ...}},
        "D": {"input": {"job_name": "C"}},
        "E": {"input": {"job_name": "D"}},
    }
    assert group_in_to_requests(data) == [["A"], ["B"], ["C", "D", "E"]]


@pytest.mark.parametrize(
    "data",
    [
        {"A": {"input": {"job_name": "A"}}},
        {"A": {"input": {"job_name": "B"}}, "B": {"input": {"job_name": "A"}}},
        {
            "A": {"input": {"job_name": "C"}},
            "B": {"input": {"job_name": "A"}},
            "C": {"input": {"job_name": "B"}},
        },
        {
            "A": {"input": {"job_name": "B"}},
            "B": {"input": {"job_name": "A"}},
            "C": {"input": {"job_name": "B"}},
        },
    ],
)
def test_cycle(data):
    with pytest.raises(InvalidAPJob, match="Graph contains a cycle"):
        group_in_to_requests(data)


def test_multiple_children():
    data = {
        "A": {"input": {"bk_query": ...}},
        "B": {"input": {"job_name": "A"}},
        "C": {"input": {"job_name": "B"}},
        "C2": {"input": {"job_name": "B"}},
    }
    # this no longer raises
    group_in_to_requests(data)


# @pytest.mark.parametrize(
#     "info_yaml,expected_exception",
#     [
#         ("complex_workflow_with_filtering", None),
#         ("complex_workflow_with_filtering_two_groups", None),
#     ],
# )
@pytest.mark.parametrize(
    "in_path", glob(str(Path(__file__).parent / "example_workflows/") + "/*.in.yaml")
)
def test_workflows(in_path: Path):
    in_path = Path(in_path)
    expected = []
    expected_out_path = in_path.with_suffix(".yaml").with_name(
        f"{in_path.name.removesuffix('.in.yaml')}.out.yaml"
    )
    if expected_out_path.exists():
        with open(expected_out_path, "r") as f:
            expected = yaml.safe_load(f)

    production_name = "example_workflows"

    rendered = render_yaml(in_path.read_text())

    jobs_data = parse_yaml(rendered, production_name, None)

    for job_name in jobs_data.keys():
        if isinstance(jobs_data[job_name]["output"], str):
            jobs_data[job_name]["output"] = [jobs_data[job_name]["output"]]

    # Apply auto-configuration to the jobs that depend on other jobs
    for job_names in group_in_to_requests(jobs_data):
        for job_name in job_names[1:]:

            configure_later_step(production_name, jobs_data, job_name, {})

    print(jobs_data)

    full_request_yaml = []

    for job_names in group_in_to_requests(jobs_data):
        input_spec = {
            "conditions_description": "Beam6800GeV-VeloClosed-MagUp",
            "conditions_dict": {},
            "event_type": "94000000",
        }
        request = step_to_production_request(
            production_name, jobs_data, job_names, input_spec, "v999999999999"
        )
        print(yaml.dump(request))

        full_request_yaml += request

    expected_out_path.with_suffix(".test_result.yaml").write_text(
        yaml.dump(full_request_yaml)
    )

    assert expected == full_request_yaml
