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

""" module for testing the Embedding """

import pytest

from quark import Embedding, HardwareAdjacency


NAME = "test_embedding"
VAR_NODES_MAP = {'a': [4, 0, 24, 48],
                 'b': [5, 1, 25],
                 'c': [6, 2, 26]}
NODE_ASSIGNMENTS = {4: 1, 0: 1, 24: 1, 48: 1, 5: 0, 1: 0, 25: 1, 6: 0, 2: 0, 26: 1}

@pytest.fixture(name="embedding")
def fixture_embedding():
    """ provide the Embedding test object """
    yield Embedding(var_nodes_map=VAR_NODES_MAP, name=NAME, index=0)


def test_init(embedding):
    """ test initialization of embedding """
    assert set(embedding.nodes) == {0, 1, 2, 4, 5, 6, 48, 24, 25, 26}
    assert embedding.max_map_size == 4
    assert embedding.edges == []

def test_consistency():
    """ test correctly thrown errors """
    with pytest.raises(ValueError, match="Either provide mapping from variables to nodes or to edges"):
        Embedding(name="nothing")
    with pytest.raises(ValueError, match="The var_edges_map cannot contain different variables than var_nodes_map"):
        Embedding(var_nodes_map={0: [0], 1: [1]}, var_edges_map={0: [(0, 2)]}, name="wrong_nodes")

    embedding = Embedding(var_nodes_map={0: [0], 1: [1]}, name="no_maps")
    with pytest.raises(ValueError, match="Cannot judge validity without mapping from couplings to edges"):
        embedding.are_all_couplings_mapped([(0, 1)])
    with pytest.raises(ValueError, match="Cannot check connectivity without mapping from variables to edges"):
        embedding.are_all_subgraphs_connected()

    with pytest.raises(ValueError, match="Each variable should map to at least one node"):
        Embedding(var_nodes_map={0: [0, 4], 1: [], 2: [2, 6]}, var_edges_map={0: [(0, 4)], 1: [], 2: [(2, 6)]})

def test_repr(embedding):
    """ test string representation """
    exp_str = "Embedding({'a': [4, 0, 24, 48], 'b': [5, 1, 25], 'c': [6, 2, 26]}, 'test_embedding', 0)"
    assert repr(embedding) == exp_str

def test_str(embedding):
    """ test string representation """
    exp_str = "a \t-> [4, 0, 24, 48]\n" \
              "b \t-> [5, 1, 25]\n" \
              "c \t-> [6, 2, 26]"
    assert str(embedding) == exp_str

def test_get_from_hwa():
    """ test construction of embedding with a given HWA """
    edges = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5), (6, 3), (7, 4), (8, 5), (6, 7), (7, 8)]
    hwa = HardwareAdjacency(edges, "test_hwa")  # 3x3 grid example
    var_nodes_map = {"a": [0, 1], "b": [3, 4], "c": [2, 5]}
    embedding = Embedding.get_from_hwa(var_nodes_map, hwa)
    couplings = [("a", "b"), ("a", "c"), ("c", "b")]

    exp_embedding = Embedding(var_nodes_map={'a': [0, 1], 'b': [3, 4], 'c': [2, 5]},
                              var_edges_map={'a': [(0, 1)], 'b': [(3, 4)], 'c': [(2, 5)]},
                              coupling_edges_map={('a', 'b'): [(0, 3), (1, 4)],
                                                  ('a', 'c'): [(1, 2)],
                                                  ('b', 'c'): [(4, 5)]},
                              name='test_hwa')
    not_exp_embedding = Embedding(var_nodes_map={'a': [0, 1], 'b': [3, 4], 'c': [2, 5]},
                                  var_edges_map={'a': [(0, 1)], 'b': [(3, 4)], 'c': [(2, 5)]},
                                  coupling_edges_map={('a', 'b'): [(0, 3)],
                                                      ('a', 'c'): [(1, 2)],
                                                      ('b', 'c'): [(4, 5)]},
                                  name='test_hwa')
    assert embedding == exp_embedding
    assert embedding != not_exp_embedding
    assert embedding != {'a': [0, 1], 'b': [3, 4], 'c': [2, 5]}

    assert embedding.is_valid(couplings)
    assert set(embedding.edges) > {(0, 1), (0, 3), (1, 2)}
    assert embedding.name == hwa.name

    embedding_only_edges = Embedding.get_from_hwa(var_nodes_map, edges, name=hwa.name)
    assert embedding == embedding_only_edges

def test_checks():
    """ test the different validity checks """
    embedding = Embedding(var_nodes_map={0: [0, 4], 1: [1, 6], 2: [2, 6]})
    assert not embedding.are_all_node_sets_disjoint()
    assert not embedding.is_valid()

    embedding = Embedding(var_nodes_map={0: [0, 4], 1: [1, 5], 2: [2, 6]},
                          var_edges_map={0: [(0, 4)], 1: [], 2: [(2, 6)]})
    assert not embedding.are_all_subgraphs_connected()
    assert not embedding.is_valid()

    embedding = Embedding(var_nodes_map={0: [0, 4], 1: [1], 2: [2, 6]},
                          var_edges_map={0: [(0, 4)], 1: [], 2: [(2, 6)]})
    assert embedding.are_all_subgraphs_connected()
    assert embedding.is_valid()

    embedding = Embedding(coupling_edges_map={(0, 1): [(0, 5)]},
                          var_edges_map={0: [(0, 4)], 1: [(1, 5)], 2: [(2, 6)]})
    assert not embedding.are_all_couplings_mapped([(0, 2)])
    assert embedding.is_valid()
    assert not embedding.is_valid([(0, 2)])

    embedding = Embedding(coupling_edges_map={(0, 1): [(0, 5)]},
                          var_edges_map={0: [(0, 4)], 1: [(1, 7)], 2: [(2, 6)]})
    assert not embedding.are_all_edges_valid()
    assert not embedding.is_valid()

def test_get_single_var_scores(embedding):
    """ test scores of variable assignments for de-embedding """
    assert embedding.get_var_value_scores(NODE_ASSIGNMENTS) == [("a", [(1, 1.0)]),
                                                                ("b", [(0, 2/3), (1, 1/3)]),
                                                                ('c', [(0, 2/3), (1, 1/3)])]

def test_vars_with_broken_embedding(embedding):
    """ test broken embeddings """
    assert embedding.get_vars_with_broken_embedding(NODE_ASSIGNMENTS) == ['b', 'c']

def test_de_embed(embedding):
    """ test de-embedding """
    assert embedding.de_embed(NODE_ASSIGNMENTS) == {'a': 1, 'b': 0, 'c': 0}
    assert embedding.de_embed(NODE_ASSIGNMENTS, return_score=True) == ({'a' : 1, 'b': 0, 'c': 0}, 4/9)

    assert not embedding.de_embed(NODE_ASSIGNMENTS, single_var_threshold=0.8)
    assert embedding.de_embed(NODE_ASSIGNMENTS, single_var_threshold=0.8, return_score=True) == ([], 4/9)

    assert embedding.de_embed(NODE_ASSIGNMENTS, single_var_threshold=0.6) == [{'a': 1, 'b': 0, 'c': 0}]
    assert embedding.de_embed(NODE_ASSIGNMENTS, single_var_threshold=0.6, return_score=True) \
                                                                          == [({'a': 1, 'b': 0, 'c': 0}, 4/9)]

    assert not embedding.de_embed(NODE_ASSIGNMENTS, total_threshold=0.8)
    assert embedding.de_embed(NODE_ASSIGNMENTS, total_threshold=0.8, return_score=True) == ([], 4/9)

    assert embedding.de_embed(NODE_ASSIGNMENTS, total_threshold=0.2) == [{'a': 1, 'b': 0, 'c': 0},
                                                                         {'a': 1, 'b': 1, 'c': 0},
                                                                         {'a': 1, 'b': 0, 'c': 1}]
    assert embedding.de_embed(NODE_ASSIGNMENTS, total_threshold=0.3) == [{'a': 1, 'b': 0, 'c': 0}]
    assert embedding.de_embed(NODE_ASSIGNMENTS, total_threshold=0.2, return_score=True) \
                                                                     == [({'a': 1, 'b': 0, 'c': 0}, 4/9),
                                                                         ({'a': 1, 'b': 1, 'c': 0}, 2/9),
                                                                         ({'a': 1, 'b': 0, 'c': 1}, 2/9)]
    assert embedding.de_embed(NODE_ASSIGNMENTS, total_threshold=0.3, return_score=True) \
                                                                     == [({'a': 1, 'b': 0, 'c': 0}, 4/9)]
