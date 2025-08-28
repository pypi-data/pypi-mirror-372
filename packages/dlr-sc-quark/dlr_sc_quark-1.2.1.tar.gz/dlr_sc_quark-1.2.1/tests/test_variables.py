# Copyright 2025 DLR-SC
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

""" module for testing namedtuple variables """

import pytest

from quark import PolyBinary, PolyIsing
from quark.variables import var_binary_namedtuple, var_ising_namedtuple


X = var_binary_namedtuple("x", "node", "index")
Y = var_binary_namedtuple("y", "node")
S = var_ising_namedtuple("s", "item", "value", "weight")

def test_init():
    """ test initialization """
    assert X("a", 1) == ("x", "a", 1)
    assert X("a", 1).var == "x"
    assert X("a", 1).node == "a"  # pylint: disable=no-member
    assert X("a", 1).index == 1   # pylint: disable=comparison-with-callable  # strange pylint false positives

    assert Y("b") == ("y", "b")
    assert S("box", 10, 5) == ("s", "box", 10, 5)

def test_add():
    """ test addition """
    assert X("a", 1) + X("a", 2) + Y("a") == PolyBinary({(('x', 'a', 1),): 1, (('x', 'a', 2),): 1, (('y', 'a'),): 1})
    assert X("a", 1) + 3 == PolyBinary({(('x', 'a', 1),): 1, (): 3})
    assert S("box", 10, 5) + S("ball", 2, 15) == PolyIsing({(("s", "box", 10, 5),): 1, (("s", "ball", 2, 15),): 1})

    with pytest.raises(ValueError, match="Cannot add PolyIsing and PolyBinary"):
        _ = X("a", 1) + S("box", 10, 5)

def test_radd():
    """ test addition from the right """
    assert 3 + X("a", 1) == PolyBinary({(('x', 'a', 1),): 1, (): 3})
    assert -7 + S("box", 10, 5) == PolyIsing({(("s", "box", 10, 5),): 1, (): -7})

def test_sub():
    """ test subtraction """
    assert X("a", 1) - X("a", 2) - Y("a") == PolyBinary({(('x', 'a', 1),): 1, (('x', 'a', 2),): -1, (('y', 'a'),): -1})
    assert X("a", 1) - 3 == PolyBinary({(('x', 'a', 1),): 1, (): -3})
    assert S("box", 10, 5) - S("ball", 2, 15) == PolyIsing({(("s", "box", 10, 5),): 1, (("s", "ball", 2, 15),): -1})

    with pytest.raises(ValueError, match="Cannot add PolyBinary and PolyIsing"):
        _ = X("a", 1) - S("box", 10, 5)

def test_rsub():
    """ test subtraction from the right """
    assert 3 - X("a", 1) == PolyBinary({(('x', 'a', 1),): -1, (): 3})
    assert -7 - S("box", 10, 5) == PolyIsing({(("s", "box", 10, 5),): -1, (): -7})

def test_mul():
    """ test multiplication """
    assert X("a", 1) * X("a", 2) * Y("a") == PolyBinary({(('x', 'a', 1), ('x', 'a', 2), ('y', 'a')): 1})
    assert X("a", 1) * 3 == PolyBinary({(('x', 'a', 1),): 3})
    assert S("box", 10, 5) * S("ball", 2, 15) == PolyIsing({(("s", "box", 10, 5), ("s", "ball", 2, 15)): 1})

    with pytest.raises(ValueError, match="Cannot multiply PolyBinary and PolyIsing"):
        _ = X("a", 1) * S("box", 10, 5)

def test_rmul():
    """ test multiplication from the right """
    assert 3 * X("a", 1) == PolyBinary({(('x', 'a', 1),): 3})
    assert -7 * S("box", 10, 5) == PolyIsing({(("s", "box", 10, 5),): -7})

def test_truediv():
    """ test division """
    assert X("a", 1) / 3 == PolyBinary({(('x', 'a', 1),): 1 / 3})
    assert S("box", 10, 5) / (-7) == PolyIsing({(("s", "box", 10, 5),): -1 / 7})

def test_pow():
    """ test power """
    assert X("a", 1) ** 3 == PolyBinary({(('x', 'a', 1),): 1})
    assert S("box", 10, 5) ** 3 == PolyIsing({(("s", "box", 10, 5),): 1})
