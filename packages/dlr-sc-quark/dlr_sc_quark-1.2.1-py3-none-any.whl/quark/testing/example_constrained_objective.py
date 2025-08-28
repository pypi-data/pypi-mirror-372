# Copyright 2020 DLR-SC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" module for ExampleConstraintObjective """

from quark import ConstrainedObjective, ConstraintBinary, PolyBinary


X = "x"
ONE_COLOR_PER_NODE = "one_color_per_node"
COLORED_EDGES      = "colored_edges"


class ExampleConstrainedObjective(ConstrainedObjective):
    """
    An example implementation of a ConstraintObjective for testing based on the MaxColorableSubgraph problem

    The binary variable x_n_c is 1 if node n is colored with color c and 0 otherwise.
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        # counting the number of wrongly colored edges:
        # sum_[c in Colors] sum_[(n, m) in Edges] (1 * x_n_c * x_m_c)
        return PolyBinary({((X, node1, color), (X, node2, color)): 1 for node1, node2 in instance.edges
                                                                     for color in instance.colors})

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        constraints = {}

        # every node should get exactly one color:
        # for all n in Nodes: sum_[c in Colors] x_n_c == 1
        for node in instance.nodes:
            poly = PolyBinary({((X, node, color),): 1 for color in instance.colors})
            constraints[ONE_COLOR_PER_NODE + f"_{node}"] = ConstraintBinary(poly, 1, 1)

        return constraints

    def get_objective_terms(self, objective_name=COLORED_EDGES, combine_prefixes=(ONE_COLOR_PER_NODE,), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """
        get an ObjectiveTerms object with the objective as one term
        and automatically generated penalty terms for each constraint

        this overwrites the inherited method to set specific default values
        """
        return super().get_objective_terms(objective_name=objective_name, combine_prefixes=combine_prefixes, name=name,
                                           reduction_strategy=reduction_strategy,
                                           check_special_constraints=check_special_constraints)

    @staticmethod
    def get_original_problem_solution(raw_solution, precision=1e-9):
        """
        extract the actual solution from the variable assignment

        :param (Solution or dict) raw_solution: the binary assignment of the variables according to the above encoding
        :param (float) precision: precision value for rounding issues
        :return: the actual mapping of interest from nodes to colors
        """
        return {node : color for (_, node, color), value in raw_solution.items() if abs(value - 1) < precision}
