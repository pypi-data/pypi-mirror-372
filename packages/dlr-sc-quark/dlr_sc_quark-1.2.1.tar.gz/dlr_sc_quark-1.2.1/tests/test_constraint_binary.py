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

""" module for testing the ConstraintBinary """

import pytest

from quark import PolyBinary, ConstraintBinary
from quark.poly_binary import get_all_reduction_penalty_terms
from quark.constraint_binary import get_binary_representation_polynomial, get_standard_penalty_polynomial, \
    get_reduction_constraints, retrieve_reduction, matches_special_penalty_constraint, \
    get_special_constraint_penalty_poly


QUADRATIC_POLY = PolyBinary({(("x", 1),): 7, (("x", 2), ("x", 1)): 2, (): -3})
LINEAR_POLY = PolyBinary({(("x", 1),): 7, (("x", 2),): 2})
QUBIC_POLY = PolyBinary({(("x", 1), ("x", 2), ("x", 3)): 1, (("x", 1),): 1})
NAME = "test_constraint"


def test_init__check_input():
    """ test errors for inconsistent data """
    with pytest.raises(ValueError, match="At least one bound needs to be given"):
        ConstraintBinary(PolyBinary())
    with pytest.raises(ValueError, match="At the moment can only handle PolyBinary"):
        ConstraintBinary(PolyBinary().to_ising(), 0, 1)

def test_init__check_consistency():
    """ test errors for inconsistent data """
    with pytest.raises(ValueError, match="Lower bound must be less than or equal to upper bound"):
        ConstraintBinary(PolyBinary({"a" : 1}), 4, 2)
    with pytest.raises(ValueError, match="Lower bound must be less than or equal to upper bound"):
        ConstraintBinary(PolyBinary(), 4)
    with pytest.raises(ValueError, match="Lower bound must be less than or equal to upper bound"):
        ConstraintBinary(PolyBinary(), upper_bound=-4)
    with pytest.raises(ValueError, match="Unfulfillable constraint '5 == 1'"):
        ConstraintBinary(PolyBinary({(): 5}), 1, 1)
    with pytest.raises(ValueError, match="Unfulfillable constraint '4 <= 0 <= 8'"):
        ConstraintBinary(PolyBinary(), 4, 8)
    with pytest.raises(ValueError, match="Unfulfillable constraint '-6 <= 1 <= -4'"):
        ConstraintBinary(PolyBinary() + 1, upper_bound=-4, lower_bound=-6)
    with pytest.warns(UserWarning, match="Useless constraint '0 <= 5 <= 10'"):
        ConstraintBinary(PolyBinary({(): 5}), 0, 10)

    # lb <= p+(x) + p-(x) + c <= ub
    with pytest.raises(ValueError, match="Negative coefficients do not suffice to get below the upper bound"):
        ConstraintBinary(LINEAR_POLY, -1, -1)
    with pytest.raises(ValueError, match="Positive coefficients do not suffice to get above the lower bound"):
        ConstraintBinary(PolyBinary({(("x", 0),): 1}) - LINEAR_POLY, 2, 2)
    with pytest.raises(ValueError, match="Negative coefficients do not suffice to get below the upper bound"):
        ConstraintBinary(QUADRATIC_POLY, -4, -4)
    with pytest.raises(ValueError, match="Positive coefficients do not suffice to get above the lower bound"):
        ConstraintBinary(PolyBinary({(("x", 0),): 1}) - QUADRATIC_POLY, 5, 5)

    # preprocessable equality and negation
    with pytest.warns(UserWarning, match=r"The two variables 'x' and 'y' are set to be equal"):
        ConstraintBinary(PolyBinary({'x': 1, 'y': -1}), 0, 0)
    with pytest.warns(UserWarning, match=r"The two variables 'x' and 'y' are set to be negations of each other"):
        ConstraintBinary(PolyBinary({'x': 1, 'y': 1}), 1, 1)

    # contradiction found by preprocessing
    with pytest.raises(ValueError, match=r"Unfulfillable constraint '\+1 \+1 x1 \+1 x2 -1 x1 x2 == 0'"):
        ConstraintBinary(PolyBinary({"x1": 1, "x2": 1, ("x1", "x2"): -1, (): 1}), 0, 0)
    with pytest.raises(ValueError, match=r"Unfulfillable constraint '-2 \+1 x1 -1 x2 -1 x3 \+1 x2 x3 == 0'"):
        ConstraintBinary(PolyBinary({"x1": 1, "x2": -1, "x3": -1, ("x2", "x3"): 1, (): -2}), 0, 0)

    # bounds too weak on both sides
    with pytest.warns(UserWarning, match=r"Useless constraint '0 <= \+5 x1 <= 10'"):
        ConstraintBinary(PolyBinary({(1,): 5}), 0, 10)

    # bounds too weak on one sides
    with pytest.warns(UserWarning, match="Upper bound could be sharpened to 2"):
        ConstraintBinary(PolyBinary({(0,): 1, (1,): 1}), 1, 3)
    with pytest.warns(UserWarning, match="Lower bound could be sharpened to 0"):
        ConstraintBinary(PolyBinary({(0,): 1, (1,): 1}), -1, 1)

def test_init__open_bounds():
    """ test the worst case calculation of open bounds """
    constraint = ConstraintBinary(LINEAR_POLY, 1)
    assert constraint.upper_bound == 9

    constraint = ConstraintBinary(LINEAR_POLY, upper_bound=3)
    assert constraint.lower_bound == 0

    constraint = ConstraintBinary(QUADRATIC_POLY, 1)
    assert constraint.upper_bound == 6

    constraint = ConstraintBinary(QUADRATIC_POLY, upper_bound=3)
    assert constraint.lower_bound == -3

def test_add():
    """ test addition of scalars to constraint """
    exp_poly = PolyBinary({(("x", 1),): 7, (("x", 2), ("x", 1)): 2, (): -1})
    constraint = ConstraintBinary(QUADRATIC_POLY, 5, 6)
    constraint += 2
    assert constraint.polynomial == exp_poly
    assert constraint.lower_bound == 7
    assert constraint.upper_bound == 8

    constraint *= -2
    assert constraint.polynomial == -2 * exp_poly
    assert constraint.lower_bound == -16
    assert constraint.upper_bound == -14

    with pytest.raises(ValueError, match="Constant must be a number"):
        _ = ConstraintBinary(LINEAR_POLY, 0, 1) + PolyBinary()

def test_sub():
    """ test subtraction of scalars from constraint """
    exp_poly = PolyBinary({(("x", 1),): 7, (("x", 2), ("x", 1)): 2, (): -5})
    constraint = ConstraintBinary(QUADRATIC_POLY, 5, 6)
    constraint -= 2
    assert constraint.polynomial == exp_poly
    assert constraint.lower_bound == 3
    assert constraint.upper_bound == 4

    with pytest.raises(ValueError, match="Constant must be a number"):
        _ = ConstraintBinary(LINEAR_POLY, 0, 1) - PolyBinary()

def test_mul():
    """ test multiplication of scalars to constraint """
    exp_poly = PolyBinary({(("x", 1),): 14, (("x", 2), ("x", 1)): 4, (): -6})
    constraint = ConstraintBinary(QUADRATIC_POLY, 5, 6)
    constraint *= 2
    assert constraint.polynomial == exp_poly
    assert constraint.lower_bound == 10
    assert constraint.upper_bound == 12

    constraint *= -2
    assert constraint.polynomial == -2 * exp_poly
    assert constraint.lower_bound == -24
    assert constraint.upper_bound == -20

    with pytest.raises(ValueError, match="Constant must be a number"):
        _ = ConstraintBinary(LINEAR_POLY, 0, 1) * PolyBinary()

def test_eq():
    """ test equality of constraints """
    # Equality Constraints: Upper_Bound == Lower_Bound
    constraint1 = ConstraintBinary(QUADRATIC_POLY, 2, 2)
    constraint2 = ConstraintBinary(QUADRATIC_POLY, 2, 2)
    assert constraint1 != QUADRATIC_POLY
    assert constraint1 == constraint2
    assert constraint1 == constraint2.normalize()
    assert constraint1.polynomial != constraint2.normalize().polynomial
    assert constraint1 == constraint1 + 3
    assert constraint1 == constraint1 * 4

    # Inequality Constraints: Upper_Bound > Lower_Bound
    constraint1 = ConstraintBinary(QUADRATIC_POLY, 5, 6)
    constraint2 = ConstraintBinary(PolyBinary({(("x", 1),): 7, (("x", 2), ("x", 1)): 2, (): -3}), 5, 6)
    assert constraint1 != QUADRATIC_POLY
    assert constraint1 == constraint2
    assert constraint1 == constraint2.normalize()
    assert constraint1.polynomial != constraint2.normalize().polynomial
    assert constraint1 == constraint1 + 3
    assert constraint1 == constraint1 * 4

    # different polynomial
    assert constraint1 != ConstraintBinary(PolyBinary({(("x", 1),): 5, (("x", 2), ("x", 1)): 2, (): 3}), 5, 6)
    # different upper bound
    assert constraint1 != ConstraintBinary(QUADRATIC_POLY, 5, 5)
    # different lower bound
    assert constraint1 != ConstraintBinary(QUADRATIC_POLY, 4, 6)
    # different variable types
    assert constraint1 != ConstraintBinary(QUADRATIC_POLY.compact(), 5, 6)
    # different monomials
    assert constraint1 != ConstraintBinary(PolyBinary({(("x", 2), ("x", 1)): 2, (): 5}), 5, 6)
    # empty polynomial
    with pytest.warns(UserWarning, match="Useless constraint '0 == 0'"):
        useless1 = ConstraintBinary(PolyBinary(), 0, 0)
        assert useless1 == ConstraintBinary(PolyBinary(), 0, 0)
    assert useless1 != constraint1

    with pytest.warns(UserWarning, match="Useless constraint '0 <= 0 <= 1'"):
        useless2 = ConstraintBinary(PolyBinary(), 0, 1)
    assert useless1 != useless2

    # equality constraints with str variables
    assert ConstraintBinary(PolyBinary({("a", "b"): 1}), 0, 0) == ConstraintBinary(PolyBinary({("a", "b"): 2}), 0, 0)

    # equality constraints with int variables
    constraint1 = ConstraintBinary(PolyBinary({(1, 2): 1, (3, 4): 1}), 1, 1)
    constraint2 = ConstraintBinary(PolyBinary({(1, 2): 3, (3, 4): 3, (): 2}), 5, 5)
    assert constraint1 == constraint2

def test_repr():
    """ test string representation """
    constraint = ConstraintBinary(PolyBinary({(0,): 1, (1,): 1}), 0, 1)
    assert repr(constraint) == "ConstraintBinary(PolyBinary({(0,): 1, (1,): 1}), 0, 1)"

def test_str():
    """ test string creation """
    constraint = ConstraintBinary(QUADRATIC_POLY, 1, 2)
    assert str(constraint) == "1 <= -3 +7 x_1 +2 x_1 x_2 <= 2"

    constraint = ConstraintBinary(QUADRATIC_POLY, 4, 4)
    assert str(constraint) == "-3 +7 x_1 +2 x_1 x_2 == 4"

    constraint = ConstraintBinary(QUADRATIC_POLY, 4, 4)
    assert constraint.__str__(revert_eq=True) == "4 == -3 +7 x_1 +2 x_1 x_2"  # pylint: disable=unnecessary-dunder-call

    constraint = ConstraintBinary(PolyBinary({(): -15.99999992050575, (('alpha', 0),): 1.0, (('alpha', 1),): 2.0,
                                              (('alpha', 2),): 4.5, (('x', 2),): -4.000000022959645, (('x', 3),):
                                                  -8.00000004591929, (('x', 4),): -1.0000000057399112}), -20.0, -9.0)
    assert str(constraint) == "-20 <= -16 +1 alpha_0 +2 alpha_1 +4.5 alpha_2 -4 x_2 -8 x_3 -1 x_4 <= -9"

def test_is_equality_constraint():
    """ test if constraint is equality """
    constraint = ConstraintBinary(LINEAR_POLY, 0, 1)
    assert not constraint.is_equality_constraint()
    constraint = ConstraintBinary(QUADRATIC_POLY, 0, 0)
    assert constraint.is_equality_constraint()
    constraint = ConstraintBinary(QUBIC_POLY, 1, 1)
    assert constraint.is_equality_constraint()

def test_is_integer():
    """ test if constraint is integer """
    constraint = ConstraintBinary(LINEAR_POLY, 0, 1)
    assert constraint.is_integer()
    constraint = ConstraintBinary(QUADRATIC_POLY, 0.5, 1)
    assert not constraint.is_integer()
    constraint = ConstraintBinary(QUBIC_POLY, 0, 0.5)
    assert not constraint.is_integer()

    poly = PolyBinary({(("x", 1), ("x", 2), ("x", 3)): 1.000001, (("x", 1),): 1.000001})
    constraint = ConstraintBinary(poly, 0, 1)
    assert not constraint.is_integer()
    assert constraint.is_integer(precision=1e-3)

def test_round():
    """ test rounding """
    poly = PolyBinary({(0,): 5, (1,): 6, (2, 0): -3, (1, 3): 0.5, (3,): -1, (0, 1): 0.9, (): 16, (2,): 0, (2, 2): 2})
    constraint = ConstraintBinary(poly, 12.4, 19.9)
    exp_poly = PolyBinary({(0,): 5, (1,): 6, (2, 0): -3, (2, 2): 2, (1, 3): 0, (3,): -1, (0, 1): 1, (): 16})
    exp_constraint = ConstraintBinary(exp_poly, 12, 20)
    assert constraint.round() == exp_constraint

    poly = PolyBinary({(1,): 4, (2,): 5.7777})
    constraint = ConstraintBinary(poly, 5, 8.991)
    exp_poly = PolyBinary({(1,): 4, (2,): 5.78})
    exp_constraint = ConstraintBinary(exp_poly, 5, 8.99)
    assert constraint.round(2) == exp_constraint

def test_is_normal():
    """ test check of normalization of constraints """
    assert ConstraintBinary(QUADRATIC_POLY, 0, 6).is_normal()
    assert not ConstraintBinary(QUADRATIC_POLY, 5, 6).is_normal()
    assert not ConstraintBinary(-1 * QUADRATIC_POLY, -6, 0).is_normal()

def test_normalize():
    """ test normalization of constraints """
    exp_constraint = ConstraintBinary(QUADRATIC_POLY, 0, 6)
    normalized = exp_constraint.normalize()
    assert normalized.polynomial == exp_constraint.polynomial
    assert normalized.lower_bound == exp_constraint.lower_bound
    assert normalized.upper_bound == exp_constraint.upper_bound

    constraint = ConstraintBinary(-1 * QUADRATIC_POLY, -6, 0)
    normalized = constraint.normalize()
    assert normalized.polynomial == exp_constraint.polynomial
    assert normalized.lower_bound == exp_constraint.lower_bound
    assert normalized.upper_bound == exp_constraint.upper_bound

    with pytest.warns(UserWarning, match="Useless constraint '0 <= 5 <= 10'"):
        constraint = ConstraintBinary(PolyBinary({(): 5}), 0, 10)
        assert constraint.normalize() == constraint

def test_replace_variables():
    """ test replacement of variables """
    constraint = ConstraintBinary(QUBIC_POLY, 0, 1)
    qubic_flat = PolyBinary({(0, 1, 2): 1, (0,): 1})
    exp_constraint = ConstraintBinary(qubic_flat, 0, 1)
    new_constraint = constraint.replace_variables({("x", 1): 0, ("x", 2): 1, ("x", 3): 2})
    assert new_constraint == exp_constraint

    replacement = {("x", 1): "c", ("x", 2): "b", ("x", 3): "a"}
    qubic_str = PolyBinary({("c", "b", "a"): 1, ("c",): 1})
    exp_constraint = ConstraintBinary(qubic_str, 0, 1)
    new_constraint = constraint.replace_variables(replacement)
    assert new_constraint == exp_constraint

def test_get_preprocessable_variables():
    """ test preprocessable variables """
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('x', 1\): 0, \('x', 2\): 0\}"):
        constraint = ConstraintBinary(LINEAR_POLY, 0, 0)
    assert constraint.get_preprocessable_variables() == {('x', 1): 0, ('x', 2): 0}

    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{'x': 1, 'y': 1\}"):
        constraint = ConstraintBinary(PolyBinary({("x",): 1, ("x", "y"): 2, (): 3}), 6, 6)
    assert constraint.get_preprocessable_variables() == {'x': 1, 'y': 1}

def test_preprocess():
    """ test preprocessable variables """
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('x', 1\): 0, \('x', 2\): 0\}"):
        constraint = ConstraintBinary(LINEAR_POLY, 0, 0)
    exp_preprocessed = {("x", 1): 0, ("x", 2): 0}
    preprocessed_constraint, preprocessed = constraint.preprocess()
    assert preprocessed_constraint is None
    assert preprocessed == exp_preprocessed

    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{'x': 1, 'y': 1\}"):
        constraint = ConstraintBinary(PolyBinary({("x",): 1, ("x", "y"): 2, ("z", "w"): -1, (): 3}), 6, 6)
    exp_constraint = ConstraintBinary(PolyBinary({("z", "w"): 1}), 0, 0)
    exp_preprocessed = {"x": 1, "y": 1}
    preprocessed_constraint, preprocessed = constraint.preprocess()
    assert preprocessed_constraint == exp_constraint
    assert preprocessed == exp_preprocessed

    with pytest.warns(UserWarning, match=r"The two variables 'x' and 'y' are set to be equal"):
        constraint = ConstraintBinary(PolyBinary({("x",): 1, ("y",): -1, (): 5}), 5, 5)
    exp_preprocessed = {"y": PolyBinary({"x": 1})}
    preprocessed_constraint, preprocessed = constraint.preprocess()
    assert preprocessed_constraint is None
    assert preprocessed == exp_preprocessed

    with pytest.warns(UserWarning, match=r"The two variables 'x' and 'y' are set to be negations of each other"):
        constraint = ConstraintBinary(PolyBinary({("x",): 1, ("y",): 1, (): 4}), 5, 5)
    exp_preprocessed = {"y": PolyBinary({"x": -1, (): 1})}
    preprocessed_constraint, preprocessed = constraint.preprocess()
    assert preprocessed_constraint is None
    assert preprocessed == exp_preprocessed

def test_copy():
    """ test copying of constraint """
    constraint = ConstraintBinary(LINEAR_POLY, 0, 1)
    constraint_copy = constraint.copy()
    assert constraint_copy == constraint
    assert constraint_copy is not constraint

def test_provides_penalty_term_directly():
    """ test check whether the polynomial of the constraint directly is a penalty term """
    constraint = ConstraintBinary(PolyBinary({(0, 1): 1, (1, 2): -1}), 0, 0)
    assert not constraint.provides_penalty_term_directly()

    # all summands positive
    constraint = ConstraintBinary(PolyBinary({(0, 1): 1, (1, 2): 1}), 0, 0)
    assert constraint.provides_penalty_term_directly()

    # penalty term to first linear reduction constraint
    constraint = ConstraintBinary(PolyBinary({('a', 'r'): 1, 'r': -1}), 0, 0)
    assert constraint.provides_penalty_term_directly()

    # penalty term to second linear reduction constraint
    constraint = ConstraintBinary(PolyBinary({('r',): 3, ('r', 'x'): -2, ('a', 'r'): -2, ('a', 'x'): 1}), 0, 0)
    assert constraint.provides_penalty_term_directly()

    # penalty term to second linear reduction constraint with different variable ordering
    constraint = ConstraintBinary(PolyBinary({('r',): 3, ('r', 'x'): -2, ('a', 'r'): -2, ('a', 'x'): 1}), 0, 0)
    assert not constraint.provides_penalty_term_directly(max_degree=1)

def test_get_reductions__standard():
    """ test reduction """
    # already linear, nothing happens
    constraint = ConstraintBinary(LINEAR_POLY, 3, 9)
    linear_constraint, reductions = constraint.get_reductions()
    assert linear_constraint == constraint
    assert not reductions

    with pytest.warns(UserWarning, match="Force is only necessary to get a fully linear problem"):
        constraint.get_reductions(max_degree=2, force=True)

    # already quadratic, nothing happens when reducing to degree 2
    constraint = ConstraintBinary(QUADRATIC_POLY, 3, 6)
    quadratic_constraint, reductions = constraint.get_reductions(2)
    assert quadratic_constraint == constraint
    assert not reductions

    # reduction from quadratic to linear
    linear_constraint, reductions = constraint.get_reductions()  # default reduction degree is 1
    exp_poly = PolyBinary({(("reduction", "x", 1, "x", 2),): 2, (("x", 1),): 7, (): -3})
    exp_constraint = ConstraintBinary(exp_poly, 3, 6)
    exp_reductions = [(('reduction', 'x', 1, 'x', 2), ('x', 1), ('x', 2))]
    assert linear_constraint == exp_constraint
    assert reductions == exp_reductions

    # reduction from qubic to quadratic
    constraint = ConstraintBinary(QUBIC_POLY, 0, 1)
    quadratic_constraint, reductions = constraint.get_reductions(2)
    exp_poly = PolyBinary({(('x', 1),): 1, (('reduction', 'x', 1, 'x', 2), ('x', 3)): 1})
    exp_constraint = ConstraintBinary(exp_poly, 0, 1)
    exp_reductions = [(('reduction', 'x', 1, 'x', 2), ('x', 1), ('x', 2))]
    assert quadratic_constraint == exp_constraint
    assert reductions == exp_reductions

    # reduction from qubic to linear
    linear_constraint, reductions = constraint.get_reductions(1)
    exp_poly = PolyBinary({(('x', 1),): 1, (('reduction', 'x', 3, 'reduction', 'x', 1, 'x', 2),): 1})
    exp_constraint = ConstraintBinary(exp_poly, 0, 1)
    exp_reductions = [(('reduction', 'x', 1, 'x', 2), ('x', 1), ('x', 2)),
                      (('reduction', 'x', 3, 'reduction', 'x', 1, 'x', 2), ('x', 3), ('reduction', 'x', 1, 'x', 2))]
    assert linear_constraint == exp_constraint
    assert reductions == exp_reductions

    # reduction from qubic to linear using a specific predefined reduction
    use_reductions = [(('nice_reduction_var', 1), ('x', 3), ('x', 1))]
    linear_constraint, reductions = constraint.get_reductions(1, use_reductions)
    exp_poly = PolyBinary({(('x', 1),): 1, (('reduction', 'nice_reduction_var', 1, 'x', 2),): 1})
    exp_constraint = ConstraintBinary(exp_poly, 0, 1)
    exp_reductions = [(('reduction', 'nice_reduction_var', 1, 'x', 2), ('nice_reduction_var', 1), ('x', 2))]
    assert linear_constraint == exp_constraint
    assert reductions == exp_reductions

    # just apply a specific predefined reduction
    use_reductions = [(('nice_reduction_var', 1), ('x', 3), ('x', 1))]
    reduced_constraint, reductions = constraint.get_reductions(None, use_reductions)
    exp_poly = PolyBinary({(('x', 1),): 1, (('nice_reduction_var', 1), ('x', 2)): 1})
    exp_constraint = ConstraintBinary(exp_poly, 0, 1)
    assert reduced_constraint == exp_constraint
    assert reductions == []

def test_get_reductions__special():
    """ test reduction on reduction constraint itself """
    # special constraint a * x == r
    constraint = ConstraintBinary(PolyBinary({('a', 'x'): -1, 'r': 1}), 0, 0)
    reduced_constraint, reductions = constraint.get_reductions()
    assert reduced_constraint is None
    assert reductions == [('r', 'a', 'x')]

    # special constraint 3 * r - 2 * r * x - 2 * a * r + a * x == 0  ->  reduction penalty term
    constraint = ConstraintBinary(PolyBinary({('r',): 3, ('r', 'x'): -2, ('a', 'r'): -2, ('a', 'x'): 1}), 0, 0)
    reduced_constraint, reductions = constraint.get_reductions(force=True)
    assert reduced_constraint is None
    assert reductions == [('r', 'a', 'x')]

    # special constraint 1 * r - 1 * r * x - 1 * a * r + a * x == 0  ->  reduction penalty term
    # but without force the constraint is kept
    constraint = ConstraintBinary(PolyBinary({('r',): 1, ('r', 'x'): -1, ('a', 'r'): -1, ('a', 'x'): 1}), 0, 0)
    reduced_constraint, reductions = constraint.get_reductions()
    assert reduced_constraint == constraint
    assert reductions == []

    reduced_constraint, reductions = constraint.get_reductions(force=True)
    assert reduced_constraint is None
    assert reductions == [('r', 'a', 'x')]

def test_reduce():
    """ test reduction and get all constraints """
    # reduction from quadratic to linear
    constraint = ConstraintBinary(QUADRATIC_POLY, 3, 6)
    linear_constraints = constraint.reduce(1)
    exp_poly = PolyBinary({(("reduction", "x", 1, "x", 2),): 2, (("x", 1),): 7, (): -3})
    exp_constraint_original = ConstraintBinary(exp_poly, 3, 6)
    exp_polys = [PolyBinary({(('x', 1),): -1, (('reduction', 'x', 1, 'x', 2),): 1}),
                 PolyBinary({(('x', 2),): -1, (('reduction', 'x', 1, 'x', 2),): 1}),
                 PolyBinary({(('x', 1),): -1, (('x', 2),): -1, (('reduction', 'x', 1, 'x', 2),): 1})]
    exp_constraints = {"original": exp_constraint_original,
                       "reduction_x_1_x_2_0": ConstraintBinary(exp_polys[0], -1, 0),
                       "reduction_x_1_x_2_1": ConstraintBinary(exp_polys[1], -1, 0),
                       "reduction_x_1_x_2_2": ConstraintBinary(exp_polys[2], -1, 0)}
    assert linear_constraints == exp_constraints

    # reduction from qubic to quadratic
    constraint = ConstraintBinary(QUBIC_POLY, 0, 1)
    quadratic_constraints = constraint.reduce(2)
    exp_poly = PolyBinary({(('x', 1),): 1, (('reduction', 'x', 1, 'x', 2), ('x', 3)): 1})
    exp_constraint_original = ConstraintBinary(exp_poly, 0, 1)
    exp_poly = PolyBinary({(('x', 1), ('x', 2)): -1, (('reduction', 'x', 1, 'x', 2),): 1})
    exp_constraint_reduction = ConstraintBinary(exp_poly, 0, 0)
    exp_constraints = {"original": exp_constraint_original,
                       "reduction_x_1_x_2": exp_constraint_reduction}
    assert quadratic_constraints == exp_constraints

    # just apply a specific predefined reduction
    use_reductions = [(("nice_reduction_var", 1), ('x', 3), ('x', 1))]
    reduced_constraints = constraint.reduce(None, use_reductions)
    exp_poly = PolyBinary({(('x', 1),): 1, (("nice_reduction_var", 1), ('x', 2)): 1})
    exp_constraint = ConstraintBinary(exp_poly, 0, 1)
    assert reduced_constraints == {"original": exp_constraint}

    # check useless constraint when replacing variables in useless constraint
    exp_constraints = {"reduction_x_1_x_2_0": ConstraintBinary(exp_polys[0], -1, 0),
                       "reduction_x_1_x_2_1": ConstraintBinary(exp_polys[1], -1, 0),
                       "reduction_x_1_x_2_2": ConstraintBinary(exp_polys[2], -1, 0)}
    with pytest.warns(UserWarning, match="Useless constraint"):
        constraint = ConstraintBinary(PolyBinary({(('x', 1), ('x', 2)): 1}), 0, 1)
        reduced_constraints = constraint.reduce(force=True, max_degree=1)
    assert reduced_constraints == exp_constraints


def test_get_penalty_terms__constant_polynomial():
    """ test construction of objective terms with constant polynomial """
    poly = PolyBinary({(): 5})
    with pytest.warns(UserWarning, match="Useless constraint '5 == 5'"):
        constraint = ConstraintBinary(poly, 5, 5)
        assert not constraint.get_penalty_terms()

    with pytest.warns(UserWarning, match="Useless constraint '0 <= 5 <= 10'"):
        constraint = ConstraintBinary(poly, 0, 10)
        assert not constraint.get_penalty_terms()

def test_get_penalty_terms__linear_equality_constraint():
    """ test construction of objective terms for equality constraint """
    constraint = ConstraintBinary(LINEAR_POLY, 5, 5)
    exp_penalty_terms = {NAME: (LINEAR_POLY - 5)**2}
    assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

    # in the following case the polynomial can be used itself as a penalty term as it is >=0 for all assignments
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('x', 1\): 0, \('x', 2\): 0\}"):
        constraint = ConstraintBinary(LINEAR_POLY, 0, 0)
    exp_penalty_terms = {NAME: LINEAR_POLY}
    assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

def test_get_penalty_terms__linear_inequality_constraint():
    """ test construction of objective terms for inequality """
    constraint = ConstraintBinary(LINEAR_POLY, 3, 9)
    exp_poly = (LINEAR_POLY - 3 - get_binary_representation_polynomial(6, variable_prefix="test_constraint_slack")) ** 2
    exp_penalty_terms = {NAME: exp_poly}
    assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

    with pytest.raises(ValueError, match="Inequality constraint must have integer coefficients and boundaries"):
        ConstraintBinary(PolyBinary({"x": 3.5}), 0, 1).get_penalty_terms()
    with pytest.raises(ValueError, match="Inequality constraint must have integer coefficients and boundaries"):
        ConstraintBinary(PolyBinary({"x": 3}), 0, 1.5).get_penalty_terms()

def test_get_penalty_terms__quadratic_equality_constraint():
    """ test construction of objective terms for equality constraint with quadratic polynomial """
    constraint = ConstraintBinary(QUADRATIC_POLY, 5, 5)
    poly, exp_reductions = QUADRATIC_POLY.reduce()
    exp_penalty_terms = {NAME: (poly - 5) ** 2}
    exp_penalty_terms.update(get_all_reduction_penalty_terms(exp_reductions))
    assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

    # in the following case the polynomial (minus the constant) can be used itself as a penalty term
    # as it is >=0 for all assignments
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('x', 1\): 0\}"):
        constraint = ConstraintBinary(QUADRATIC_POLY, -3, -3)
    exp_penalty_terms = {NAME: QUADRATIC_POLY + 3}
    assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

    constraint = ConstraintBinary(PolyBinary({("x",): 1, ("x", "y"): -2, (): 3}), 2, 2)
    exp_penalty_terms = {"reduction_x_y": PolyBinary({(("reduction", "x", "y"),): 3,
                                                      (("reduction", "x", "y"), ("x",)): -2,
                                                      (("reduction", "x", "y"), ("y",)): -2,
                                                      (("x",), ("y",)): 1}),
                         "test_constraint": PolyBinary({(): 1, (("x",),): 3, (("reduction", "x", "y"), ("x",)): -4})}
    with pytest.warns(UserWarning, match=r"Variables are replaced by tuple variables"):
        assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

def test_get_penalty_terms__quadratic_inequality_constraint():
    """ test construction of objective terms for inequality with quadratic polynomial """
    constraint = ConstraintBinary(QUADRATIC_POLY, 5, 6)
    poly, exp_reductions = QUADRATIC_POLY.reduce()
    exp_poly = (poly - 5 - get_binary_representation_polynomial(1, variable_prefix="test_constraint_slack")) ** 2
    exp_penalty_terms = {NAME: exp_poly}
    exp_penalty_terms.update(get_all_reduction_penalty_terms(exp_reductions))
    assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

def test_get_penalty_terms__quartic_equality_constraint():
    """ test construction of objective terms for inequality with quadratic polynomial """
    R, X = "reduction", "x"
    exp_reductions1 = {"reduction_x_1_x_2": PolyBinary({((R, X, 1, X, 2),): 3,
                                                        ((R, X, 1, X, 2), (X, 1)): -2,
                                                        ((R, X, 1, X, 2), (X, 2)): -2,
                                                        ((X, 1), (X, 2)): 1}),
                       "reduction_x_3_x_4": PolyBinary({((R, X, 3, X, 4),): 3,
                                                        ((R, X, 3, X, 4), (X, 3)): -2,
                                                        ((R, X, 3, X, 4), (X, 4)): -2,
                                                        ((X, 3), (X, 4)): 1})}
    exp_reductions2 = {"reduction_reduction_x_1_x_2_reduction_x_3_x_4":
                           PolyBinary({((R, R, X, 1, X, 2, R, X, 3, X, 4),): 3,
                                       ((R, R, X, 1, X, 2, R, X, 3, X, 4), (R, X, 1, X, 2)): -2,
                                       ((R, R, X, 1, X, 2, R, X, 3, X, 4), (R, X, 3, X, 4)): -2,
                                       ((R, X, 1, X, 2), (R, X, 3, X, 4)): 1})}

    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{1: 1, 2: 1, 3: 1, 4: 1\}"):
        constraint = ConstraintBinary(PolyBinary({(1, 2, 3, 4): 1}), 1, 1)

    exp_penalty_terms = {NAME: PolyBinary({(): 1, ((R, R, X, 1, X, 2, R, X, 3, X, 4),): -1})}
    exp_penalty_terms.update(exp_reductions1)
    exp_penalty_terms.update(exp_reductions2)
    with pytest.warns() as record:
        assert constraint.get_penalty_terms(NAME) == exp_penalty_terms
    assert len(record) == 2
    assert str(record[0].message) == "Variables are replaced by tuple variables"
    assert str(record[1].message) == "Variables could be set in advance: " \
                                     "{('reduction', 'reduction', 'x', 1, 'x', 2, 'reduction', 'x', 3, 'x', 4): 1}"

    constraint = ConstraintBinary(PolyBinary({((X, 1), (X, 2), (X, 3), (X, 4)): 1, ((X, 1), (X, 2)): 1}), 1, 1)
    exp_penalty_terms = {NAME: PolyBinary({(): 1,
                                           ((R, R, X, 1, X, 2, R, X, 3, X, 4),): -1,
                                           ((R, X, 1, X, 2),): -1,
                                           ((R, R, X, 1, X, 2, R, X, 3, X, 4), (R, X, 1, X, 2)): 2})}
    exp_penalty_terms.update(exp_reductions1)
    exp_penalty_terms.update(exp_reductions2)

    warning_msg = r"The two variables '\('reduction', 'reduction', 'x', 1, 'x', 2, 'reduction', 'x', 3, 'x', 4\)' " \
                  r"and '\('reduction', 'x', 1, 'x', 2\)' are set to be " \
                  r"negations of each other, consider replacing one with '1 - other'"
    with pytest.warns(UserWarning, match=warning_msg):
        assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

    constraint = ConstraintBinary(PolyBinary({((X, 1), (X, 2), (X, 3), (X, 4)): 1, ((X, 1), (X, 2)): 1}), 0, 0)
    exp_penalty_terms = {NAME: PolyBinary({((R, X, 1, X, 2),): 1, ((R, X, 1, X, 2), (R, X, 3, X, 4)): 1})}
    exp_penalty_terms.update(exp_reductions1)
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('reduction', 'x', 1, 'x', 2\): 0\}"):
        assert constraint.get_penalty_terms(NAME) == exp_penalty_terms

def test_get_penalty_terms__special_constraints():
    """ test construction of objective terms for special constraints """
    reduction_constraint1 = ConstraintBinary(PolyBinary({'x': 1, 'r': -1}), 0, 1)
    exp_penalty_terms = {'constraint': PolyBinary({('r',): 1, ('r', 'x'): -1})}
    assert reduction_constraint1.get_penalty_terms() == exp_penalty_terms

    reduction_constraint1 = ConstraintBinary(PolyBinary({'a': -1, 'r': 1, (): 1}), 0, 1)
    exp_penalty_terms = {'constraint': PolyBinary({('r',): 1, ('a', 'r'): -1})}
    assert reduction_constraint1.get_penalty_terms() == exp_penalty_terms

    reduction_constraint2 = ConstraintBinary(PolyBinary({'a': -1, 'r': 1, 'x': -1, (): 1}), 0, 1)
    exp_penalty_terms = {'reduction': PolyBinary({('r',): 1, ('a', 'r'): -1, ('r', 'x'): -1, ('a', 'x'): 1})}
    assert reduction_constraint2.get_penalty_terms('reduction') == exp_penalty_terms

    reduction_constraint0 = ConstraintBinary(PolyBinary({('a', 'x'): -1, 'r': 1, 's': 0}), 0, 0)
    exp_penalty_terms = {'constraint': PolyBinary({('r',): 3, ('a', 'r'): -2, ('r', 'x'): -2, ('a', 'x'): 1})}
    assert reduction_constraint0.get_penalty_terms() == exp_penalty_terms

def test_check_validity():
    """ test validity check """
    constraint = ConstraintBinary(PolyBinary({'x': 1, 'r': -1}), 0, 1)
    assert constraint.check_validity({'r': 0, 'x': 1})
    assert not constraint.check_validity({'r': 1, 'x': -1})

def test_get_special_constraint_penalty_poly():
    """ test check for reduction constraint """
    # linear constraint with 2 variables, 2 permutations
    reduction_constraint_l2 = ConstraintBinary(PolyBinary({'x': 1, 'r': -1}), 0, 1)
    exp_poly = PolyBinary({('r',): 1, ('r', 'x'): -1})
    assert get_special_constraint_penalty_poly(reduction_constraint_l2) == exp_poly

    reduction_constraint_l2 = ConstraintBinary(PolyBinary({'a': -1, 'r': 1, (): 1}), 0, 1)
    exp_poly = PolyBinary({('r',): 1, ('a', 'r'): -1})
    assert get_special_constraint_penalty_poly(reduction_constraint_l2) == exp_poly

    # penalty constraint with 2 variables, 2 permutations
    reduction_constraint_l2 = ConstraintBinary(PolyBinary({'r': 1, ('x', 'r'): -1}), 0, 0)
    exp_poly = PolyBinary({('r',): 1, ('r', 'x'): -1})
    poly = get_special_constraint_penalty_poly(reduction_constraint_l2)
    assert poly == exp_poly

    reduction_constraint_l2 = ConstraintBinary(PolyBinary({('a', 'r'): 1, 'r': -1}), 0, 0)
    exp_poly = PolyBinary({('r',): 1, ('a', 'r'): -1})
    assert get_special_constraint_penalty_poly(reduction_constraint_l2) == exp_poly

    # linear constraint with 3 variables, 3 permutations, 1 shift
    reduction_constraint_l3 = ConstraintBinary(PolyBinary({'a': -1, 'r': 1, 'x': -1, (): 1}), 0, 1)
    exp_poly = PolyBinary({('r',): 1, ('a', 'r'): -1, ('r', 'x'): -1, ('a', 'x'): 1})
    assert get_special_constraint_penalty_poly(reduction_constraint_l3) == exp_poly

    reduction_constraint_l3 = ConstraintBinary(PolyBinary({'x': 1, 'y': 1, 'r': -1}), 0, 1)
    exp_penalty_poly = PolyBinary({('r',): 1, ('r', 'x'): -1, ('r', 'y'): -1, ('x', 'y'): 1})
    assert get_special_constraint_penalty_poly(reduction_constraint_l3) == exp_penalty_poly

    reduction_constraint_l3 = ConstraintBinary(PolyBinary({(1,): 1, (3,): 1, (2,): -1}), 0, 1)
    exp_penalty_poly = PolyBinary({(2,): 1, (2, 1): -1, (2, 3): -1, (1, 3): 1})
    assert get_special_constraint_penalty_poly(reduction_constraint_l3) == exp_penalty_poly

    reduction_constraint_l3 = ConstraintBinary(PolyBinary({(('x', 1),): 1,
                                                           (('x', 2),): 1,
                                                           (('x', 3),): -1,
                                                           (): 3}), 3, 4)
    exp_penalty_poly = PolyBinary({(('x', 3),): 1,
                                   (('x', 3), ('x', 1)): -1,
                                   (('x', 3), ('x', 2)): -1,
                                   (('x', 1), ('x', 2)): 1})
    assert get_special_constraint_penalty_poly(reduction_constraint_l3) == exp_penalty_poly

    # penalty constraint with 3 variables, 1 shift
    penalty_constraint_l3 = ConstraintBinary(exp_penalty_poly + 5, 5, 5)
    assert get_special_constraint_penalty_poly(penalty_constraint_l3) == exp_penalty_poly

    # full penalty constraint
    exp_penalty_poly = PolyBinary({(('x', 3),): 3,
                                   (('x', 3), ('x', 1)): -2,
                                   (('x', 3), ('x', 2)): -2,
                                   (('x', 1), ('x', 2)): 1})
    penalty_constraint_full = ConstraintBinary(exp_penalty_poly, 0, 0)
    assert get_special_constraint_penalty_poly(penalty_constraint_full) == exp_penalty_poly

    # quadratic constraint, 3 permutations, 1 shift
    reduction_constraint_q = ConstraintBinary(PolyBinary({('a', 'x'): -1, 'r': 1}), 0, 0)
    exp_poly = PolyBinary({('r',): 3, ('a', 'r'): -2, ('r', 'x'): -2, ('a', 'x'): 1})
    assert get_special_constraint_penalty_poly(reduction_constraint_q) == exp_poly

    reduction_constraint_q = ConstraintBinary(PolyBinary({(0, 1): -1, (2,): 1, (): -3}), -3, -3)
    exp_poly = PolyBinary({(2,): 3, (0, 2): -2, (2, 1): -2, (0, 1): 1})
    assert get_special_constraint_penalty_poly(reduction_constraint_q) == exp_poly

    reduction_constraint_q = ConstraintBinary(PolyBinary({(('x', 2), ('x', 1)): -1, (('x', 0),): 1}), 0, 0)
    exp_poly = PolyBinary({(('x', 0),): 3,
                           (('x', 2), ('x', 0)): -2,
                           (('x', 0), ('x', 1)): -2,
                           (('x', 1), ('x', 2)): 1})
    assert get_special_constraint_penalty_poly(reduction_constraint_q) == exp_poly

def test_to_equality_constraint():
    """ test the construction of the corresponding equality constraint """
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('x', 1\): 0, \('x', 2\): 0\}"):
        constraint = ConstraintBinary(LINEAR_POLY, 0, 0)
    assert constraint.to_equality_constraint() == constraint

    constraint = ConstraintBinary(LINEAR_POLY, 0, 1)
    exp_poly = LINEAR_POLY - PolyBinary({(("slack", 0),) : 1})
    exp_constraint = ConstraintBinary(exp_poly, 0, 0)
    assert constraint.to_equality_constraint() == exp_constraint

    constraint = ConstraintBinary(QUADRATIC_POLY, 0, 3)
    exp_poly = QUADRATIC_POLY - PolyBinary({(("other_slack", 0),) : 1, (("other_slack", 1),) : 2})
    exp_constraint = ConstraintBinary(exp_poly, 0, 0)
    assert constraint.to_equality_constraint("other_slack") == exp_constraint

def test_get_standard_penalty_polynomial():
    """ test the construction of the penalty term for linear constraint """
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('x', 1\): 0, \('x', 2\): 0\}"):
        constraint = ConstraintBinary(LINEAR_POLY, 0, 0)
    exp_poly = LINEAR_POLY ** 2
    assert get_standard_penalty_polynomial(constraint) == exp_poly

    constraint = ConstraintBinary(LINEAR_POLY, 0, 1)
    exp_poly = (LINEAR_POLY - PolyBinary({(("slack", 0),) : 1})) ** 2
    assert get_standard_penalty_polynomial(constraint) == exp_poly

    constraint = ConstraintBinary(QUADRATIC_POLY, 0, 1)
    exp_poly = PolyBinary({(): 9, (('slack', 0),): 7, (('x', 1),): 7, (('slack', 0), ('x', 1)): -14,
                           (('x', 1), ('x', 2)): 20, (('slack', 0), ('x', 1), ('x', 2)): -4})
    assert get_standard_penalty_polynomial(constraint) == exp_poly

def test_get_reduction_constraints():
    """ check the reduction constraints """
    exp_constraint1 = ConstraintBinary(PolyBinary({(('r', 2, 5),): -1, (('x', 2),): 1}), 0, 1)
    exp_constraint2 = ConstraintBinary(PolyBinary({(('r', 2, 5),): -1, (('x', 5),): 1}), 0, 1)
    exp_constraint3 = ConstraintBinary(PolyBinary({(('r', 2, 5),): -1, (('x', 2),): 1, (('x', 5),): 1}), 0, 1)
    exp_constraints = {"r_2_5_0": exp_constraint1, "r_2_5_1": exp_constraint2, "r_2_5_2": exp_constraint3}
    assert get_reduction_constraints(("r", 2, 5), ("x", 2), ("x", 5)) == exp_constraints

    exp_constraint = ConstraintBinary(PolyBinary({("r_2_5",): 1, ("x_2", "x_5"): -1}), 0, 0)
    exp_constraints = {"r_2_5": exp_constraint}
    assert get_reduction_constraints("r_2_5", "x_2", "x_5", max_degree=2) == exp_constraints

def test_get_all_reduction_penalty_terms():
    """ test the penalty terms from the reductions """
    reductions = [(('reduction', 'x', 1, 'x', 2), ('x', 1), ('x', 2)),
                  (('reduction', 'x', 2, 'x', 3), ('x', 2), ('x', 3)),
                  (('reduction', 'x', 3, 'reduction', 'x', 1, 'x', 2), ('x', 3), ('reduction', 'x', 1, 'x', 2)),
                  (('reduction', 'x', 4, 'reduction', 'x', 2, 'x', 3), ('x', 4), ('reduction', 'x', 2, 'x', 3))]
    exp_penalty_term1 = PolyBinary({(("reduction", "x", 1, "x", 2),): 3,
                                    (("reduction", "x", 1, "x", 2), ("x", 1)): -2,
                                    (("reduction", "x", 1, "x", 2), ("x", 2)): -2,
                                    (("x", 1), ("x", 2)): 1})
    exp_penalty_term2 = PolyBinary({(("reduction", "x", 2, "x", 3),): 3,
                                    (("reduction", "x", 2, "x", 3), ("x", 2)): -2,
                                    (("reduction", "x", 2, "x", 3), ("x", 3)): -2,
                                    (("x", 2), ("x", 3)): 1})
    exp_penalty_term3 = PolyBinary({(("reduction", "x", 3, "reduction", "x", 1, "x", 2),): 3,
                                    (("reduction", "x", 1, "x", 2),
                                     ("reduction", "x", 3, "reduction", "x", 1, "x", 2)): -2,
                                    (("reduction", "x", 1, "x", 2), ("x", 3)): 1,
                                    (("reduction", "x", 3, "reduction", "x", 1, "x", 2), ("x", 3)): -2})
    exp_penalty_term4 = PolyBinary({(("reduction", "x", 4, "reduction", "x", 2, "x", 3),): 3,
                                    (("reduction", "x", 2, "x", 3),
                                     ("reduction", "x", 4, "reduction", "x", 2, "x", 3)): -2,
                                    (("reduction", "x", 2, "x", 3), ("x", 4)): 1,
                                    (("reduction", "x", 4, "reduction", "x", 2, "x", 3), ("x", 4)): -2})
    exp_penalty_terms = {"reduction_x_1_x_2": exp_penalty_term1,
                         "reduction_x_2_x_3": exp_penalty_term2,
                         "reduction_x_3_reduction_x_1_x_2": exp_penalty_term3,
                         "reduction_x_4_reduction_x_2_x_3": exp_penalty_term4}
    assert get_all_reduction_penalty_terms(reductions) == exp_penalty_terms


## exhaustive tests for special constraints

VARS_STANDARD = ("x", 1), ("x", 2), ("reduction", "x", 1, "x", 2)
VARS_RESORTED_1 = ("a", 1), ("b", 2), ("reduction", "a", 1, "b", 2)
VARS_RESORTED_2 = ("a", 1), ("y", 2), ("reduction", "a", 1, "y", 2)


@pytest.fixture(params=[VARS_STANDARD, VARS_RESORTED_1, VARS_RESORTED_2],
                ids=["standard", "resorted_1", "resorted_2"],
                name="reduction_constraints")
def fixture_reduction_constraints(request):
    """ get test objects """
    # pylint: disable=too-many-locals
    x1, x2, r = request.param
    constraint_poly_lin2_1 = PolyBinary({(r,): 1, (x1,): -1, (): 1})
    constraint_poly_lin2_2 = PolyBinary({(r,): 1, (x2,): -1, (): 1})
    constraint_poly_lin3   = PolyBinary({(r,): 1, (x1,): -1, (x2,): -1, (): 1})
    constraint_poly_quad   = PolyBinary({(r,): 1, (x1, x2): -1})
    penalty_poly_lin2_1    = PolyBinary({(r,): 1, (r, x1): -1})
    penalty_poly_lin2_2    = PolyBinary({(r,): 1, (r, x2): -1})
    penalty_poly_lin3      = PolyBinary({(r,): 1, (r, x1): -1, (r, x2): -1, (x1, x2): 1})
    penalty_poly_full      = PolyBinary({(r,): 3, (r, x1): -2, (r, x2): -2, (x1, x2): 1})

    constraint_lin2_1         = ConstraintBinary(constraint_poly_lin2_1, 0, 1)
    constraint_lin2_2         = ConstraintBinary(constraint_poly_lin2_2, 0, 1)
    constraint_lin3           = ConstraintBinary(constraint_poly_lin3, 0, 1)
    constraint_quad           = ConstraintBinary(constraint_poly_quad, 0, 0)
    constraint_penalty_lin2_1 = ConstraintBinary(penalty_poly_lin2_1, 0, 0)
    constraint_penalty_lin2_2 = ConstraintBinary(penalty_poly_lin2_2, 0, 0)
    constraint_penalty_lin3   = ConstraintBinary(penalty_poly_lin3, 0, 0)
    constraint_penalty_full   = ConstraintBinary(penalty_poly_full, 0, 0)

    all_combinations =  [(constraint_lin2_1,         penalty_poly_lin2_1, False, (r, x1)),
                         (constraint_lin2_2,         penalty_poly_lin2_2, False, (r, x2)),
                         (constraint_lin3,           penalty_poly_lin3,   False, (r, x1, x2)),
                         (constraint_quad,           penalty_poly_full,   False, (r, x1, x2)),
                         (constraint_penalty_lin2_1, penalty_poly_lin2_1, True,  (r, x1)),
                         (constraint_penalty_lin2_2, penalty_poly_lin2_2, True,  (r, x2)),
                         (constraint_penalty_lin3,   penalty_poly_lin3,   True,  (r, x1, x2)),
                         (constraint_penalty_full,   penalty_poly_full,   True,  (r, x1, x2))]
    yield all_combinations

@pytest.fixture(params=range(8),
                ids=["lin2_1", "lin2_2", "lin3", "quad", "p_lin2_2", "p_lin2_2", "p_lin3", "p_full"],
                name="reduction_constraint__penalty_poly__is_penalty__reduction")
def fixture_reduction_constraint__penalty_poly__is_penalty__reduction(request, reduction_constraints):
    """ address each test object individually """
    yield reduction_constraints[request.param]


def test_provides_penalty_term_directly__reduction(reduction_constraint__penalty_poly__is_penalty__reduction):
    """ test check whether the polynomial of the constraint directly is a penalty term """
    constraint, _, provides_penalty_term, _ = reduction_constraint__penalty_poly__is_penalty__reduction
    if provides_penalty_term:
        assert constraint.provides_penalty_term_directly()
    else:
        assert not constraint.provides_penalty_term_directly()
    assert not constraint.provides_penalty_term_directly(max_degree=1)

def test_retrieve_reductions(reduction_constraint__penalty_poly__is_penalty__reduction):
    """ test retrieval of reductions from the constraint """
    constraint, _, _, exp_reduction = reduction_constraint__penalty_poly__is_penalty__reduction
    reductions = retrieve_reduction(constraint)
    assert reductions == exp_reduction

def test_get_reductions(reduction_constraint__penalty_poly__is_penalty__reduction):
    """ test getting the reductions from the constraint """
    constraint, _, provides_penalty_poly, exp_reduction = reduction_constraint__penalty_poly__is_penalty__reduction
    reduced_constraint, reductions = constraint.get_reductions(force=True)
    assert reduced_constraint is None
    assert reductions == [exp_reduction]

    exp_reductions_non_force = [] if provides_penalty_poly or constraint.polynomial.degree <= 1 else [exp_reduction]
    exp_constraint = constraint if provides_penalty_poly or constraint.polynomial.degree <= 1 else None
    reduced_constraint, reductions = constraint.get_reductions()
    assert reduced_constraint == exp_constraint
    assert reductions == exp_reductions_non_force

def test_matches_special_penalty_constraint__reduction(reduction_constraint__penalty_poly__is_penalty__reduction):
    """ test recognition of special constraints """
    constraint, _, provides_penalty_poly, _ = reduction_constraint__penalty_poly__is_penalty__reduction
    assert (provides_penalty_poly and matches_special_penalty_constraint(constraint)) \
           or (not provides_penalty_poly and not matches_special_penalty_constraint(constraint))

def test_get_special_constraint_penalty_poly__reduction(reduction_constraint__penalty_poly__is_penalty__reduction):
    """ test penalty polynomial of special constraint """
    constraint, exp_penalty_poly, _, _ = reduction_constraint__penalty_poly__is_penalty__reduction
    penalty_poly = get_special_constraint_penalty_poly(constraint)
    assert penalty_poly == exp_penalty_poly
