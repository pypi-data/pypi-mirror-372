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

""" test binary polynomial module """

import pytest
import numpy as np

from quark import Polynomial, PolyBinary, PolyIsing
from quark.poly_binary import get_binary_representation_polynomial, get_unary_representation_polynomial, MEDIUM, \
                              BETTER, STRAIGHT


X, Y, R = "x", "y", "reduction"

P1_DICT = {(1,): 5, (2,): 6, (1, 3): -3, (2, 4): 3, (4,): -1, (): 3}
P2_DICT = {((X, 1), (Y, 2, 3)): -2, ((Y, 1, 2),): 3}
P3_DICT = {(0,): 5, (1, 1): 6, (2, 0): -3, (1, 3): 0.5, (3,): -1, (0, 1): 0.9, (): 16, (2,): 0}
P1_ISING_DICT = {(): 8.0, (1,): 1.75, (1, 3): -0.75, (2,): 3.75, (2, 4): 0.75, (3,): -0.75, (4,): 0.25}
P1_ISING_INV_DICT = {(): 8.0, (1,): -1.75, (1, 3): -0.75, (2,): -3.75, (2, 4): 0.75, (3,): 0.75, (4,): -0.25}

POLY1 = PolyBinary(P1_DICT)
POLY2 = PolyBinary(P2_DICT)
POLY3 = PolyBinary(P3_DICT)
POLY1_NONE = Polynomial(P1_DICT)
POLY1_ISING = PolyIsing(P1_ISING_DICT)
POLY1_ISING_INV = PolyIsing(P1_ISING_INV_DICT, inverted=True)

POLY3_QUADRATIC = [[ 5. ,  0.9, -3. ,  0. ],
                   [ 0. ,  6. ,  0. ,  0.5],
                   [ 0. ,  0. ,  0. ,  0. ],
                   [ 0. ,  0. ,  0. , -1. ]]
POLY3_LINEAR = [ 5.,  6.,  0., -1.]
POLY3_QUAD_NO_DIAG = [[ 0. ,  0.9, -3. ,  0. ],
                      [ 0. ,  0. ,  0. ,  0.5],
                      [ 0. ,  0. ,  0. ,  0. ],
                      [ 0. ,  0. ,  0. ,  0. ]]

QUADRATIC_POLY = PolyBinary({((X, 1),): 7, ((X, 2), (X, 1)): 2, (): 3})
LINEAR_POLY = PolyBinary({((X, 1),): 7, ((X, 2),): 2})

FROM_RIGHT_WARNING = "PolyBinary will be cast to Polynomial when added or multiplied from the right"


def test_init():
    """ test creation """
    poly = PolyBinary({(1, 1, 1): 5, (2,): 9, (2, 2) : -3, (3, 3, 1): -3, (2, 4): 3, (4,): -1, (): 3})
    assert POLY1 == poly
    assert P1_DICT == dict(poly)

    poly = PolyBinary({((Y, 2, 3), (X, 1), (Y, 2, 3), (Y, 2, 3)): -2, ((Y, 1, 2),): 3})
    assert POLY2 == poly
    assert P2_DICT == dict(poly)

def test_repr():
    """ test string representation """
    assert repr(POLY1) == "PolyBinary({(): 3, (1,): 5, (2,): 6, (4,): -1, (1, 3): -3, (2, 4): 3})"

def test_str():
    """ test string representation """
    assert str(POLY1) == "+3 +5 x1 +6 x2 -1 x4 -3 x1 x3 +3 x2 x4"

def test_add():
    """ test addition """
    # pylint: disable=unidiomatic-typecheck
    sum_poly = PolyBinary(P1_DICT)
    sum_poly += Polynomial({(0,) : 1})
    assert type(POLY1 + Polynomial({(0,) : 1})) is PolyBinary
    assert type(sum_poly) is PolyBinary

    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        sum_poly = Polynomial({(4,): 1}) + POLY1
        assert type(sum_poly) is Polynomial

    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        sum_poly = Polynomial({(4,): 1})
        sum_poly += POLY1
        assert type(sum_poly) is Polynomial

    with pytest.raises(ValueError, match="Cannot add PolyBinary and PolyIsing"):
        _ = POLY1 + PolyIsing(P1_DICT)

def test_mul():
    """ test multiplication """
    # pylint: disable=unidiomatic-typecheck
    exp_poly = PolyBinary({(1, 4): 5, (2, 4): 9, (1, 3, 4): -3, (4,): 2})
    prod_poly = POLY1 * PolyBinary({(4,): 1})
    assert prod_poly == exp_poly

    exp_poly = PolyBinary({((X, 1), (Y, 2, 3)): -4, ((X, 1), (Y, 1, 2)): 6})
    prod_poly = POLY2 * PolyBinary({((X, 1),): 2})
    assert prod_poly == exp_poly

    exp_poly = PolyBinary({((X, 1), (Y, 2, 3)): 4, ((Y, 1, 2),): 9, ((X, 1), (Y, 2, 3), (Y, 1, 2)) : -12})
    prod_poly = POLY2 * POLY2
    assert prod_poly == exp_poly

    prod_poly = PolyBinary(P1_DICT)
    prod_poly *= Polynomial({(0,) : 1})
    assert type(POLY1 * Polynomial({(0,) : 1})) is PolyBinary
    assert type(prod_poly) is PolyBinary

    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        prod_poly = Polynomial({(4,): 1}) * POLY1
        assert type(prod_poly) is Polynomial

    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        prod_poly = Polynomial({(4,): 1})
        prod_poly *= POLY1
        assert type(prod_poly) is Polynomial

    with pytest.raises(ValueError, match="Cannot multiply PolyBinary and PolyIsing"):
        _ = POLY1 * PolyIsing(P1_DICT)

def test_copy():
    """ test copying """
    # pylint: disable=unidiomatic-typecheck
    poly1_copy = POLY1.copy()
    assert poly1_copy == POLY1
    assert dict(poly1_copy) == dict(POLY1)
    assert type(poly1_copy) is PolyBinary

    p2_copy = POLY2.copy()
    assert p2_copy == POLY2
    assert dict(p2_copy) == dict(POLY2)
    assert type(poly1_copy) is PolyBinary

def test_remove_zero_coefficients():
    """ test the removal of monomials with zero coefficient """
    # pylint: disable=unidiomatic-typecheck
    poly_with_zero = {(3,): 0, (2,3): 0}
    poly_with_zero.update(P1_DICT)
    poly = PolyBinary(poly_with_zero)
    assert poly == POLY1
    assert dict(poly) != dict(POLY1)

    poly_nonzero = poly.remove_zero_coefficients()
    assert poly_nonzero == POLY1
    assert dict(poly_nonzero) == dict(POLY1)
    assert type(poly_nonzero) is PolyBinary

def test_preprocess_minimize():
    """ test preprocessing """
    exp_poly = PolyBinary({(): 2})
    exp_variables = {1 : 0, 2 : 0, 3 : 1, 4 : 1}
    preprocessed_poly, preprocessed_variables = POLY1.preprocess_minimize()
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables
    preprocessed_poly, preprocessed_variables = POLY1.preprocess_minimize(unambitious=True)
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables

    exp_poly = PolyBinary({(): -2})
    exp_variables = {(X, 1) : 1, (Y, 2, 3) : 1, (Y, 1, 2) : 0}
    preprocessed_poly, preprocessed_variables = POLY2.preprocess_minimize()
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables
    preprocessed_poly, preprocessed_variables = POLY2.preprocess_minimize(unambitious=True)
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables

    poly = PolyBinary({(0,): 10, (1,): 2, (2,): -8, (3,): 10, (4,): -7, (5,): 4, (0, 1): 2, (0, 2): -10, (0, 3): -10,
                       (1, 3): -8, (1, 4): -7, (2, 3): 8, (2, 5): 1, (3, 5): 2})
    exp_variables = {0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 0}
    preprocessed_poly, preprocessed_variables = poly.preprocess_minimize()
    assert preprocessed_poly == -20
    assert preprocessed_variables == exp_variables

    exp_variables = {1: 1, 2: 1, 4: 1, 5: 0}
    exp_poly = PolyBinary({(): -20, (0,): 2, (3,): 10, (0, 3): -10})
    preprocessed_poly, preprocessed_variables = poly.preprocess_minimize(unambitious=True)
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables

def test_to_ising():
    """ test conversion to Ising polynomials """
    poly_binary = PolyBinary.read_from_string("5 x1 + 6 x2 + 3 x1 x3 - x4 - 3 x2 x4 + 3")
    exp_poly_ising = 0.25 * PolyIsing.read_from_string("32 + 13 x1 + 9 x2 + 3 x3 - 5 x4 + 3 x1 x3 - 3 x2 x4")
    exp_poly_ising_inv = 0.25 * Polynomial.read_from_string("32 - 13 x1 - 9 x2 - 3 x3 + 5 x4 + 3 x1 x3 - 3 x2 x4")
    assert poly_binary.to_ising() == exp_poly_ising
    assert poly_binary.to_ising(inverted=True) == exp_poly_ising_inv

    exp_poly_ising = PolyIsing({(): 8.0, (1,): 1.75, (1, 3): -0.75, (2,): 3.75, (2, 4): 0.75, (3,): -0.75, (4,): 0.25})
    exp_poly_ising_inv = exp_poly_ising.invert()
    assert POLY1.to_ising() == exp_poly_ising
    assert POLY1.to_ising(inverted=True) == exp_poly_ising_inv

    exp_poly_ising = PolyIsing({(): 1.0, ((X, 1),): -0.5, ((Y, 1, 2),): 1.5, ((Y, 2, 3),): -0.5,
                                ((X, 1), (Y, 2, 3)): -0.5})
    exp_poly_ising_inv = exp_poly_ising.invert()
    assert POLY2.to_ising() == exp_poly_ising
    assert POLY2.to_ising(inverted=True) == exp_poly_ising_inv

def test_unknown_poly_to_binary():
    """ test conversion to binary polynomial """
    assert PolyBinary.from_unknown_poly(POLY1) == POLY1

    poly = PolyBinary.from_unknown_poly(POLY1_NONE)
    assert poly == POLY1_NONE
    assert isinstance(poly, PolyBinary)

    assert PolyBinary.from_unknown_poly(POLY1_ISING) == POLY1
    assert PolyBinary.from_unknown_poly(POLY1_ISING_INV) == POLY1

def test_affine_transform():
    """ test affine transformation """
    # pylint: disable=unidiomatic-typecheck
    exp_poly = Polynomial({(4,) : 33, () : 43, (2, 4) : 27, (2,) : 54, (1, 3) : -27, (1,) : -21, (3,) : -36})
    transformed_poly = POLY1.affine_transform(3, 4)
    assert transformed_poly == exp_poly
    assert type(transformed_poly) is Polynomial

def test_evaluate():
    """ test evaluation """
    # pylint: disable=unidiomatic-typecheck
    var_assignment = {(X, 1): -1, (Y, 2, 3): 1}
    evaluated_poly = POLY2.evaluate(var_assignment)
    exp_poly = PolyBinary({(): 2, ((Y, 1, 2),): 3})
    assert evaluated_poly == exp_poly
    assert type(evaluated_poly) is PolyBinary

    var_assignment = {(X, 1) : 0, (Y, 2, 3) : 1, (Y, 1, 2) : 0}
    evaluated_poly = POLY2.evaluate(var_assignment)
    assert evaluated_poly == 0

    with pytest.raises(ValueError, match="Can only assign numbers or polynomials"):
        var_assignment = {(X, 1): PolyBinary({((X, 1),): 2, (): 3})}
        POLY2.evaluate(var_assignment)

    var_assignment = {(X, 1): Polynomial({((X, 1),): 2, (): 3})}
    exp_poly = Polynomial({((X, 1), (Y, 2, 3)): -4, ((Y, 1, 2),): 3, ((Y, 2, 3),): -6})
    evaluated_poly = POLY2.evaluate(var_assignment)
    assert type(evaluated_poly) is Polynomial
    assert evaluated_poly == exp_poly

def test_replace_variables():
    """ test replacement of variables in polynomials """
    # pylint: disable=unidiomatic-typecheck
    replacement = {(X, 1) : "a", (Y, 2, 3) : "b", (Y, 1, 2) : "c"}
    exp_poly = PolyBinary({("a", "b"): -2, ("c",): 3})
    replaced_poly = POLY2.replace_variables(replacement)
    assert replaced_poly == exp_poly
    assert type(replaced_poly) is PolyBinary

def test_get_rounded():
    """ test rounding of polynomials """
    # pylint: disable=unidiomatic-typecheck
    poly = PolyBinary({((X, 1), (Y, 2, 3)): -2.3, ((Y, 1, 2),): 2.9})
    rounded_poly = poly.round(0)
    assert rounded_poly == POLY2
    assert type(rounded_poly) is PolyBinary

def test_get_matrix_representation():
    """ test standard matrix representation """
    with pytest.warns(UserWarning, match="Constant offset of 16 is dropped"):
        quadratic = POLY3.get_matrix_representation()
    assert np.array_equal(quadratic, POLY3_QUADRATIC)

def test_get_from_matrix_representation():
    """ test conversion from matrix representation """
    poly = PolyBinary.get_from_matrix_representation(POLY3_QUADRATIC)
    assert poly == POLY3 - 16

    poly = PolyBinary.get_from_matrix_representation(POLY3_LINEAR, POLY3_QUAD_NO_DIAG)
    assert poly == POLY3 - 16

def test_reduce():
    """ test reduction of polynomial """
    qubic = PolyBinary({(1, 2, 3): 1, (2, 3, 4): 2})
    exp_reduced_poly = PolyBinary({((R, X, 3, R, X, 1, X, 2),): 1,
                                   ((R, X, 4, R, X, 2, X, 3),): 2})
    exp_reductions = [((R, X, 1, X, 2), (X, 1), (X, 2)),
                      ((R, X, 2, X, 3), (X, 2), (X, 3)),
                      ((R, X, 3, R, X, 1, X, 2), (X, 3), (R, X, 1, X, 2)),
                      ((R, X, 4, R, X, 2, X, 3), (X, 4), (R, X, 2, X, 3))]

    with pytest.warns(UserWarning, match="Variables are replaced by tuple variables"):
        reduced_poly, reductions = qubic.reduce(reduction_variable_prefix=R)
    assert reduced_poly.degree == 1
    assert reduced_poly == exp_reduced_poly
    assert reductions == exp_reductions

    exp_reduced_poly = PolyBinary({((R, X, 1, X, 2), (X, 3)): 1,
                                   ((R, X, 2, X, 3), (X, 4)): 2})
    exp_reductions = [((R, X, 1, X, 2), (X, 1), (X, 2)),
                      ((R, X, 2, X, 3), (X, 2), (X, 3))]

    with pytest.warns(UserWarning, match="Variables are replaced by tuple variables"):
        reduced_poly, reductions = qubic.reduce(max_degree=2)
    assert reduced_poly.degree == 2
    assert reduced_poly == exp_reduced_poly
    assert reductions == exp_reductions

    use = {((R, X, 2, X, 3), (X, 2), (X, 3))}
    exp_reduced_poly = PolyBinary({((R, X, 2, X, 3), (X, 1)): 1,
                                   ((R, X, 2, X, 3), (X, 4)): 2})
    with pytest.warns(UserWarning, match="Variables are replaced by tuple variables"):
        reduced_poly, reductions = qubic.reduce(max_degree=2, use=use)
    assert reduced_poly.degree == 2
    assert reduced_poly == exp_reduced_poly
    assert not reductions

    use = [(10, 2, 3)]
    exp_reduced_poly = PolyBinary({(10, 1): 1, (10, 4): 2})
    reduced_poly, reductions = qubic.reduce(max_degree=2, use=use)
    assert reduced_poly.degree == 2
    assert reduced_poly == exp_reduced_poly
    assert not reductions

    reduced_poly, reductions = qubic.reduce(max_degree=3)
    assert reduced_poly.degree == 3
    assert reduced_poly == qubic
    assert not reductions

    with pytest.raises(ValueError, match="Unknown strategy 'sth_else'"):
        with pytest.warns(UserWarning, match="Variables are replaced by tuple variables"):
            qubic.reduce(reduction_strategy="sth_else")

    with pytest.raises(ValueError, match="Provide integer max_degree larger than 0 or set to None"):
        qubic.reduce(max_degree=0)

def test_reduce_options():
    """ test reduction of polynomial with different options to choose the next variable pair to be replaced """
    poly = PolyBinary({(1, 2, 3, 4): 1, (2, 3, 4, 5): 2, (3, 4): 3})

    exp_poly3 = PolyBinary({((X, 3), (X, 4)): 3,
                            ((R, X, 1, X, 2), (X, 3), (X, 4)): 1,
                            ((R, X, 2, X, 3), (X, 4), (X, 5)): 2})
    exp_reductions3 = [((R, X, 1, X, 2), (X, 1), (X, 2)),
                       ((R, X, 2, X, 3), (X, 2), (X, 3))]
    exp_poly2 = PolyBinary({((R, X, 3, X, 4),): 3,
                            ((R, X, 1, X, 2), (R, X, 3, X, 4)): 1,
                            ((R, X, 2, X, 5), (R, X, 3, X, 4)): 2})
    exp_reductions2 = [((R, X, 1, X, 2), (X, 1), (X, 2)),
                       ((R, X, 2, X, 5), (X, 2), (X, 5)),
                       ((R, X, 3, X, 4), (X, 3), (X, 4))]

    _check_reductions(STRAIGHT, exp_poly2, exp_poly3, exp_reductions2, exp_reductions3, poly)

    exp_poly3 = PolyBinary({((R, X, 2, X, 3), (X, 1), (X, 4)): 1,
                            ((R, X, 2, X, 3), (X, 4), (X, 5)): 2,
                            ((X, 3), (X, 4)): 3})
    exp_reductions3 = [((R, X, 2, X, 3), (X, 2), (X, 3))]
    exp_poly2 = PolyBinary({((R, X, 4, R, X, 2, X, 3), (X, 1)): 1,
                            ((R, X, 4, R, X, 2, X, 3), (X, 5)): 2,
                            ((X, 3), (X, 4)): 3})
    exp_reductions2 = [((R, X, 2, X, 3), (X, 2), (X, 3)),
                       ((R, X, 4, R, X, 2, X, 3), (X, 4), (R, X, 2, X, 3))]

    _check_reductions(MEDIUM, exp_poly2, exp_poly3, exp_reductions2, exp_reductions3, poly)

    exp_poly3 = PolyBinary({((R, X, 3, X, 4),): 3,
                             ((R, X, 3, X, 4), (X, 1), (X, 2)): 1,
                             ((R, X, 3, X, 4), (X, 2), (X, 5)): 2})
    exp_reductions3 = [((R, X, 3, X, 4), (X, 3), (X, 4))]
    exp_poly2 = PolyBinary({((R, X, 3, X, 4),): 3,
                            ((R, X, 2, R, X, 3, X, 4), (X, 1)): 1,
                            ((R, X, 2, R, X, 3, X, 4), (X, 5)): 2})
    exp_reductions2 = [((R, X, 2, R, X, 3, X, 4), (X, 2), (R, X, 3, X, 4)),
                       ((R, X, 3, X, 4), (X, 3), (X, 4))]

    _check_reductions(BETTER, exp_poly2, exp_poly3, exp_reductions2, exp_reductions3, poly)

def _check_reductions(reduction_strategy, exp_poly2, exp_poly3, exp_reductions2, exp_reductions3, poly):
    with pytest.warns(UserWarning, match="Variables are replaced by tuple variables"):
        reduced_poly3, reductions3 = poly.reduce(max_degree=3, reduction_strategy=reduction_strategy)
        reduced_poly2, reductions2 = poly.reduce(max_degree=2, reduction_strategy=reduction_strategy)
    assert reduced_poly3.degree == 3
    assert reduced_poly3 == exp_poly3
    assert reductions3 == exp_reductions3
    assert reduced_poly2.degree == 2
    assert reduced_poly2 == exp_poly2
    assert reductions2 == exp_reductions2


def test_reduce_quadratic_to_linear_polynomial():
    """ test reduction to quadratic polynomial """
    exp_poly = PolyBinary({((R, X, 1, X, 2),): 2, ((X, 1),): 7, (): 3})
    exp_reductions = [((R, X, 1, X, 2), (X, 1), (X, 2))]
    reduced_poly, reductions = QUADRATIC_POLY.reduce()
    assert reduced_poly == exp_poly
    assert reductions == exp_reductions

    flat_poly = PolyBinary({(2, 1): 2, (1,): 7, (): 3})
    with pytest.warns(UserWarning, match="Variables are replaced by tuple variables"):
        reduced_poly, reductions = flat_poly.reduce()
    assert reduced_poly == exp_poly
    assert reductions == exp_reductions

    reduced_poly, reductions = LINEAR_POLY.reduce()
    assert reduced_poly == LINEAR_POLY
    assert not reductions

def test_get_binary_representation_polynomial():
    """ test construction of binary representation polynomial """
    poly = get_binary_representation_polynomial(0)
    exp_poly = PolyBinary()
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(1)
    exp_poly = PolyBinary({((X, 0),): 1})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(2)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 1})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(3)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 2})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(4)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 2, ((X, 2),): 1})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(5, 1)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 2, ((X, 2),): 1, (): 1})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(5, -1)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 2, ((X, 2),): 3, (): -1})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(5, -2, split_signs=True)
    exp_poly = PolyBinary({((X, "+", 0),): 1, ((X, "+", 1),): 2, ((X, "+", 2),): 2,
                           ((X, "-", 0),): -1, ((X, "-", 1),): -1})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(-2, -7)
    exp_poly = PolyBinary({((X, 0),): -1, ((X, 1),): -2, ((X, 2),): -2, (): -2})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(num_variables=3)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 2, ((X, 2),): 4})
    assert poly == exp_poly

    poly = get_binary_representation_polynomial(7, variable_prefix="slack")
    exp_poly = PolyBinary({(("slack", 0),): 1, (("slack", 1),): 2, (("slack", 2),): 4})
    assert poly == exp_poly

    with pytest.raises(ValueError, match="Either provide upper_bound or num_variables"):
        get_binary_representation_polynomial()

    with pytest.warns(UserWarning, match="With upper_bound given, num_variables is ignored"):
        get_binary_representation_polynomial(7, 3, 3)

    with pytest.raises(ValueError, match="Upper bound needs to be larger than or equal to lower bound"):
        get_binary_representation_polynomial(-7)

def test_get_unary_representation_polynomial():
    """ test construction of unary representation polynomial """
    poly = get_unary_representation_polynomial(0)
    exp_poly = PolyBinary()
    assert poly == exp_poly

    poly = get_unary_representation_polynomial(1)
    exp_poly = PolyBinary({((X, 0),): 1})
    assert poly == exp_poly

    poly = get_unary_representation_polynomial(2)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 1})
    assert poly == exp_poly

    poly = get_unary_representation_polynomial(3)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 1, ((X, 2),): 1})
    assert poly == exp_poly

    poly = get_unary_representation_polynomial(4, 1)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 1, ((X, 2),): 1, (): 1})
    assert poly == exp_poly

    poly = get_unary_representation_polynomial(3, -1)
    exp_poly = PolyBinary({((X, 0),): 1, ((X, 1),): 1, ((X, 2),): 1, ((X, 3),): 1, (): -1})
    assert poly == exp_poly

    poly = get_unary_representation_polynomial(-2, -5)
    exp_poly = PolyBinary({((X, 0),): -1, ((X, 1),): -1, ((X, 2),): -1, (): -2})
    assert poly == exp_poly

    poly = get_unary_representation_polynomial(3, variable_prefix="slack")
    exp_poly = PolyBinary({(("slack", 0),): 1, (("slack", 1),): 1, (("slack", 2),): 1})
    assert poly == exp_poly

    with pytest.raises(ValueError, match="Upper bound needs to be larger than or equal to lower bound"):
        get_unary_representation_polynomial(-7)

def test_positive_negative():
    """ test positive and negative part """
    exp_positive = PolyBinary({(1,): 5, (2,): 6, (2, 4): 3})
    exp_negative = PolyBinary({(1, 3): -3, (4,): -1})
    assert POLY1.positive == exp_positive
    assert POLY1.negative == exp_negative

def test_naive_upper_bound():
    """ test upper bound """
    assert POLY1.naive_upper_bound == 17
    assert POLY2.naive_upper_bound == 3

def test_naive_lower_bound():
    """ test lower bound"""
    assert POLY1.naive_lower_bound == -1
    assert POLY2.naive_lower_bound == -2
