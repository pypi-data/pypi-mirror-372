###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from copy import deepcopy
from textwrap import dedent

import pytest
import yaml
from pydantic import ValidationError

from LbAPCommon.models import parse_yaml, validate_yaml

OPTIONAL_KEYS = [
    "root_in_tes",
    "simulation",
    "luminosity",
    "data_type",
    "input_type",
    "dddb_tag",
    "conddb_tag",
    "comment",
]


def test_good_no_defaults():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: cernuser
        priority: 1a
        completion_percentage: 99.5
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py", "$VAR/a.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 99.5


@pytest.mark.parametrize(
    "input_runs,expected_runs,expected_start_run,expected_end_run",
    [
        (["1234:1238"], None, 1234, 1238),
        (["1234:1238", "1240"], ["1234:1238", "1240"], None, None),
    ],
)
def test_good_runs(input_runs, expected_runs, expected_start_run, expected_end_run):
    runs = "".join([f"\n             - {run}" for run in input_runs])
    rendered_yaml = dedent(
        f"""\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            runs: {runs}
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    if expected_runs is None:
        assert "runs" not in jobs_data["job_1"]["input"]
    else:
        assert jobs_data["job_1"]["input"]["runs"] == expected_runs
    if expected_start_run is None:
        assert "start_run" not in jobs_data["job_1"]["input"]
    else:
        assert jobs_data["job_1"]["input"]["start_run"] == expected_start_run
    if expected_end_run is None:
        assert "end_run" not in jobs_data["job_1"]["input"]
    else:
        assert jobs_data["job_1"]["input"]["end_run"] == expected_end_run


@pytest.mark.parametrize("key", ["start_run", "end_run"])
def test_good_run_limit(key):
    rendered_yaml = dedent(
        f"""\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            {key}: 42
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["input"][key] == 42
    other_key = {"start_run": "end_run", "end_run": "start_run"}[key]
    assert other_key not in jobs_data["job_1"]["input"]


@pytest.mark.parametrize("key", ["start_run", "end_run"])
def test_bad_runs_and_limit(key):
    rendered_yaml = dedent(
        f"""\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            runs:
                - 1234:1238
            {key}: 1237
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    with pytest.raises(
        ValidationError,
        match="Either use `start_run` and `end_run`, or use `runs` - can't use both.",
    ):
        parse_yaml(rendered_yaml)


def test_bad_end_run():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            start_run: 42
            end_run: 41
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    with pytest.raises(ValueError, match="must be less than end run"):
        parse_yaml(rendered_yaml)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("FILETYPE.ROOT", ["FILETYPE.ROOT"]),
        ("filetype.root", ["FILETYPE.ROOT"]),
        ("filetype.ROOT", ["FILETYPE.ROOT"]),
        ("\n        - filetype.ROOT", ["FILETYPE.ROOT"]),
        (
            "\n        - filetype.ROOT\n        - filetype.dst",
            ["FILETYPE.ROOT", "FILETYPE.DST"],
        ),
    ],
)
def test_good_output_filetype_scalar(value, expected):
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: {value}
        options:
            - $VAR/a.py
        wg: Charm
        inform: cernuser
    """.format(
            value=value
        )
    )
    jobs_data = parse_yaml(rendered_yaml)
    validate_yaml(jobs_data, "a", "b")
    assert len(jobs_data) == 1

    assert jobs_data["job_1"]["output"] == expected

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["options"] == {"files": ["$VAR/a.py"]}
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]


def test_good_with_defaults():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        inform:
            - cernuser
        priority: 1a
        completion_percentage: 95.6
        comment: This production will produce tuples of a, b, c decays for the x analysis in the y working group

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser
        priority: 2a
        completion_percentage: 87.35
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 2

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 95.6
    assert (
        jobs_data["job_1"]["comment"]
        == "This production will produce tuples of a, b, c decays for the x analysis in the y working group"
    )

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]
    assert jobs_data["job_2"]["priority"] == "2a"
    assert jobs_data["job_2"]["completion_percentage"] == 87.35
    assert (
        jobs_data["job_2"]["comment"]
        == "This production will produce tuples of a, b, c decays for the x analysis in the y working group"
    )


def test_good_all_turbo():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: yes
        inform:
            - cernuser

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: no
        options:
            - options.py
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is True
    assert jobs_data["job_1"]["inform"] == ["cernuser"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is True
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is False
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    for key in OPTIONAL_KEYS:
        for job in ["job_1", "job_2", "job_3"]:
            assert key not in jobs_data[job]


def test_good_some_turbo():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - cernuser

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    for key in OPTIONAL_KEYS:
        for job in ["job_1", "job_2", "job_3"]:
            assert key not in jobs_data[job]


def test_good_automatically_configure_overrides():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - cernuser

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
        root_in_tes: "/Event/Charm"
        simulation: yes
        luminosity: no
        data_type: "2018"
        input_type: "DST"
        dddb_tag: "xyz-234"
        conddb_tag: "abc-def-20u"
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    for key in OPTIONAL_KEYS:
        assert key not in jobs_data["job_1"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["root_in_tes"] == "/Event/Charm"
    assert jobs_data["job_3"]["simulation"] is True
    assert jobs_data["job_3"]["luminosity"] is False
    assert jobs_data["job_3"]["data_type"] == "2018"
    assert jobs_data["job_3"]["input_type"] == "DST"
    assert jobs_data["job_3"]["dddb_tag"] == "xyz-234"
    assert jobs_data["job_3"]["conddb_tag"] == "abc-def-20u"


def test_good_automatically_configure_defaults_overrides():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - cernuser
        root_in_tes: "/Event/Charm"
        simulation: yes
        luminosity: no
        data_type: "2018"
        input_type: "DST"
        dddb_tag: "xyz-234"
        conddb_tag: "abc-def-20u"

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
        root_in_tes: "/Event/Other"
        simulation: no
        luminosity: yes
        data_type: "2017"
        input_type: "MDST"
        dddb_tag: "tuv-345"
        conddb_tag: "ghj-20z"
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    for job in ["job_1", "job_2"]:
        assert jobs_data[job]["root_in_tes"] == "/Event/Charm"
        assert jobs_data[job]["simulation"] is True
        assert jobs_data[job]["luminosity"] is False
        assert jobs_data[job]["data_type"] == "2018"
        assert jobs_data[job]["input_type"] == "DST"
        assert jobs_data[job]["dddb_tag"] == "xyz-234"
        assert jobs_data[job]["conddb_tag"] == "abc-def-20u"

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["root_in_tes"] == "/Event/Other"
    assert jobs_data["job_3"]["simulation"] is False
    assert jobs_data["job_3"]["luminosity"] is True
    assert jobs_data["job_3"]["data_type"] == "2017"
    assert jobs_data["job_3"]["input_type"] == "MDST"
    assert jobs_data["job_3"]["dddb_tag"] == "tuv-345"
    assert jobs_data["job_3"]["conddb_tag"] == "ghj-20z"


def test_good_gaudipython():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            command:
                - python
            files:
                - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
        completion_percentage: 99.5
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "command": ["python"],
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"],
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 99.5


@pytest.mark.parametrize(
    "missing_key", ["application", "input", "output", "wg", "inform"]
)
def test_bad_missing_key(missing_key):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
            "wg": "Charm",
            "inform": "cernuser",
        }
    }
    del data["job_1"][missing_key]
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises(
        ValidationError,
        match=rf"(\d) validation error for APConfiguration\njob_1.{missing_key}\n\s+Field required \[type=missing(.*?)",
    ):
        parse_yaml(rendered_yaml)


@pytest.mark.parametrize(
    "key,value",
    [
        ("application", "DaVinci"),
        ("input", "hello"),
        ("output", ""),
        ("wg", ""),
        ("inform", ""),
        ("automatically_configure", "null"),
        ("turbo", "absolutely"),
        ("root_in_tes", "DST"),
        ("simulation", "absolutely"),
        ("luminosity", "nope"),
        ("data_type", "MSDT"),
        ("input_type", "2016"),
        ("dddb_tag", ""),
        ("conddb_tag", ""),
        ("priority", "3a"),
    ],
)
def test_bad_invalid_value(key, value):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
            "wg": "Charm",
            "inform": "cernuser",
        }
    }
    data["job_1"][key] = value
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises(
        ValidationError,
        match=rf"(\d) validation error for APConfiguration\njob_1.{key}(.*?)",
    ):
        parse_yaml(rendered_yaml)


@pytest.mark.parametrize(
    "key,value",
    [
        ("completion_percentage", "ninety-nine"),
        ("completion_percentage", 100.1),
        ("completion_percentage", -24.33),
        ("completion_percentage", 9.9),
    ],
)
def test_bad_invalid_completion_percentage(key, value):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
            "wg": "Charm",
            "inform": "cernuser",
        }
    }
    data["job_1"][key] = value
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises(ValueError):
        validate_yaml(*parse_yaml(rendered_yaml), "a", "b")


def test_completion_percentage_not_in_defaults():
    job_template = {
        "application": "DaVinci/v45r3",
        "input": {
            "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        },
        "output": "FILETYPE.ROOT",
        "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
        "wg": "Charm",
        "inform": "cernuser",
    }
    data = {
        "job_1": deepcopy({**job_template, "completion_percentage": 100}),
        "job_2": deepcopy({**job_template}),
        "job_3": deepcopy({**job_template, "completion_percentage": 20}),
    }
    rendered_yaml = yaml.safe_dump(data)
    jobs_data = parse_yaml(rendered_yaml)
    assert jobs_data["job_1"]["completion_percentage"] == 100
    assert jobs_data["job_2"]["completion_percentage"] == 100
    assert jobs_data["job_3"]["completion_percentage"] == 20


def test_completion_percentage_in_defaults():
    job_template = {
        "application": "DaVinci/v45r3",
        "input": {
            "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        },
        "output": "FILETYPE.ROOT",
        "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
        "wg": "Charm",
        "inform": "cernuser",
    }
    data = {
        "defaults": {
            "completion_percentage": 50,
        },
        "job_1": deepcopy({**job_template, "completion_percentage": 100}),
        "job_2": deepcopy({**job_template}),
        "job_3": deepcopy({**job_template, "completion_percentage": 20}),
    }
    rendered_yaml = yaml.safe_dump(data)
    jobs_data = parse_yaml(rendered_yaml)
    assert jobs_data["job_1"]["completion_percentage"] == 100
    assert jobs_data["job_2"]["completion_percentage"] == 50
    assert jobs_data["job_3"]["completion_percentage"] == 20


# def test_filetype_validation():
#     from parsing import _normalise_filetype

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "XICPS_MC_26265072_2016_MAGUP.ROOT")
#     assert "is excessively long" not in str(excinfo.value)
#     assert "event type" in str(excinfo.value)
#     assert "magnet polarity" in str(excinfo.value)
#     assert "data taking year" in str(excinfo.value)

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "XICPS_MC_26265072.ROOT")
#     assert "is excessively long" not in str(excinfo.value)
#     assert "event type" in str(excinfo.value)
#     assert "magnet polarity" not in str(excinfo.value)
#     assert "data taking year" not in str(excinfo.value)

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "XICPS_MC_MagDown.ROOT")
#     assert "is excessively long" not in str(excinfo.value)
#     assert "event type" not in str(excinfo.value)
#     assert "magnet polarity" in str(excinfo.value)
#     assert "data taking year" not in str(excinfo.value)

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "A" * 100)
#     assert "is excessively long" in str(excinfo.value)
#     assert "event type" not in str(excinfo.value)
#     assert "magnet polarity" not in str(excinfo.value)
#     assert "data taking year" not in str(excinfo.value)

#     assert _normalise_filetype("PROD", "JOB", "XICPS_MC.ROOT") == "XICPS_MC.ROOT"
#     assert _normalise_filetype("PROD", "JOB", "xicps_mc.root") == "XICPS_MC.ROOT"
