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

""" test ising polynomial module """

import pytest
import numpy as np

from quark import PolyIsing, PolyBinary, Polynomial


X, Y = "x", "y"

P1_DICT = {(1,): 5, (2,): 6, (1, 3): -3, (2, 4): 3, (4,): -1, (): 3}
P2_DICT = {((X, 1), (Y, 2, 3)): -2, ((Y, 1, 2),): 3}
P3_DICT = {(0,): 5, (1,): 6, (2, 0): -3, (1, 3): 0.5, (3,): -1, (0, 1): 0.9, (): 16, (2,): 0}
P1_INV_DICT = {(1,): -5, (2,): -6, (1, 3): -3, (2, 4): 3, (4,): 1, (): 3}
P1_BINARY_DICT = {(): -7, (1,): 16, (2,): 6, (3,): 6, (4,): -8, (1, 3): -12, (2, 4): 12}

POLY1 = PolyIsing(P1_DICT)
POLY2 = PolyIsing(P2_DICT, inverted=True)
POLY3 = PolyIsing(P3_DICT)
POLY1_INV = PolyIsing(P1_INV_DICT, inverted=True)
POLY1_NONE = Polynomial(P1_DICT)
POLY1_BINARY = PolyBinary(P1_BINARY_DICT)

POLY3_LINEAR = [ 5.,  6.,  0., -1.]
POLY3_QUADRATIC = [[ 0. ,  0.9, -3. ,  0. ],
                   [ 0. ,  0. ,  0. ,  0.5],
                   [ 0. ,  0. ,  0. ,  0. ],
                   [ 0. ,  0. ,  0. ,  0. ]]
POLY3_QUAD_DIAG = [[ 5. ,  0.9, -3. ,  0. ],
                   [ 0. ,  6. ,  0. ,  0.5],
                   [ 0. ,  0. ,  0. ,  0. ],
                   [ 0. ,  0. ,  0. , -1. ]]

FROM_RIGHT_WARNING = "PolyIsing will be cast to Polynomial when added or multiplied from the right"


def check_polys_ising(received, expected):
    """ check inverted Ising polynomials """
    # pylint: disable=unidiomatic-typecheck
    assert type(received) is PolyIsing
    assert received == expected
    assert received.is_inverted() == expected.is_inverted()


def test_init():
    """ test initialization """
    poly = PolyIsing({(1, 1, 1): 5, (2, 4, 4, 4, 4): 6, (3, 1): -3, (2, 4): 3, (4,): -1, (2, 2): 3})
    assert POLY1 == poly
    assert P1_DICT == dict(poly)

    poly = PolyIsing({((Y, 2, 3), (X, 1), (Y, 2, 3), (Y, 2, 3)): -2, ((Y, 1, 2),): 3}, inverted=True)
    assert POLY2 == poly
    assert P2_DICT == dict(poly)

def test_repr():
    """ test string representation """
    assert repr(POLY1) == "PolyIsing({(): 3, (1,): 5, (2,): 6, (4,): -1, (1, 3): -3, (2, 4): 3})"
    assert repr(POLY1_INV) == "PolyIsing({(): 3, (1,): -5, (2,): -6, (4,): 1, (1, 3): -3, (2, 4): 3})"

def test_str():
    """ test string representation """
    assert str(POLY1) == '+3 +5 s1 +6 s2 -1 s4 -3 s1 s3 +3 s2 s4'

def test_not_eq():
    """ test unequal """
    assert POLY1 != "nonsense"
    assert POLY1 != PolyBinary(P1_DICT)
    assert PolyBinary(P1_DICT) != POLY1

def test_invert():
    """ test inversion """
    # pylint: disable=protected-access
    exp_poly = PolyIsing({(1,): -5, (2,): -6, (1, 3): -3, (2, 4): 3, (4,): 1, (): 3}, inverted=True)
    inverted_poly = POLY1.invert()
    assert inverted_poly == exp_poly
    assert inverted_poly._inverted
    assert inverted_poly.is_inverted()

    exp_poly = PolyIsing({((X, 1), (Y, 2, 3)): -2, ((Y, 1, 2),): -3})
    inverted_poly = PolyIsing(P2_DICT, inverted=True).invert()
    assert inverted_poly == exp_poly
    assert not inverted_poly._inverted
    assert not inverted_poly.is_inverted()

def test_add():
    """ test addition """
    # pylint: disable=unidiomatic-typecheck
    exp_poly = PolyIsing({(1,): 5, (2,): 6, (1, 3): -3, (2, 4): 3, (4,): -1, (): 4})
    sum_poly = PolyIsing(P1_DICT)
    sum_poly += 1
    check_polys_ising(sum_poly, exp_poly)
    check_polys_ising(POLY1 + 1, exp_poly)
    check_polys_ising(1 + POLY1, exp_poly)

    exp_poly = PolyIsing({(1,): 5, (2,): 6, (1, 3): -3, (2, 4): 3, (): 3})
    sum_poly = PolyIsing(P1_DICT)
    sum_poly += PolyIsing({(4,): 1})
    check_polys_ising(sum_poly, exp_poly)
    check_polys_ising(POLY1 + PolyIsing({(4,): 1}), exp_poly)
    check_polys_ising(PolyIsing({(4,): 1}) + POLY1, exp_poly)

    sum_poly = PolyIsing(P1_DICT)
    sum_poly += Polynomial({(4,): 1})
    check_polys_ising(sum_poly, exp_poly)
    check_polys_ising(POLY1 + Polynomial({(4,): 1}), exp_poly)

    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        sum_poly = Polynomial({(4,): 1}) + POLY1
        assert sum_poly == exp_poly
        assert type(sum_poly) is Polynomial

    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        sum_poly = Polynomial({(4,): 1})
        sum_poly += POLY1
        assert sum_poly == exp_poly
        assert type(sum_poly) is Polynomial

    with pytest.raises(ValueError, match="Cannot add two PolyIsings with different inversions"):
        _ = PolyIsing(P1_DICT, inverted=True) + POLY1
    with pytest.raises(ValueError, match="Cannot add two PolyIsings with different inversions"):
        _ = POLY1 + PolyIsing(P1_DICT, inverted=True)
    with pytest.raises(ValueError, match="Cannot add PolyIsing and PolyBinary"):
        _ = POLY1 + PolyBinary(P1_DICT)

def test_mul():
    """ test multiplication """
    # pylint: disable=unidiomatic-typecheck
    exp_poly = PolyIsing({(1, 4): 5, (2, 4): 6, (1, 3, 4): -3, (2,): 3, (): -1, (4,): 3})
    prod_poly = PolyIsing(P1_DICT)
    prod_poly *= PolyIsing({(4,): 1})
    check_polys_ising(prod_poly, exp_poly)
    check_polys_ising(POLY1 * PolyIsing({(4,): 1}), exp_poly)
    check_polys_ising(PolyIsing({(4,): 1}) * POLY1, exp_poly)

    exp_poly = PolyIsing({((X, 1), (Y, 2, 3), (Y, 1, 2)): -12, (): 13}, inverted=True)
    prod_poly = POLY2 * POLY2
    check_polys_ising(prod_poly, exp_poly)

    factor_poly = PolyIsing({((X, 1),): 2}, inverted=True)
    exp_poly = PolyIsing({((Y, 2, 3),): -4, ((X, 1), (Y, 1, 2)): 6}, inverted=True)
    prod_poly = PolyIsing(P2_DICT, inverted=True)
    prod_poly *= factor_poly
    check_polys_ising(prod_poly, exp_poly)
    check_polys_ising(POLY2 * factor_poly, exp_poly)
    check_polys_ising(factor_poly * POLY2, exp_poly)

    prod_poly = PolyIsing(P2_DICT, inverted=True)
    prod_poly *= factor_poly
    check_polys_ising(prod_poly, exp_poly)
    check_polys_ising(POLY2 * factor_poly, exp_poly)

    exp_poly = Polynomial({((Y, 2, 3), (X, 1), (X, 1)): -4, ((X, 1), (Y, 1, 2)): 6})
    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        prod_poly = Polynomial({((X, 1),): 2}) * POLY2
        assert prod_poly == exp_poly
        assert type(prod_poly) is Polynomial

    with pytest.warns(UserWarning, match=FROM_RIGHT_WARNING):
        prod_poly = Polynomial({((X, 1),): 2})
        prod_poly *= POLY2
        assert prod_poly == exp_poly
        assert type(prod_poly) is Polynomial

    with pytest.raises(ValueError, match="Cannot multiply two PolyIsings with different inversions"):
        _ = PolyIsing(P2_DICT, inverted=False) * POLY2

    with pytest.raises(ValueError, match="Cannot multiply two PolyIsings with different inversions"):
        _ = POLY2 * PolyIsing(P2_DICT, inverted=False)

    with pytest.raises(ValueError, match="Cannot multiply PolyIsing and PolyBinary"):
        _ = POLY2 * PolyBinary(P2_DICT)

def test_copy():
    """ test copying """
    # pylint: disable=unidiomatic-typecheck
    poly1_copy = POLY1.copy()
    assert poly1_copy == POLY1
    assert dict(poly1_copy) == dict(POLY1)
    assert poly1_copy.is_inverted() == POLY1.is_inverted()
    assert type(poly1_copy) is PolyIsing

    poly2_copy = POLY2.copy()
    assert poly2_copy == POLY2
    assert dict(poly2_copy) == dict(POLY2)
    assert poly2_copy.is_inverted() == POLY2.is_inverted()
    assert type(poly1_copy) is PolyIsing

def test_remove_zero_coefficients():
    """ test removal of monomials with zero coefficients """
    # pylint: disable=unidiomatic-typecheck
    poly_with_zero = {(3,): 0, (2, 3): 0}
    poly_with_zero.update(P1_DICT)
    poly = PolyIsing(poly_with_zero)
    assert dict(poly) != dict(POLY1)
    assert poly == POLY1

    poly_nonzero = poly.remove_zero_coefficients()
    assert poly_nonzero == POLY1
    assert dict(poly_nonzero) == dict(POLY1)
    assert type(poly_nonzero) is PolyIsing

def test_preprocess_minimize():
    """ test preprocessing """
    exp_poly = PolyIsing({(): -15})
    exp_variables = {1 : -1, 2 : -1, 3 : -1, 4 : 1}
    preprocessed_poly, preprocessed_variables = POLY1.preprocess_minimize()
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables

    exp_poly = PolyIsing({((X, 1), (Y, 2, 3)): -2, (): -3}, inverted=True)
    exp_variables = {(Y, 1, 2) : -1}
    preprocessed_poly, preprocessed_variables = POLY2.preprocess_minimize()
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables

    poly = PolyIsing({(1,) : -1, (0, 1) : -1, (0,) : 2, (0, 2) : -1, (2,) : -1})
    exp_variables = {0: -1, 1: 1, 2: 1}
    preprocessed_poly, preprocessed_variables = poly.preprocess_minimize()
    assert preprocessed_poly == -2
    assert preprocessed_variables == exp_variables

    poly = PolyIsing({(0,): 10, (1,): 2, (2,): -8, (3,): 5, (4,): -7, (5,): 4, (0, 1): 3, (0, 2): -4, (0, 3): -3,
                      (1, 3): -8, (1, 4): -7, (2, 3): 8, (2, 5): 1, (3, 4): 3, (3, 5): 2})
    exp_variables = {0: -1, 5: -1}
    exp_poly = PolyIsing({(): -14, (1,): -1, (2,): -5, (3,): 6, (4,): -7, (1, 3): -8, (1, 4): -7, (2, 3): 8, (3, 4): 3})
    preprocessed_poly, preprocessed_variables = poly.preprocess_minimize()
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables

    exp_variables = {5: -1}
    exp_poly = PolyIsing({(): -4, (0,): 10, (1,): 2, (2,): -9, (3,): 3, (4,): -7, (0, 1): 3, (0, 2): -4, (0, 3): -3,
                          (1, 3): -8, (1, 4): -7, (2, 3): 8, (3, 4): 3})
    preprocessed_poly, preprocessed_variables = poly.preprocess_minimize(unambitious=True)
    assert preprocessed_poly == exp_poly
    assert preprocessed_variables == exp_variables

def test_to_binary():
    """ test conversion to binary polynomial """
    poly_ising = PolyIsing.read_from_string("32 + 13 x1 + 9 x2 + 3 x3 - 5 x4 + 3 x1 x3 - 3 x2 x4")
    poly_ising_inv = poly_ising.invert()
    exp_binary_poly = 4 * PolyBinary.read_from_string("5 x1 + 6 x2 + 3 x1 x3 - x4 - 3 x2 x4 + 3")
    assert poly_ising.to_binary() == exp_binary_poly
    assert poly_ising_inv.to_binary() == exp_binary_poly

    poly_ising_inv = POLY1.invert()
    exp_binary_poly = PolyBinary({(): -7, (1,): 16, (1, 3): -12, (2,): 6, (2, 4): 12, (3,): 6, (4,): -8})
    assert POLY1.to_binary() == exp_binary_poly
    assert poly_ising_inv.to_binary() == exp_binary_poly

    poly_ising_inv = POLY2.invert()
    exp_binary_poly = PolyBinary({(): 1, ((X, 1),): 4, ((X, 1), (Y, 2, 3)): -8, ((Y, 1, 2),): -6,
                                  ((Y, 2, 3),): 4})
    assert POLY2.to_binary() == exp_binary_poly
    assert poly_ising_inv.to_binary() == exp_binary_poly

def test_from_unknown_poly_to_ising_no_inv():
    """ test conversion to ising polynomial without inverting ising and without setting ising to certain inversion """
    assert PolyIsing.from_unknown_poly(POLY1) == POLY1
    assert PolyIsing.from_unknown_poly(POLY1_INV) == POLY1_INV

    poly = PolyIsing.from_unknown_poly(POLY1_NONE)
    assert poly == POLY1_NONE
    assert isinstance(poly, PolyIsing)
    assert not poly.is_inverted()

    assert PolyIsing.from_unknown_poly(POLY1_BINARY) == POLY1

def test_unknown_poly_to_ising_invert():
    """ test conversion to ising polynomial with inverting ising """
    assert PolyIsing.from_unknown_poly(POLY1, invert=True) == POLY1_INV
    assert PolyIsing.from_unknown_poly(POLY1_INV, invert=True) == POLY1

    poly = PolyIsing.from_unknown_poly(POLY1_NONE, invert=True)
    assert poly == POLY1_NONE
    assert isinstance(poly, PolyIsing)
    assert poly.is_inverted()

    assert PolyIsing.from_unknown_poly(POLY1_BINARY, invert=True) == POLY1_INV

def test_unknown_poly_to_ising_set_inverted():
    """ test conversion to ising polynomial with setting ising to certain inversion """
    assert PolyIsing.from_unknown_poly(POLY1, inverted=False) == POLY1
    assert PolyIsing.from_unknown_poly(POLY1_INV, inverted=False) == POLY1
    assert PolyIsing.from_unknown_poly(POLY1, inverted=True) == POLY1_INV
    assert PolyIsing.from_unknown_poly(POLY1_INV, inverted=True) == POLY1_INV

    poly = PolyIsing.from_unknown_poly(POLY1_NONE, inverted=True)
    assert poly == POLY1_NONE
    assert isinstance(poly, PolyIsing)
    assert poly.is_inverted()

    poly = PolyIsing.from_unknown_poly(POLY1_NONE, inverted=False)
    assert poly == POLY1_NONE
    assert isinstance(poly, PolyIsing)
    assert not poly.is_inverted()

    assert PolyIsing.from_unknown_poly(POLY1_BINARY, inverted=True) == POLY1_INV
    assert PolyIsing.from_unknown_poly(POLY1_BINARY, inverted=False) == POLY1

def test_from_unknown_poly_to_ising_error():
    """ test conversion to ising polynomial error """
    with pytest.raises(ValueError, match="Choose either to set certain inversion"):
        PolyIsing.from_unknown_poly(POLY1, inverted=True, invert=True)

def test_affine_transform():
    """ test affine transformation """
    # pylint: disable=unidiomatic-typecheck
    exp_poly = Polynomial({(): 43, (1,): -14, (2,): 36, (3,): -24, (4,): 22, (1, 3): -12, (2, 4): 12})
    transformed_poly = POLY1.affine_transform(2, 4)
    assert transformed_poly == exp_poly
    assert type(transformed_poly) is Polynomial

def test_evaluate():
    """ test evaluation of Ising polynomial """
    # pylint: disable=unidiomatic-typecheck
    var_assignment = {(X, 1): -1, (Y, 2, 3): 1}
    evaluated_poly = POLY2.evaluate(var_assignment)
    exp_poly = PolyIsing({(): 2, ((Y, 1, 2),): 3}, inverted=True)
    check_polys_ising(evaluated_poly, exp_poly)

    var_assignment = {(X, 1) : -1, (Y, 2, 3) : 1, (Y, 1, 2) : -1}
    evaluated_poly = POLY2.evaluate(var_assignment)
    assert evaluated_poly == -1

    with pytest.raises(ValueError, match="Can only assign numbers or polynomials"):
        var_assignment = {(X, 1): PolyIsing({((X, 1),): 2, (): 3})}
        POLY2.evaluate(var_assignment)

    var_assignment = {(X, 1): Polynomial({(("z", 1),): 2, (): 3})}
    exp_poly = Polynomial({(("z", 1), (Y, 2, 3)): -4, ((Y, 1, 2),): 3, ((Y, 2, 3),): -6})
    evaluated_poly = POLY2.evaluate(var_assignment)
    assert type(evaluated_poly) is Polynomial
    assert evaluated_poly == exp_poly

def test_replace_variables():
    """ test replacement of variables """
    replacement = {(X, 1) : "a", (Y, 2, 3) : "b", (Y, 1, 2) : "c"}
    exp_poly = PolyIsing({("a", "b"): -2, ("c",): 3}, inverted=True)
    replaced_poly = POLY2.replace_variables(replacement)
    check_polys_ising(replaced_poly, exp_poly)

def test_get_rounded():
    """ test rounding """
    poly = PolyIsing({((X, 1), (Y, 2, 3)): -2.3, ((Y, 1, 2),): 2.9}, inverted=True)
    rounded_poly = poly.round(0)
    check_polys_ising(rounded_poly, POLY2)

def test_get_matrix_representation():
    """ test standard matrix representation """
    with pytest.warns(UserWarning, match="Constant offset of 16 is dropped"):
        linear, quadratic = POLY3.get_matrix_representation()
    assert np.array_equal(linear, POLY3_LINEAR)
    assert np.array_equal(quadratic, POLY3_QUADRATIC)

def test_get_from_matrix_representation():
    """ test conversion from matrix representation """
    poly = PolyIsing.get_from_matrix_representation(POLY3_LINEAR, POLY3_QUADRATIC)
    assert poly == POLY3 - 16

    poly = PolyIsing.get_from_matrix_representation(POLY3_QUAD_DIAG)
    exp_poly = PolyIsing({(2, 0): -3, (1, 3): 0.5, (0, 1): 0.9, (): 10})
    assert poly == exp_poly
