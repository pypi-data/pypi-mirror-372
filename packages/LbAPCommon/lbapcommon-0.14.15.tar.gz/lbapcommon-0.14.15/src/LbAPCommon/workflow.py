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
from itertools import combinations
from typing import Literal

import networkx as nx
import yaml
from pydantic import BaseModel

INTERMEDIATE_SE = "CERN-BUFFER"
FINAL_OUTPUT_SE = "CERN-ANAPROD"


class TransformationDescription(BaseModel):
    type: str
    steps: list[int]
    output_se: str
    input_plugin: str
    group_size: int
    input_data_policy: Literal["protocol"] | Literal["download"]
    output_mode: Literal["Local"] | Literal["Run"] | Literal["Any"]

    output_file_mask: str = ""
    multicore: bool = True
    events: int = -1
    ancestor_depth: int = 0
    cpu: str = "1000000"
    priority: int = 2
    remove_inputs_flags: bool = False


class WorkflowSolver:
    def __init__(
        self,
        request_data={},
        input_plugin: str = "default",
    ):
        self.request = {
            **request_data,
            "submission_info": {"transforms": []},
            "steps": [],
        }
        self.merge_steps = []
        self.input_plugin = input_plugin
        self.G = nx.MultiDiGraph()

    @property
    def steps(self):
        return self.request["steps"]

    @property
    def node_to_transform(self):
        return {
            step: trf_i
            for trf_i, trf in enumerate(self.request["submission_info"]["transforms"])
            for step in trf["steps"]
        }

    def trf_idx_from_step_idx(self, step_idx):
        for trf_i, trf in enumerate(self.request["submission_info"]["transforms"]):
            for step in trf["steps"]:
                if step == step_idx:
                    return trf_i

    @property
    def transform_subgraph_groups(self):
        return {
            trf_i: [step for step in trf["steps"]]
            for trf_i, trf in enumerate(self.request["submission_info"]["transforms"])
        }

    def load_from_yaml(self, filename):
        with open(filename, "r") as f:
            self.request = yaml.safe_load(f)[0]
        self.request["submission_info"]["transforms"] = []

    def append_step(self, step_data, is_merge_step=False):
        self.request["steps"].append(step_data)

        if is_merge_step:
            self.merge_steps.append(step_data["name"])

    def validate_graph(self, allow_isolated=False):
        self.G = nx.MultiDiGraph()
        self.request["submission_info"] = {"transforms": []}
        self._build_graph()
        try:
            self._verify_graph_sanity(allow_isolated=allow_isolated)
        except Exception as e:
            print(self.dump_mermaid())
            raise e

    def _build_graph(self):
        assert len(self.G.nodes) == 0, "Graph is not empty"

        for i, _ in enumerate(self.request["steps"]):
            self.G.add_node(i)

        node_to_transform = {}

        for step1, step2 in combinations(self.G.nodes, 2):
            for edge_key in self._has_edge(self.steps[step1], self.steps[step2]):
                self.G.add_edge(step1, step2, key=edge_key)

        removable_edges = set()
        for u, v, ft1 in self.G.edges(keys=True):
            # check if any other edge pointing out from node u has the same filetype
            for _, y, ft2 in self.G.out_edges(u, keys=True):
                if y == v:
                    continue
                if ft1 == ft2 and y > v:
                    # node v has precedence over node y ingesting this filetype.
                    removable_edges.add((u, y, ft2))

        self.G.remove_edges_from(removable_edges)
        print(f"Removed edges {removable_edges!r}")

        print(self.dump_mermaid(output_edges=False))
        self.nodes_adj_nodes = {
            node: adj_nodes for node, adj_nodes in self.G.adjacency()
        }

        for j, transform_found in enumerate(self._find_transforms()):
            print(f"Transformation {j}: {transform_found!r}")
            trim_trf = False
            for node in transform_found:
                if node in node_to_transform:
                    print(f"Step already part of Trf. {node_to_transform[node]!r}")
                    if (
                        existing_trf := self.transform_subgraph_groups[
                            node_to_transform[node]
                        ]
                    ) != transform_found:
                        print(f"{existing_trf=} != {transform_found=}")
                        raise ValueError(
                            "A step cannot belong to more than one transform, and this cannot be trimmed as the transforms are different."
                        )
                    else:
                        print("Step trimmed.")
                        trim_trf = True
                    continue
                node_to_transform[node] = j
            if not trim_trf:
                self.request["submission_info"]["transforms"].append(
                    self._make_transform(transform_found)
                )

        # ensure that the input step index is correctly set
        self._update_step_input_indices()

    def _update_step_input_indices(self):
        for step_idx, step in enumerate(self.request["steps"]):
            input_edges = list(self.G.in_edges(step_idx, keys=True))
            step["input"] = [
                {**step_input, "step_idx": input_step_idx}
                for step_input in step["input"]
                for input_step_idx, _, file_type in input_edges
                if file_type == step_input["type"]
            ]

    def _has_edge(self, step1, step2):
        for output in step1["output"]:
            for input in step2["input"]:
                # TODO: How to handle visible flag?
                if input["type"] == output["type"]:
                    yield output["type"]

    def _make_transform(self, found_transform):
        is_output_trf = self.G.out_degree(found_transform[-1]) == 0
        is_merge_trf = (
            len(found_transform) == 1
            and self.steps[found_transform[0]]["name"] in self.merge_steps
        )

        input_plugin = "APProcessingByFileTypeSize" if is_merge_trf else "APProcessing"
        if self.input_plugin == "by-run":
            input_plugin = "ByRunFileTypeSizeWithFlush"

        trf_type = "WGProduction"
        for step_idx in found_transform:
            step = self.steps[step_idx]
            if step["application"]["name"].startswith("lb-conda/"):
                # Assume this is not a Gaudi application
                trf_type = "APPostProc"
                break

        # if the transform contains the first step or any step has an empty input array assume
        # that we should not remove the input.
        input_removable = not any(
            n == 0 or len(self.steps[n]["input"]) == 0 for n in found_transform
        )
        return TransformationDescription(
            type="APMerge" if is_merge_trf else trf_type,
            steps=list(found_transform),
            output_se=FINAL_OUTPUT_SE if is_output_trf else INTERMEDIATE_SE,
            input_data_policy="protocol",
            input_plugin=input_plugin,
            output_mode="Local",
            remove_inputs_flags=input_removable,
            group_size=10 if is_merge_trf else 2,
        ).model_dump()

    def _find_transforms(self):
        transforms: list[list[int]] = []
        visited = set()

        # Helper function to generate paths with a single outgoing edge
        def get_linear_path(start_node):
            path = [start_node]
            current = start_node
            while True:
                successors = list(self.G.successors(current))
                if len(successors) != 1 or current in visited:
                    break
                next_node = successors[0]
                if self.G.out_degree(next_node) != 1:
                    break
                path.append(next_node)
                current = next_node
            return path

        for node in nx.topological_sort(self.G):
            if node in visited:
                continue

            # Check if this node is a "merge" step or has multiple outgoing edges
            if (
                "merge" in self.steps[node]["processing_pass"].lower()
                or self.G.out_degree(node) > 1
            ):
                # Treat this node as its own separate transform
                transforms.append([node])
                visited.add(node)
                continue

            # Otherwise, create a linear path transform
            transform = get_linear_path(node)
            transforms.append(transform)
            visited.update(transform)

        return transforms

    def check_output_leaves(self):
        all_unprocessed_output_filetypes = {}

        for node in self.G.nodes:
            unprocessed_output_filetypes = {
                oft["type"] for oft in self.steps[node]["output"]
            }

            # Collect filetypes ingested by downstream nodes
            for _, _, filetype in self.G.out_edges(node, keys=True):
                if filetype in unprocessed_output_filetypes:
                    unprocessed_output_filetypes.remove(filetype)

            # Store remaining unprocessed filetypes for this node
            all_unprocessed_output_filetypes[node] = list(unprocessed_output_filetypes)

            # Ensure no duplicate filetypes are created in the node's outputs
            assert len(unprocessed_output_filetypes) == len(
                set(unprocessed_output_filetypes)
            ), f"Duplicate output filetypes for step {self.steps[node]['name']}"

        # Check for conflicts: ensure no duplicate unprocessed filetypes across nodes
        problematic = False
        for node_a, filetypes_a in all_unprocessed_output_filetypes.items():
            for node_b, filetypes_b in all_unprocessed_output_filetypes.items():
                if node_a != node_b:
                    conflicts = set(filetypes_a).intersection(filetypes_b)
                    if conflicts:
                        print(
                            f"{conflicts} are produced in both {node_a} and {node_b} but are not later ingested by any node."
                        )
                        problematic = True

        assert (
            not problematic
        ), "Multiple non-unique (node, output file type) pairs were found."

        return all_unprocessed_output_filetypes

    def _verify_graph_sanity(self, allow_isolated=False):
        first_edge_idx = 0
        # assert that the first and last step have no input edge and output edge respectively
        assert len(self.G.in_edges(first_edge_idx)) == 0
        assert len(self.G.out_edges(len(self.steps) - 1)) == 0

        # Verify that there are no isolated nodes
        if not allow_isolated:
            assert not list(
                nx.isolates(self.G)
            ), "There are isolated nodes in the graph"

        # Verify that there are no cycles
        assert not list(nx.simple_cycles(self.G)), "There are cycles in the graph"

        # Verify that there are no self looping edges
        assert not list(
            nx.selfloop_edges(self.G)
        ), "There are self looping edges in the graph"

        assert nx.is_directed_acyclic_graph(self.G), "Graph is not a DAG"

        # check that all of the output filetypes of the leaves are unique
        self.check_output_leaves()

    def dump_mermaid(self, direction="TD", output_edges=True):
        mermaid_graph = f"graph {direction}\n"

        # add input edges to first node
        for filetype in self.steps[0]["input"]:
            step1name = self.steps[0]["name"]
            mermaid_graph += (
                f"    {-1}[(INPUT)] -- {filetype['type']} --> {0}[{step1name}]\n"
            )
        # Add edges from the graph
        for u, v, filetype in self.G.edges(keys=True):
            step1name = self.steps[u]["name"]
            step2name = self.steps[v]["name"]
            mermaid_graph += (
                f"    {u}[{step1name}] -- {filetype} --> {v}[{step2name}]\n"
            )

        # add output edges to last node
        if output_edges:
            for node, ofts in self.check_output_leaves().items():
                for filetype in ofts:
                    step2name = self.steps[node]["name"]
                    mermaid_graph += (
                        f"    {node}[{step2name}] -- {filetype} --> {999}[(OUTPUT)] \n"
                    )

        # Add groupings if provided
        for group_name, nodes in self.transform_subgraph_groups.items():
            mermaid_graph += f"    subgraph Trf.{group_name}\n"
            for node in nodes:
                mermaid_graph += f"        {node}\n"
            mermaid_graph += "    end\n"

        return mermaid_graph

    def solved_request(self):
        return self.request
