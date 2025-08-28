# Copyright 2023 DLR-SC
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

""" module for ExampleObjective """

from quark import Objective, PolyBinary


X = "x"


class ExampleObjective(Objective):
    """ An example implementation of an Objective for testing based on the MaxColorableSubgraph problem """

    @staticmethod
    def _get_polynomial(instance):
        """ get the objective terms from the instance data """
        # actual objective
        # counting the number of wrongly colored edges:
        # sum_[c in Colors] sum_[(n, m) in Edges] (1 * x_n_c * x_m_c)
        poly_colored_edges = PolyBinary()
        for color in instance.colors:
            poly_colored_edges += PolyBinary({((X, node1, color), (X, node2, color)): 1
                                              for node1, node2 in instance.edges})

        # additional penalty term from the constraint
        # every node should get exactly one color:
        # sum_[n in Nodes] (sum_[c in Colors] x_n_c - 1)^2
        poly_one_color_per_node = PolyBinary()
        for node in instance.nodes:
            poly = PolyBinary({((X, node, color),): 1 for color in instance.colors}) - 1
            poly_one_color_per_node += poly * poly
        # apply a default worst case scaling
        poly_one_color_per_node *= len(instance.edges)

        # return the full QUBO
        return poly_colored_edges + poly_one_color_per_node
