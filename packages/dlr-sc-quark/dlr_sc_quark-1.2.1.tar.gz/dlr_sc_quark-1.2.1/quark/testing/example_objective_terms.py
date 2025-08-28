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

""" module for ExampleObjectiveTerms """

from quark import ObjectiveTerms, PolyBinary


ONE_COLOR_PER_NODE = "one_color_per_node"
COLORED_EDGES      = "colored_edges"
X = "x"


class ExampleObjectiveTerms(ObjectiveTerms):
    """
    An example implementation of an ObjectiveTerms for testing based on the MaxColorableSubgraph problem

    The binary variable x_n_c is 1 if node n is colored with color c and 0 otherwise.
    """

    @staticmethod
    def _get_constraint_terms_names():
        """
        get the names of the objective terms whose value must be zero to have the corresponding constraints fulfilled,
        which need to be a subset of all objective terms names
        """
        return [ONE_COLOR_PER_NODE]

    @staticmethod
    def _get_objective_terms(instance):
        """ get the objective terms from the instance data """
        objective_terms = {COLORED_EDGES: PolyBinary(),
                           ONE_COLOR_PER_NODE : PolyBinary()}

        # actual objective
        # counting the number of wrongly colored edges:
        # sum_[c in Colors] sum_[(n, m) in Edges] (1 * x_n_c * x_m_c)
        for color in instance.colors:
            objective_terms[COLORED_EDGES] += PolyBinary({((X, node1, color), (X, node2, color)): 1
                                                          for node1, node2 in instance.edges})

        # objective terms from the constraints
        # every node should get exactly one color:
        # sum_[n in Nodes] (sum_[c in Colors] x_n_c - 1)^2
        for node in instance.nodes:
            poly = PolyBinary({((X, node, color),): 1 for color in instance.colors}) - 1
            objective_terms[ONE_COLOR_PER_NODE] += poly * poly

        return objective_terms
