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

""" Testing objective.py """

import pytest

from quark import VariableMapping, Polynomial, PolyIsing, PolyBinary, Objective
from quark.testing import ExampleInstance, ExampleObjective


X, Y = "x", "y"
NAME = "test_objective"
CONSTRUCTED_NAME = 'colored_edges1.000000e+00_one_color_per_node7.000000e+00'

POLY = Polynomial.read_from_string("5 x1 + 6 x2 + 3 x1 x3 - x4 - 3 x2 x4 + 3")
BINARY = PolyBinary.read_from_string("5 x1 + 6 x2 + 3 x1 x3 - x4 - 3 x2 x4 + 3")
ISING = 0.25 * PolyIsing.read_from_string("32 + 13 x1 + 9 x2 + 3 x3 - 5 x4 + 3 x1 x3 - 3 x2 x4")
ISING_INV = 0.25 * PolyIsing(Polynomial.read_from_string("32-13 x1 -9 x2 -3 x3 +5 x4 +3 x1 x3 -3 x2 x4"), inverted=True)
SYM_ISING = PolyIsing({(0, 1): 0.5, (0, 5): 0.5, (1, 2): 0.5, (2, 3): 0.5, (3, 4): 0.5, (4, 5): 0.5}, inverted=False)

OBJ_UNDEF = Objective(POLY, NAME)
OBJ_BINARY = Objective(BINARY, NAME)
OBJ_ISING = Objective(ISING, NAME)
OBJ_ISING_INV = Objective(ISING_INV, NAME)
OBJ_SYM_ISING = Objective(SYM_ISING, NAME)


def test_init(objective, exp_objective):
    """ test objective creation """
    assert objective == exp_objective

def test_get_from_instance(objective_direct_impl, exp_objective, instance):
    """ test different initialization methods """
    # note that at the same time, this also tests two different implementations:
    #     - the fixture objective relies on the implementation of the ExampleConstrainedObjective,
    #       from which we get then automatically generate the corresponding ObjectiveTerms and the Objective
    #     - objective_get uses the direct implementation of the ExampleObjective
    assert not objective_direct_impl.name
    objective_direct_impl.name = CONSTRUCTED_NAME
    assert objective_direct_impl == exp_objective

    with pytest.warns(DeprecationWarning, match="This way of instantiation is deprecated"):
        objective_depr = ExampleObjective(instance=instance, name=CONSTRUCTED_NAME)
    assert objective_depr == exp_objective

def test_repr():
    """ test string representation """
    OBJ_BINARY.name = "test_objective"
    exp_str = "Objective(PolyBinary({(): 3.0, (1,): 5.0, (2,): 6.0, (4,): -1.0, (1, 3): 3.0, (2, 4): -3.0}), " \
                        "'test_objective')"
    assert repr(OBJ_BINARY) == exp_str

def test_str():
    """ test string representation """
    exp_str = "min  +3 +5 x1 +6 x2 -1 x4 +3 x1 x3 -3 x2 x4\n" \
              "s.t. x* in {0, 1}"
    assert str(OBJ_BINARY) == exp_str

    poly = PolyBinary({(): 3, ((X, 1),): 5, ((X, 2),): 6, ((Y, 4, 1),): -1,
                       ((X, 1), (Y, 3, 1)): 3, ((X, 2), (Y, 4, 1)): -3})
    exp_str = "min  +3 +5 x_1 +6 x_2 -1 y_4_1 +3 x_1 y_3_1 -3 x_2 y_4_1\n" \
              "s.t. x_* in {0, 1}\n" \
              "     y_*_* in {0, 1}"
    assert str(Objective(poly)) == exp_str

    exp_str = "min  +8 -3.25 s1 -2.25 s2 -0.75 s3 +1.25 s4 +0.75 s1 s3 -0.75 s2 s4\n" \
              "s.t. s* in {-1, 1}"
    assert str(OBJ_ISING_INV) == exp_str

def test_is_binary():
    """ test is_binary method """
    assert OBJ_BINARY.is_binary()
    assert not OBJ_ISING.is_binary()
    assert not OBJ_ISING_INV.is_binary()
    assert not OBJ_UNDEF.is_binary()

def test_is_ising():
    """ test is_ising method """
    # ising without inverted flag
    assert OBJ_ISING.is_ising()
    assert OBJ_ISING_INV.is_ising()
    assert not OBJ_BINARY.is_ising()
    assert not OBJ_UNDEF.is_ising()

    # non-inverted ising
    assert OBJ_ISING.is_ising(inverted=False)
    assert not OBJ_ISING_INV.is_ising(inverted=False)
    assert not OBJ_BINARY.is_ising(inverted=False)
    assert not OBJ_UNDEF.is_ising(inverted=False)

    # inverted ising
    assert not OBJ_ISING.is_ising(inverted=True)
    assert OBJ_ISING_INV.is_ising(inverted=True)
    assert not OBJ_BINARY.is_ising(inverted=True)
    assert not OBJ_UNDEF.is_ising(inverted=True)

def test_to_ising():
    """ test conversion to ising """
    # binary to ising
    assert OBJ_BINARY.to_ising() == OBJ_ISING
    assert OBJ_BINARY.to_ising() != ISING
    assert OBJ_BINARY.to_ising(invert=True) == OBJ_ISING_INV

    # should be identical
    assert OBJ_ISING.to_ising() == OBJ_ISING
    assert OBJ_ISING_INV.to_ising() == OBJ_ISING_INV

    # inversion
    assert OBJ_ISING_INV.to_ising(invert=True) == OBJ_ISING
    assert OBJ_ISING.to_ising(invert=True) == OBJ_ISING_INV

def test_to_binary():
    """ test conversion to binary """
    assert OBJ_ISING.to_binary() == OBJ_BINARY
    assert OBJ_ISING_INV.to_binary() == OBJ_BINARY
    assert OBJ_UNDEF.to_binary() == OBJ_BINARY
    assert OBJ_BINARY.to_binary() == OBJ_BINARY

def test_compact():
    """ test making the polynomial compact """
    compact, var_mapping = OBJ_BINARY.compact()
    exp_poly = PolyBinary(Polynomial.read_from_string("5 x0 + 6 x1 + 3 x0 x2 - x3 - 3 x1 x3 + 3"))
    exp_vm = VariableMapping({0: 1, 1: 2, 2: 3, 3: 4})
    assert compact.polynomial == exp_poly
    assert compact.name == NAME
    assert var_mapping == exp_vm

    compact, var_mapping = OBJ_ISING_INV.compact(new_name="new_name")
    exp_poly = 0.25 * PolyIsing(Polynomial.read_from_string("32 - 13 x0 - 9 x1 - 3 x2 + 5 x3 + 3 x0 x2 - 3 x1 x3"),
                                inverted=True)
    assert compact.polynomial == exp_poly
    assert compact.name == "new_name"
    assert var_mapping == exp_vm

    compact = Objective(PolyBinary({(0,): 1, (1, 0): 2}), "compact")
    assert compact.compact() == (compact, None)

def test_break_symmetry_by_fixing_variable():
    """ test fixing one variable """
    exp_name = "objective_fixed_spin"
    exp_poly = PolyIsing({(0, 1): 0.5, (0,): 0.5, (1, 2): 0.5, (2, 3): 0.5, (3, 4): 0.5, (4,): 0.5})
    new_objective = OBJ_SYM_ISING.break_symmetry_by_fixing_variable(new_name=exp_name)
    assert new_objective.polynomial == exp_poly
    assert new_objective.name == exp_name

    with pytest.raises(ValueError, match="Only supported for Ising models"):
        OBJ_BINARY.break_symmetry_by_fixing_variable()
    with pytest.raises(ValueError, match="Only supported for Ising models without linear terms"):
        OBJ_ISING.break_symmetry_by_fixing_variable()
    with pytest.raises(ValueError, match="Cannot find variable '6' in polynomial"):
        OBJ_SYM_ISING.break_symmetry_by_fixing_variable(new_name=exp_name, variable=6)

def test_errors():
    """ test the errors """
    # pylint: disable=protected-access
    with pytest.warns(DeprecationWarning, match="This way of instantiation is deprecated"):
        ExampleObjective(instance=ExampleInstance([(0, 1)], 1))
    with pytest.raises(NotImplementedError, match="Provide 'polynomial' on initialization or "):
        Objective._get_polynomial(None)
    with pytest.raises(ValueError, match="Objective's polynomial is neither Polynomial, PolyIsing nor PolyBinary"):
        Objective("13 x1 + 15 x2", "wrong")
    with pytest.warns(UserWarning, match="There is nothing in this Objective"):
        Objective(PolyBinary())
