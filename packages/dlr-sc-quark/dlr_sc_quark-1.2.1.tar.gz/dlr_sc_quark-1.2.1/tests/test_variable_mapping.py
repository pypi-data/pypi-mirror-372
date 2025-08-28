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

""" module for testing variable mapping """

from numbers import Integral
import pytest
from numpy.random import randint
from bidict import inverted, KeyAndValueDuplicationError, ValueDuplicationError

from quark import VariableMapping, Polynomial


X, Y = "x", "y"

MAPPING_DICT = {(1, 2): 4, (1, 3): 5}
MAPPING_DICT_INV = {4: (1, 2), 5: (1, 3)}


def test_init():
    """ test correct construction with inverse """
    # pylint: disable=unsubscriptable-object
    var_mapping = VariableMapping(MAPPING_DICT)
    assert isinstance(var_mapping.inverse, VariableMapping)
    assert var_mapping == MAPPING_DICT
    assert var_mapping.inverse == MAPPING_DICT_INV
    assert var_mapping[(1, 2)] == 4
    assert var_mapping[(1, 3)] == 5
    assert var_mapping.inverse[4] == (1, 2)
    assert var_mapping.inverse[5] == (1, 3)

    var_mapping = VariableMapping(inverted(MAPPING_DICT))
    assert isinstance(var_mapping.inverse, VariableMapping)
    assert var_mapping.inverse == MAPPING_DICT
    assert var_mapping == MAPPING_DICT_INV
    assert var_mapping.inverse[(1, 2)] == 4
    assert var_mapping.inverse[(1, 3)] == 5
    assert var_mapping[4] == (1, 2)
    assert var_mapping[5] == (1, 3)

    var_mapping = VariableMapping()
    assert isinstance(var_mapping.inverse, VariableMapping)
    assert not var_mapping
    assert not var_mapping.inverse
    assert "type_values" not in var_mapping.__dict__
    assert "type_keys" not in var_mapping.__dict__
    assert "type_values" not in var_mapping.inverse.__dict__
    assert "type_keys" not in var_mapping.inverse.__dict__
    assert var_mapping.type_values is None
    assert var_mapping.type_keys is None
    assert var_mapping.inverse.type_values is None
    assert var_mapping.inverse.type_keys is None

    with pytest.raises(ValueDuplicationError):
        VariableMapping({(1, 2): 4, (1, 3): 4})

def test_wrong_init():
    """ test correct raising of errors when instantiating with wrong variable types """
    with pytest.raises(ValueError, match="Invalid key type"):
        VariableMapping({X : 4, (1, 3) : 5})
    with pytest.raises(ValueError, match="Invalid value type"):
        VariableMapping({4 : X, 5 : (1, 3)})
    with pytest.raises(ValueError, match="Invalid value type"):
        VariableMapping({4 : True, 5 : False})
    with pytest.raises(ValueError, match="Invalid key type"):
        VariableMapping({True : 4, False : 5})

    var_mapping = VariableMapping()
    var_mapping.__dict__["_fwdm"] = {(X, 1) : 1, "x2" : 2}
    with pytest.raises(ValueError, match="The keys have inconsistent types"):
        _ = var_mapping.type_keys

    var_mapping = VariableMapping()
    var_mapping.__dict__["_invm"] = {(X, 1) : 1, "x2" : 2}
    with pytest.raises(ValueError, match="The values have inconsistent types"):
        _ = var_mapping.type_values

def test_set_item():
    """ test item setting """
    # pylint: disable=unsupported-assignment-operation
    var_mapping = VariableMapping(MAPPING_DICT)

    var_mapping[(2, 3)] = 3
    assert var_mapping == {(2, 3): 3, (1, 2): 4, (1, 3): 5}
    assert var_mapping.inverse == {3: (2, 3), 4: (1, 2), 5: (1, 3)}

    var_mapping[(2, 3)] = 6
    assert var_mapping == {(2, 3): 6, (1, 2): 4, (1, 3): 5}
    assert var_mapping.inverse == {6: (2, 3), 4: (1, 2), 5: (1, 3)}

    var_mapping.inverse[7] = (0, 1)
    assert var_mapping == {(2, 3): 6, (1, 2): 4, (1, 3): 5, (0, 1): 7}
    assert var_mapping.inverse == {6: (2, 3), 4: (1, 2), 5: (1, 3), 7: (0, 1)}

    var_mapping.inverse[7] = (0, 2)
    assert var_mapping == {(2, 3): 6, (1, 2): 4, (1, 3): 5, (0, 2): 7}
    assert var_mapping.inverse == {6: (2, 3), 4: (1, 2), 5: (1, 3), 7: (0, 2)}

    with pytest.raises(KeyAndValueDuplicationError):
        var_mapping[(2, 3)] = 4
    assert var_mapping == {(2, 3): 6, (1, 2): 4, (1, 3): 5, (0, 2): 7}

    with pytest.raises(ValueDuplicationError):
        var_mapping.inverse[9] = (2, 3)
    assert var_mapping == {(2, 3): 6, (1, 2): 4, (1, 3): 5, (0, 2): 7}

    with pytest.raises(ValueError, match="Invalid key type"):
        var_mapping[X] = 1

    with pytest.raises(ValueError, match="Invalid value type"):
        var_mapping[(1, 4)] = X

def test_del():
    """ test item deletion """
    var_mapping = VariableMapping(MAPPING_DICT)
    del var_mapping[(1, 2)]
    assert var_mapping == {(1, 3): 5}
    assert var_mapping.inverse == {5: (1, 3)}

    var_mapping = VariableMapping(MAPPING_DICT)
    del var_mapping.inverse[4]
    assert var_mapping == {(1, 3): 5}
    assert var_mapping.inverse == {5: (1, 3)}

def test_pop():
    """ test item pop """
    var_mapping = VariableMapping(MAPPING_DICT)
    assert var_mapping.pop((1, 2)) == 4
    assert var_mapping == {(1, 3): 5}
    assert var_mapping.inverse == {5: (1, 3)}

    var_mapping = VariableMapping(MAPPING_DICT)
    assert var_mapping.inverse.pop(4) == (1, 2)
    assert var_mapping == {(1, 3): 5}
    assert var_mapping.inverse == {5: (1, 3)}

    assert var_mapping.type_keys == tuple
    assert var_mapping.type_values == Integral
    assert var_mapping.inverse.pop(5) == (1, 3)
    assert not var_mapping
    assert not var_mapping.inverse
    assert not var_mapping.type_keys
    assert not var_mapping.type_values

    var_mapping = VariableMapping(MAPPING_DICT)
    item = var_mapping.popitem()
    assert item in [((1, 2), 4), ((1, 3), 5)]
    option1 = var_mapping == {(1, 3): 5} and var_mapping.inverse == {5: (1, 3)}
    option2 = var_mapping == {(1, 2): 4} and var_mapping.inverse == {4: (1, 2)}
    assert option1 or option2

    var_mapping = VariableMapping(MAPPING_DICT)
    item = var_mapping.inverse.popitem()
    assert item in [(4, (1, 2)), (5, (1, 3))]
    assert option1 or option2

def test_clear():
    """ test clearing of mapping """
    var_mapping = VariableMapping(MAPPING_DICT)
    assert var_mapping.type_keys == tuple
    assert var_mapping.type_values == Integral
    assert "type_values" in var_mapping.__dict__
    assert "type_keys" in var_mapping.__dict__

    var_mapping.clear()
    assert isinstance(var_mapping.inverse, VariableMapping)
    assert not var_mapping
    assert not var_mapping.inverse
    assert "type_values" not in var_mapping.__dict__
    assert "type_keys" not in var_mapping.__dict__
    assert "type_values" not in var_mapping.inverse.__dict__
    assert "type_keys" not in var_mapping.inverse.__dict__

def test_polynomial_use_case():
    """ test the variable mapping in relation to polynomials """
    tuple_poly = Polynomial({((X, 1),) : 1.0, ((X, 1), (X, 2)) : 3.0, () : 5.0})
    compact_poly = tuple_poly.compact()
    var_mapping = VariableMapping(tuple_poly.variables)

    decompact_poly = compact_poly.replace_variables(var_mapping)
    new_compact_poly = tuple_poly.replace_variables(var_mapping.inverse)
    assert decompact_poly == tuple_poly
    assert new_compact_poly == compact_poly

    var_num = compact_poly.get_variable_num()
    compact_solution = dict(enumerate(randint(0, 2, var_num)))
    decompact_solution = dict(zip(var_mapping.values(), compact_solution.values()))
    compact_value = compact_poly.evaluate(compact_solution)
    decompact_value = decompact_poly.evaluate(decompact_solution)
    assert compact_value == decompact_value

def test_repr():
    """ test string representation """
    assert repr(VariableMapping(MAPPING_DICT)) == "VariableMapping({(1, 2): 4, (1, 3): 5})"

def test_str():
    """ test string representation """
    poly = Polynomial({((Y, 1),) : 1, ((Y, 2),) : 1, ((Y, 3),) : 1})
    poly += Polynomial({((X, 1, 1),) : 1, ((X, 1, 2),) : 1, ((X, 2, 1),) : 1})
    var_mapping = VariableMapping(poly.variables)
    exp_str = "x0 <-> x_1_1\n" \
              "x1 <-> x_1_2\n" \
              "x2 <-> x_2_1\n" \
              "x3 <-> y_1\n" \
              "x4 <-> y_2\n" \
              "x5 <-> y_3"
    assert str(var_mapping) == exp_str

    exp_str = "x_1_1 <-> x0\n" \
              "x_1_2 <-> x1\n" \
              "x_2_1 <-> x2\n" \
              "y_1   <-> x3\n" \
              "y_2   <-> x4\n" \
              "y_3   <-> x5"
    assert str(var_mapping.inverse) == exp_str
