###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from itertools import groupby, product
from typing import Literal

from pydantic import BaseModel, Field


def expand_dict(data: dict):
    data = {k: [v] if not isinstance(v, list) else v for k, v in data.items()}
    grouped = [a for a, b in data.items() if isinstance(b, list)]
    p = [
        [a, list(b)]
        for a, b in groupby(product(*[data[i] for i in grouped]), key=lambda x: x[0])
    ]
    return [tuple({**data, **dict(zip(grouped, i))} for i in c) for _, c in p]


class SplittingRecipe(BaseModel):
    name: Literal["split-trees"]

    class SplitHow(BaseModel):
        key: str = Field(
            title="Key pattern.",
            description="Any object inside the ROOT file matching this regular expression would be selected to be saved.",
            examples=["Tuple_SpruceSLB_(Bc).*?/DecayTree"],
        )
        into: str = Field(
            title="File to save matching keys into.",
            description=(
                "The output file type without an extension. Should be lowercase. "
                "For example: 'bc' would save any key names matching the 'key' regular expression into 'BC.ROOT'."
            ),
            pattern="[a-z]+",
            examples=["bc", "rightsign"],
        )

    split: list[SplitHow]

    def configured(self, v):
        return [
            {
                **v,
                "application": "lb-conda/default/2024-12-12",
                "entrypoint": "LbExec:skim_and_merge",
                "extra_options": {
                    "compression": {
                        "optimise_baskets": False,
                    }
                },
                "extra_args": [
                    "--",
                    *[f"--write={split.into}={split.key}" for split in self.split],
                ],
                "output": [f"{split.into.upper()}.ROOT" for split in self.split],
            }
        ]


class FilteringRecipe(BaseModel):
    name: Literal["filter-trees"]
    entrypoint: str = Field(
        title="Entrypoint",
        description="Which filtering entrypoint to run.",
        examples=["MyAnalysis.filter_script:run_preselection"],
    )


class ExpandBKPath(BaseModel):
    """
    A recipe to expand the provided BK path elements into multiple jobs.

    Use format strings in the path to mark where you would like the substitutions to go.

        recipe:
          - name: "expand-bk-path"
            path: "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST"
            substitute:
                polarity: ["MagUp", "MagDown"]
                sprucing: ["24c3", "24c2"]
                stream: "94000000"

    generates 4 jobs for each BK path:

    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing24c3/94000000/CHARM.DST"
    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing24c2/94000000/CHARM.DST"

    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagDown/Real Data/Sprucing24c3/94000000/CHARM.DST"
    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagDown/Real Data/Sprucing24c2/94000000/CHARM.DST"

    """

    name: Literal["expand"]

    path: str = Field(
        title="BK path",
        description="The BK path to expand.",
        examples=[
            "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST"
        ],
    )
    substitute: dict[str, list[str] | str]

    def configure(self, v):
        expanded_dicts = expand_dict(self.substitute)
        return [
            {
                **v,
                "name": f"expanded_{'_'.join(expanded_dict.values())}",
                "input": {
                    **v["input"],
                    "bk_query": self.path.format(expanded_dict),
                },
            }
            for expanded_dict in expanded_dicts
        ]


AllRecipes = SplittingRecipe | FilteringRecipe | ExpandBKPath
