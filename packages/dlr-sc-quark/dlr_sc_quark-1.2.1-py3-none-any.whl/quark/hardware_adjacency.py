# Copyright 2022 DLR-SC
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

""" module for HardwareAdjacency """

from functools import cached_property
import networkx as nx


NODE_DATA = "node_data"
EDGE_DATA = "edge_data"


class HardwareAdjacency(list):
    """
    A hardware adjacency is a list of edges, pairs of nodes, which implicitly defines the hardware graph.
    """

    def __init__(self, edges, name=None):
        """
        initialize HardwareAdjacency object

        :param (set or list) edges: set of tuples representing edges in the hardware graph
        :param (str or None) name: identifying name to differ between several hardware adjacencies
        """
        self.name = name
        super().__init__(_sort_edges(edges))

    def __eq__(self, other):
        # we also allow for the comparison with plain lists where the name is irrelevant
        if isinstance(other, list) and super().__eq__(_sort_edges(other)):
            if isinstance(other, HardwareAdjacency):
                return self.name == other.name
            return True
        return False

    def __ne__(self, other):
        # needs to be implemented otherwise would just use list comparison
        return not self.__eq__(other)

    def __repr__(self):
        """ get nice string representation """
        return self.__class__.__name__ + f"({super().__repr__()}, {repr(self.name)})"

    def __str__(self):
        """ get nice human-readable string representation of the objective """
        return str(list(self))

    @cached_property
    def nodes(self):
        """ nodes of the hardware graph """
        return sorted(set(node for edge in self for node in edge))

    @cached_property
    def graph(self):
        """ the corresponding networkx graph """
        graph = nx.Graph()
        graph.add_nodes_from(self.nodes)
        graph.add_edges_from(self)
        return graph

    def are_neighbored(self, node1, node2):
        """
        check whether two nodes are connected by an edge

        :param node1: first node in hardware graph
        :param node2: second node in hardware graph
        :return: True if the nodes are neighbored
        """
        return tuple(sorted((node1, node2))) in self

    def update_graph(self, node_data=None, edge_data=None):
        """
        update the graph's nodes or edges with the given data

        :param (dict or None) node_data: dictionary with additional information for the nodes,
                                         should have format {info_names: single_value_for_all_nodes or {nodes: values}}
        :param (dict or None) edge_data: dictionary with additional information for the edges,
                                         should have format {info_names: single_value_for_all_edges or {edges: values}}
        """
        if node_data:
            nx.set_node_attributes(self.graph, _revert_data(self.graph.nodes, node_data))
            self.graph.graph[NODE_DATA] = self.graph.graph.get(NODE_DATA, set()).union(node_data.keys())
        if edge_data:
            nx.set_edge_attributes(self.graph, _revert_data(self.graph.edges, edge_data))
            self.graph.graph[EDGE_DATA] = self.graph.graph.get(EDGE_DATA, set()).union(edge_data.keys())


def _sort_edges(edges):
    """ sort the elements in the tuples and afterwards the tuples """
    return sorted(set(tuple(sorted(edge)) for edge in edges))

def _revert_data(elements, data):
    """ extract the data for each element """
    return {e: {name: d if not isinstance(d, dict) else d[e] for name, d in data.items()} for e in elements}
