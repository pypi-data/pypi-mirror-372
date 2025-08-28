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

""" Tests for the solution class """

import pytest

from quark import Solution
from quark.solution import binary_to_ising, ising_to_binary, invert_ising


X = "x"

NAME = "test_solution"

INVALID_SOL = Solution(var_assignments={1: -1, 2: 0, 3: 1}, name=NAME)
UNDEFINED_SOL = Solution(var_assignments={1: 1, 2: 1, 3: 1}, name=NAME)
COMPACT_SOL = Solution(var_assignments={0: 1, 1: 0, 2: 1}, solving_status="timeout", name=NAME)

VAR_ASSIGNMENTS_ISING_SOL = {(X, 0, 0): 1, (X, 4, 5): -1, (X, 3, 2): 1}
VAR_ASSIGNMENTS_ISING_INV_SOL = {(X, 0, 0): -1, (X, 4, 5): 1, (X, 3, 2): -1}
VAR_ASSIGNMENTS_BINARY_SOL = {(X, 4, 5): 0, (X, 3, 2): 1, (X, 0, 0): 1}

ISING_SOL = Solution(var_assignments=VAR_ASSIGNMENTS_ISING_SOL, solving_status="optimal", name=NAME)
INV_ISING_SOL = Solution(var_assignments=VAR_ASSIGNMENTS_ISING_INV_SOL, solving_status="optimal", name=NAME)
BINARY_SOL = Solution(var_assignments=VAR_ASSIGNMENTS_BINARY_SOL, solving_status="timeout", name=NAME)


def test_init():
    """ test initialization """
    solution = Solution([-1, 1, -1, 1], solving_time=60)
    assert dict(solution) == {0: -1, 1: 1, 2: -1, 3: 1}

def test_has_only_binary_values():
    """ test function for checking if solution has only binary values """
    assert BINARY_SOL.has_only_binary_values()
    assert UNDEFINED_SOL.has_only_binary_values()
    assert not ISING_SOL.has_only_binary_values()

def test_has_only_ising_values():
    """ test function for checking if solution has only ising values """
    assert ISING_SOL.has_only_ising_values()
    assert UNDEFINED_SOL.has_only_ising_values()
    assert not BINARY_SOL.has_only_ising_values()

def test_to_ising():
    """ test conversion of solution to ising form """
    with pytest.raises(ValueError, match="Solution is neither binary nor ising"):
        assert INVALID_SOL.to_ising()
    # solutions should be identical
    assert ISING_SOL.to_ising() == ISING_SOL

    # just invert solution
    inv_ising_sol = ISING_SOL.to_ising(invert=True)
    assert inv_ising_sol == INV_ISING_SOL

    binary_2_ising = BINARY_SOL.to_ising()
    # just checking for the var_assignments
    assert binary_2_ising == VAR_ASSIGNMENTS_ISING_SOL
    # also checking for additional attribute
    assert binary_2_ising.solving_status == BINARY_SOL.solving_status
    assert binary_2_ising.name == ISING_SOL.name

    binary_2_ising = BINARY_SOL.to_ising(invert=True)
    # just checking for the var_assignments
    assert binary_2_ising == VAR_ASSIGNMENTS_ISING_INV_SOL
    # also checking for additional attribute
    assert binary_2_ising.solving_status == BINARY_SOL.solving_status
    assert binary_2_ising.name == INV_ISING_SOL.name
    assert binary_2_ising != INV_ISING_SOL

def test_to_binary():
    """ test conversion of solution to binary form """
    with pytest.raises(ValueError, match="Solution is neither binary nor ising"):
        assert INVALID_SOL.to_binary()
    # var_assignments should be identical
    assert BINARY_SOL.to_binary() == BINARY_SOL
    # also checking for additional attribute
    assert BINARY_SOL.to_binary().solving_status == BINARY_SOL.solving_status

    ising_2_binary = ISING_SOL.to_binary()
    # just checking for the var_assignments
    assert ising_2_binary == VAR_ASSIGNMENTS_BINARY_SOL
    # also checking for additional attribute
    assert ising_2_binary.solving_status == ISING_SOL.solving_status

    ising_2_binary = ISING_SOL.to_binary(is_inverted=True)
    # just checking for the var_assignments
    assert ising_2_binary == {(X, 0, 0): 0, (X, 4, 5): 1, (X, 3, 2): 0}
    # also checking for additional attribute
    assert ising_2_binary.solving_status == ISING_SOL.solving_status
    assert ising_2_binary != [(X, 0, 0), (X, 4, 5), (X, 3, 2)]

def test_decompact():
    """ test reversion of compact """
    variables = [(X, 0, 0), (X, 4, 5), (X, 3, 2)]
    decompact_sol = COMPACT_SOL.decompact(variables)
    assert decompact_sol == BINARY_SOL
    assert decompact_sol.solving_status == BINARY_SOL.solving_status

    with pytest.raises(ValueError, match="Solution is not compact"):
        BINARY_SOL.decompact(variables)
    with pytest.raises(ValueError, match="Solution is not compact"):
        UNDEFINED_SOL.decompact(variables)

    too_less = [(X, 0, 0), (X, 4, 5)]
    with pytest.raises(ValueError, match="Number of provided variables is different than of contained variables"):
        COMPACT_SOL.decompact(too_less)

    wrong = set(variables)
    with pytest.raises(ValueError, match="Dictionary of variables or VariableMapping is expected"):
        # noinspection PyTypeChecker
        COMPACT_SOL.decompact(wrong)

    with pytest.raises(ValueError, match="Solution is empty, there are no variables to be replaced"):
        Solution({}).decompact(variables)

def test_replace_variables():
    """ test variable replacement in solution """
    replacement = {(X, 0, 0): "a", (X, 4, 5): "b", (X, 3, 2): "c"}
    exp_var_assigment = {"a": 1, "b": 0, "c": 1}
    replaced_sol = BINARY_SOL.replace_variables(replacement)
    assert replaced_sol == exp_var_assigment
    assert replaced_sol.solving_status == "timeout"

    too_less = {(X, 0, 0): "a", (X, 4, 5): "b"}
    exp_var_assigment = {"a": 1, "b": 0, (X, 3, 2): 1}
    replaced_sol = BINARY_SOL.replace_variables(too_less, check_all=False)
    assert replaced_sol == exp_var_assigment

    with pytest.raises(ValueError, match="Variable '.*' does not have a mapping to a new variable"):
        BINARY_SOL.replace_variables(too_less)

    replacement = [(X, 0, 0), (X, 4, 5), (X, 3, 2)]
    replaced_sol = COMPACT_SOL.replace_variables(replacement)
    assert replaced_sol == BINARY_SOL

def test_binary_ising_conversion():
    """ test conversion of binary and ising variable assignments """
    assert binary_to_ising(VAR_ASSIGNMENTS_BINARY_SOL) == VAR_ASSIGNMENTS_ISING_SOL
    assert binary_to_ising(VAR_ASSIGNMENTS_BINARY_SOL, invert=True) == VAR_ASSIGNMENTS_ISING_INV_SOL
    assert ising_to_binary(VAR_ASSIGNMENTS_ISING_SOL) == VAR_ASSIGNMENTS_BINARY_SOL
    assert ising_to_binary(VAR_ASSIGNMENTS_ISING_INV_SOL, is_inverted=True) == VAR_ASSIGNMENTS_BINARY_SOL
    assert invert_ising(VAR_ASSIGNMENTS_ISING_INV_SOL) == VAR_ASSIGNMENTS_ISING_SOL
    assert invert_ising(VAR_ASSIGNMENTS_ISING_SOL) == VAR_ASSIGNMENTS_ISING_INV_SOL

def test_repr():
    """ test string generation """
    assert repr(BINARY_SOL) == "Solution({('x', 0, 0): 1, ('x', 3, 2): 1, ('x', 4, 5): 0}, None, 'test_solution')"

def test_str():
    """ test string generation """
    assert str(BINARY_SOL) == "x_0_0 \t= 1\nx_3_2 \t= 1\nx_4_5 \t= 0"

def test_sort_entries():
    """ test sorting """
    solution = Solution(VAR_ASSIGNMENTS_BINARY_SOL)
    assert list(solution.keys()) == [(X, 4, 5), (X, 3, 2), (X, 0, 0)]
    solution.sort_entries()
    assert list(solution.keys()) == [(X, 0, 0), (X, 3, 2), (X, 4, 5)]
