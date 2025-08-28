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

""" module for Embedding """

from math import prod
from functools import cached_property
from itertools import combinations, product
import networkx as nx

from .hardware_adjacency import HardwareAdjacency


COMPLETE = "complete"
ARE_NEIGHBORED = "are_neighbored"

ERROR_MAPPINGS  = "Either provide mapping from variables to nodes or to edges"
ERROR_DIFFERENT = "The var_edges_map cannot contain different variables than var_nodes_map"
ERROR_CONNECTED = "Cannot check connectivity without mapping from variables to edges " \
                  "either embedding should have var_edges_map or an hwa should be provided"
ERROR_VALID     = "Cannot judge validity without mapping from couplings to edges"
ERROR_NODES     = "Each variable should map to at least one node"


class Embedding:
    """
    An embedding is a mapping from variables and couplings of the original problem to the nodes and edges of a hardware
    graph, defining the embedding subgraphs.
    """

    def __init__(self, var_nodes_map=None, coupling_edges_map=None, var_edges_map=None, name=None, index=None):
        """
        initialize Embedding object,
        need at least either var_nodes_map or var_edges_map

        :param (dict or list[list] or None) var_nodes_map: mapping of variables to nodes in the hardware graph,
                                                           if not given, it is extracted from var_edges_map
        :param (dict or None) coupling_edges_map: mapping of couplings to edges in the hardware graph
        :param (dict or list[list] or None) var_edges_map: mapping of variables to edges in the hardware graph
        :param (str or None) name: identifying name to differ between several embeddings
        :param (int or None) index: identifying index to differ between several embeddings with the same name
        """
        if not var_nodes_map and not var_edges_map:
            raise ValueError(ERROR_MAPPINGS)
        if var_edges_map and not var_nodes_map:
            var_nodes_map = {var : sorted(set(node for edge in edges for node in edge))
                             for var, edges in var_edges_map.items()}

        self.name = name
        self.index = index
        self.var_nodes_map = var_nodes_map if isinstance(var_nodes_map, dict) else dict(enumerate(var_nodes_map))
        self.var_edges_map = var_edges_map if isinstance(var_edges_map, dict) else dict(enumerate(var_edges_map or []))
        self.coupling_edges_map = {tuple(sorted(coupling)): edges
                                   for coupling, edges in (coupling_edges_map or {}).items()}
        self.check_consistency()

    def __eq__(self, other):
        if isinstance(other, Embedding):
            return self.var_nodes_map == other.var_nodes_map \
                   and self.var_edges_map == other.var_edges_map \
                   and self.coupling_edges_map == other.coupling_edges_map \
                   and self.name == other.name \
                   and self.index == other.index
        return False

    def __repr__(self):
        """ get nice string representation """
        return self.__class__.__name__ + f"({repr(self.var_nodes_map)}, {repr(self.name)}, {self.index})"

    def __str__(self):
        """ get nice human-readable string representation of the objective """
        return "\n".join(f"{var} \t-> {nodes}" for var, nodes in self.var_nodes_map.items())

    def check_consistency(self):
        """ check if the data is consistent """
        if self.var_edges_map and set(self.var_edges_map.keys()) != set(self.var_nodes_map.keys()):
            raise ValueError(ERROR_DIFFERENT)
        if any(not nodes for nodes in self.var_nodes_map.values()):
            raise ValueError(ERROR_NODES)

    @cached_property
    def nodes(self):
        """ all nodes used in the embedding """
        return sorted(set(node for nodes in self.var_nodes_map.values() for node in nodes))

    @cached_property
    def edges(self):
        """ all edges used in the embedding """
        edges = set()
        if self.var_edges_map:
            edges.update(edge for edges in self.var_edges_map.values() for edge in edges)
        if self.coupling_edges_map:
            edges.update(edge for edges in self.coupling_edges_map.values() for edge in edges)
        return sorted(edges)

    @cached_property
    def max_map_size(self):
        """ the maximum size (number of nodes) of the embedding subgraph of some variable """
        return max((len(nodes) for nodes in self.var_nodes_map.values()), default=0)

    @classmethod
    def get_from_hwa(cls, var_nodes_map, hwa, name=None, index=None):
        """
        initialize embedding with information calculated from the hardware graph

        :param (dict or list[list]) var_nodes_map: mapping of variables to nodes in the hardware graph
        :param (list[tuples]) hwa: hardware adjacency defining the hardware graph to which the embedding should fit
        :param (str or None) name: identifying name to differ between several embeddings,
                                   by default the name of the HWA
        :param (int or None) index: identifying index to differ between several embeddings with the same name
        :return: the embedding compatible to the hwa
        """
        var_nodes_map = var_nodes_map if isinstance(var_nodes_map, dict) else dict(enumerate(var_nodes_map))
        var_edges_map = get_var_edges_map(var_nodes_map, hwa)
        coupling_edges_map = get_coupling_edges_map(var_nodes_map, hwa)
        name = name or (hwa.name if isinstance(hwa, HardwareAdjacency) else None)
        return cls(var_nodes_map, coupling_edges_map, var_edges_map, name=name, index=index)

    def is_valid(self, couplings=None, hwa=None):
        """
        check if the embedding is valid in general
        and, if given, also checks if there is at least one edge in the hardware graph for each coupling

        :param (set[tuples] or list[tuples] or str or None) couplings: list of couplings of the original problem
        :param (list[tuples] or HardwareAdjacency) hwa: hardware adjacency defining the hardware graph
        :return: True if the embedding is valid
        """
        return self.are_all_node_sets_disjoint() \
               and self.are_all_subgraphs_connected(hwa) \
               and self.are_all_edges_valid() \
               and (couplings is None or self.are_all_couplings_mapped(couplings, hwa))

    def are_all_node_sets_disjoint(self):
        """
        check if the node sets do have nodes in common

        :return: True if all node sets are disjoint
        """
        for set1, set2 in combinations(self.var_nodes_map.values(), 2):
            if not set(set1).isdisjoint(set2):
                return False
        return True

    def are_all_subgraphs_connected(self, hwa=None):
        """
        check if all embeddings form a connected subgraph

        :param (list[tuples] or HardwareAdjacency) hwa: hardware adjacency defining the hardware graph
        :return: True if all embedding subgraphs are connected
        """
        if not self.var_edges_map and not hwa:
            raise ValueError(ERROR_CONNECTED)
        var_edges_map = self.var_edges_map or get_var_edges_map(self.var_nodes_map, hwa)

        for variable, edges in var_edges_map.items():
            assert self.var_nodes_map[variable], "there should not be empty nodes maps"
            # in turn, embeddings consisting of a single node, do not have edges, but are validly 'connected'
            if len(self.var_nodes_map[variable]) > 1:
                subgraph = nx.Graph()
                subgraph.add_edges_from(edges)
                if not subgraph or not nx.algorithms.is_connected(subgraph):
                    return False
        return True

    def are_all_edges_valid(self):
        """
        check if all edges for a coupling indeed connect the nodes sets of the corresponding variables

        :return: True if all edges connect the node sets
        """
        for coupling, edges in self.coupling_edges_map.items():
            for edge in edges:
                if not (edge[0] in self.var_nodes_map[coupling[0]] and edge[1] in self.var_nodes_map[coupling[1]]) and \
                        not (edge[1] in self.var_nodes_map[coupling[0]] and edge[0] in self.var_nodes_map[coupling[1]]):
                    return False
        return True

    def are_all_couplings_mapped(self, couplings, hwa=None):
        """
        check if there is at least one edge in the hardware graph for each coupling

        :param (set[tuples] or list[tuples] or str) couplings: set of couplings of the original problem
        :param (list[tuples] or HardwareAdjacency) hwa: hardware adjacency defining the hardware graph
        :return: True if all couplings do have a counterpart in the hardware
        """
        if not self.coupling_edges_map and not hwa:
            raise ValueError(ERROR_VALID)
        coupling_edges_map = self.coupling_edges_map or get_coupling_edges_map(self.var_nodes_map, hwa)

        if couplings == COMPLETE:
            couplings = combinations(self.var_nodes_map.keys(), 2)

        return all(coupling_edges_map.get(tuple(sorted(coupling)), []) for coupling in couplings)

    def get_vars_with_broken_embedding(self, node_assignments):
        """
        get those variables whose mapped nodes are not synchronized

        :param (dict) node_assignments: mapping of nodes to values
        :return: the list of variables
        """
        var_scores = self.get_var_value_scores(node_assignments)
        return [var for var, score in var_scores if len(score) > 1]

    def de_embed(self, node_assignments, single_var_threshold=None, total_threshold=None, return_score=False):
        """
        get the best assignments of the original variables from the node assignments
        based on majority vote if there are broken node sets and the thresholds are unset,
        otherwise all possible configurations are returned,
        in the order of their score until the threshold is reached,
        both thresholds can be combined, where the strongest in each case will apply

        :param (dict) node_assignments: mapping of nodes to values
        :param (float or None) single_var_threshold: the threshold which the score of a single variable assignment
                                                     should exceed, by default None, i.e. no restriction on the single
                                                     variable scores is used, if set, will return all assignments up to
                                                     this threshold, a value of 1 means no broken embeddings are
                                                     accepted, while 0 means all
        :param (float or None) total_threshold: the threshold which the total score of the variable assignments should
                                                exceed, by default None, i.e. no restriction on the total score is used,
                                                if used, will return all assignments up to this threshold, a value of 1
                                                means no broken embeddings are accepted, while 0 means all
        :param (bool) return_score: if True, also get the score(s) of the corresponding variable assignments
        :return: the best de-embedded variable assignment for the original variables if no thresholds are used,
                 otherwise all variable assignments up to the threshold(s)
        """
        var_scores = self.get_var_value_scores(node_assignments)
        best_score = prod(value_scores[0][1] for _, value_scores in var_scores)
        best_assignment = {var : value_scores[0][0] for var, value_scores in var_scores}
        if single_var_threshold is None and total_threshold is None:
            return (best_assignment, best_score) if return_score else best_assignment

        worst_in_best_score = var_scores[-1][1][0][1]  # last variable with worst score in best assignment
        single_var_threshold = single_var_threshold or 0
        total_threshold = total_threshold or 0
        if worst_in_best_score < single_var_threshold or best_score < total_threshold:
            return ([], best_score) if return_score else []

        assignments_scores = get_assignments_scores(var_scores, single_var_threshold, total_threshold)
        if return_score:
            return assignments_scores
        return [assignment for assignment, _ in assignments_scores]

    def get_var_value_scores(self, node_assignments):
        """
        extract the possible assignments for each original variable individually
        and the corresponding score of this assignment

        :param (dict) node_assignments: mapping of nodes to values
        :return: the dictionary of original variables to dictionaries with assignments to vote
        """
        var_assignments =  {var : [node_assignments[node] for node in nodes if node in node_assignments]
                            for var, nodes in self.var_nodes_map.items()}
        scores = {var : {value : values.count(value) / len(values) for value in set(values)}
                  for var, values in var_assignments.items()}
        scores = {var : sorted(values.items(), key=lambda x: x[1], reverse=True)
                  for var, values in scores.items() if values}
        scores = sorted(scores.items(), key=lambda x: x[1][0][1], reverse=True)
        return scores


def get_var_edges_map(var_nodes_map, hwa):
    """
    get the edges in the embedding subgraph for each variable

    :param (dict or list[list]) var_nodes_map: mapping of variables to nodes in the hardware graph
    :param (list[tuples]) hwa: hardware adjacency defining the hardware graph
    :return: the mapping of variables to edges in the hardware graph
    """
    return {var: get_edges_among(nodes, hwa) for var, nodes in var_nodes_map.items()}

def get_edges_among(nodes, hwa):
    """
    get the edges in the embedding subgraph defined by the given nodes

    :param (set or list) nodes: set of nodes in the hardware graph
    :param (list[tuples] or HardwareAdjacency) hwa: hardware adjacency defining the hardware graph
    :return: the corresponding edges in the hardware graph
    """
    are_neighbored = _get_are_neighbored_func(hwa)
    return sorted(tuple(sorted((n1, n2))) for n1, n2 in combinations(nodes, 2) if are_neighbored(n1, n2))

def get_coupling_edges_map(var_nodes_map, hwa):
    """
    get the edges connecting the embedding subgraphs of each variable pair

    :param (dict or list[list]) var_nodes_map: mapping of variables to nodes in the hardware graph
    :param (list[tuples] or HardwareAdjacency) hwa: hardware adjacency defining the hardware graph
    :return: the mapping of couplings to edges in the hardware graph
    """
    return {tuple(sorted((n1, n2))): get_edges_between(var_nodes_map[n1], var_nodes_map[n2], hwa) for
            n1, n2 in combinations(var_nodes_map.keys(), 2)}

def get_edges_between(nodes1, nodes2, hwa):
    """
    get the edges connecting the embedding subgraphs defined by the two node sets

    :param (set or list) nodes1: first set of nodes in the hardware graph
    :param (set or list) nodes2: second set of nodes in the hardware graph
    :param (list[tuples] or HardwareAdjacency) hwa: hardware adjacency defining the hardware graph
    :return: the edges in the hardware graph connecting the corresponding embedding subgraphs
    """
    are_neighbored = _get_are_neighbored_func(hwa)
    return sorted(tuple(sorted((n1, n2))) for n1, n2 in product(nodes1, nodes2) if are_neighbored(n1, n2))

def _get_are_neighbored_func(hwa):
    if hasattr(hwa, ARE_NEIGHBORED):
        return hwa.are_neighbored
    return lambda node1, node2: (node1, node2) in hwa or (node2, node1) in hwa


def get_assignments_scores(variables_values_scores, single_var_threshold, total_threshold):
    """
    get the valid assignments according to their scores

    :param (list) variables_values_scores: the single scores for assigning the variables to certain values
    :param (float) single_var_threshold: the threshold which the score of a single variable assignment should exceed
    :param (float) total_threshold: the threshold which the total score of the variable assignments should exceed
    :return:
    """
    assignments_scores = [({}, [])]
    for variable, var_value_scores in variables_values_scores:
        for value, var_value_score in var_value_scores:
            if var_value_score < single_var_threshold:
                break
            _add_var_assignment(assignments_scores, variable, value, var_value_score, total_threshold)

    return [(assignment, prod(assignment_scores))
            for assignment, assignment_scores in assignments_scores if len(assignment) == len(variables_values_scores)]

def _add_var_assignment(assignments_scores, variable, value, var_value_score, total_threshold):
    """
    add the variable to the already collected assignments

    :param assignments_scores: the already collected variable assignments
    :param variable: the variable to be added
    :param value: the value which the variable is assigned to
    :param var_value_score: the score of the single variable assignment
    :param total_threshold: the threshold which the total score of the variable assignments should exceed
    """
    new_assignments_scores = []
    for assignment, assignment_single_scores in assignments_scores:
        if not variable in assignment:
            if prod(assignment_single_scores) * var_value_score < total_threshold:
                break
            assignment[variable] = value
            assignment_single_scores.append(var_value_score)
        else:
            new_scores = assignment_single_scores.copy()
            new_scores[-1] = var_value_score
            if prod(new_scores) < total_threshold:
                break
            new_assignment = assignment.copy()
            new_assignment[variable] = value
            new_assignments_scores.append((new_assignment, new_scores))

    assignments_scores += new_assignments_scores
