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

""" module for testing the HardwareAdjacency """

import pytest

from quark import HardwareAdjacency


@pytest.fixture(name="hwa")
def fixture_hwa():
    """ provide the HWA test object """
    yield HardwareAdjacency([(0, 1), (1, 2), (2, 0), (1, 3)], "test_hwa")


def test_init(hwa):
    """ test initialization of hwa """
    assert hwa == [(0, 1), (0, 2), (1, 2), (1, 3)]
    assert hwa.nodes == [0, 1, 2, 3]

    hwa2 = HardwareAdjacency([(0, 1), (1, 2), (2, 0), (1, 3)], "test_hwa")
    assert hwa2 == hwa
    hwa2 = HardwareAdjacency([(0, 1), (1, 2)], "test_hwa")
    assert hwa2 != hwa
    assert hwa2 == [(0, 1), (1, 2)]
    assert hwa2 == [(0, 1), (2, 1)]
    assert hwa2 != [(0, 1), (1, 3)]
    assert hwa2 != {(0, 1), (1, 2)}

def test_repr(hwa):
    """ test string representation """
    exp_str = "HardwareAdjacency([(0, 1), (0, 2), (1, 2), (1, 3)], 'test_hwa')"
    assert repr(hwa) == exp_str

def test_str(hwa):
    """ test string representation """
    exp_str = "[(0, 1), (0, 2), (1, 2), (1, 3)]"
    assert str(hwa) == exp_str

def test_are_neighbored(hwa):
    """ check neighborhood check """
    assert hwa.are_neighbored(0, 1)
    assert hwa.are_neighbored(1, 0)
    assert not hwa.are_neighbored(0, 3)
    assert not hwa.are_neighbored(3, 0)

def test_get_graph(hwa):
    """ test graph construction """
    node_data = {"pos": {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}}
    edge_data = {"color": 0}
    hwa.update_graph(node_data, edge_data)
    assert sorted(hwa.graph.nodes) == [0, 1, 2, 3]
    assert sorted(hwa.graph.edges) == [(0, 1), (0, 2), (1, 2), (1, 3)]
    assert dict(hwa.graph.nodes(data="pos")) == {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}
    assert list(hwa.graph.edges(data="color")) == [(0, 1, 0), (0, 2, 0), (1, 2, 0), (1, 3, 0)]
