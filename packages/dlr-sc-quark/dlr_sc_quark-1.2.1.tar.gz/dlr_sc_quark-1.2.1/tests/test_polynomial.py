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

""" test polynomial module """

import numpy as np
import pytest

from quark import Polynomial
from quark.polynomial import sort_poly_dict, _get_info_values


X, Y = "x", "y"

VARIABLES = "variables"
OFFSET = "offset"
LINEAR = "linear"
QUADRATIC = "quadratic"

P1_DICT = {(1,): 5, (2,): 6, (3, 1): 3, (2, 4): 2, (4, 2): 1, (4,): 1, (): 3}
P2_DICT = {((Y, 2, 3), (X, 1)): 2, ((Y, 1, 2),): 3}
P3_DICT = {(2,): 1, (2, 4): 1, (3, 4): 3, (5,): 7}
P4_DICT = {((X, 1),): 7, ((X, 2),): 2}
P5_DICT = {(0,): 5, (1,): 6, (2, 0): -3, (1, 3): 0.5, (3,): -1, (0, 1): 0.9, (): 16, (2,): 0, (2, 2): 2}

POLY1 = Polynomial(P1_DICT)
POLY2 = Polynomial(P2_DICT)
POLY3 = Polynomial(P3_DICT)
POLY4 = Polynomial(P4_DICT)
POLY5 = Polynomial(P5_DICT)
POLY1_DUP = Polynomial(P1_DICT)
POLY2_DUP = Polynomial(P2_DICT)

POLY5_LINEAR = [ 5.,  6.,  0., -1.]
POLY5_QUADRATIC = [[ 0. ,  0.9, -3. ,  0. ],
                   [ 0. ,  0. ,  0. ,  0.5],
                   [ 0. ,  0. ,  2. ,  0. ],
                   [ 0. ,  0. ,  0. ,  0. ]]

# pylint: disable=protected-access


def teardown_function():
    """ reset cache """
    for poly in [POLY1, POLY2]:
        try:
            delattr(poly, VARIABLES)
            delattr(poly, LINEAR)
        except AttributeError:
            pass


def test_init():
    """ test initialization """
    assert len(POLY1) == 6
    assert len(POLY2) == 2
    assert (1, 3) in POLY1
    assert (3, 1) in POLY1
    assert (3, 1) not in dict(POLY1)
    assert ((X, 1), (Y, 2, 3)) in POLY2
    assert ((Y, 2, 3), (X, 1)) in POLY2
    assert ((Y, 2, 3), (X, 1)) not in dict(POLY2)
    assert all(isinstance(val, (float, int)) for val in POLY1.values())

    assert dict(POLY1) != P1_DICT
    assert dict(POLY2) != P2_DICT
    assert dict(POLY3) == P3_DICT
    assert dict(POLY4) == P4_DICT

    mixed_dict = {(1,): 5, ((Y, 1, 2),): 3}
    with pytest.raises(TypeError, match="Expected variable type 'Integral', but got 'tuple'"):
        Polynomial(mixed_dict)

    mixed_dict = {(1,): 5, ("a",): 6}
    with pytest.raises(TypeError, match="Expected variable type 'Integral', but got 'str'"):
        Polynomial(mixed_dict)

    mixed_dict = {("a",): 5, ((Y, 2, 3),): 6}
    with pytest.raises(TypeError, match="Expected variable type 'str', but got 'tuple'"):
        Polynomial(mixed_dict)

    strange_dict = {True : 5, False : 6}
    with pytest.raises(TypeError, match="Variable 'True' has invalid type 'bool'"):
        Polynomial(strange_dict)

    false_coeff_dict = {(1,) : "a"}
    with pytest.raises(ValueError, match="Invalid coefficient 'a'"):
        Polynomial(false_coeff_dict)

    false_tuple_dict = {((X, 1.4),) : 1}
    with pytest.raises(ValueError, match="is not formatted correctly, should only contain ints and strings"):
        Polynomial(false_tuple_dict)

def test_immutable():
    """ test disabled methods """
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY1[(1,)] = 4
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY2[(X, 1)] = 1
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        del POLY1[(1,)]
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY1.pop((1,))
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY1.popitem((1,))
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY1.clear()
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY1.update({(1, 2) : 4})
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY1.setdefault((1,), 6)
    with pytest.raises(TypeError, match="Cannot modify immutable Polynomial object"):
        POLY1.setdefault((1, 2), 6)

def test_equal():
    """ test equality check """
    # pylint: disable=unneeded-not
    assert POLY1 != POLY3
    assert not POLY1 == POLY3
    assert POLY4 == POLY4.copy()
    assert POLY4 != POLY2

    # new initialization
    assert POLY1_DUP == POLY1
    assert not POLY1_DUP != POLY1
    assert not POLY1_DUP is POLY1
    assert POLY2 == POLY2_DUP
    assert not POLY2 != POLY2_DUP
    assert not POLY2 is POLY2_DUP

    # adding zero coefficient
    sum_poly = POLY1 + Polynomial({(0,): 0})
    assert sum_poly == POLY1
    assert not sum_poly != POLY1

    # constant
    assert Polynomial({() : 3}) == 3
    assert Polynomial({() : 4}) != 3
    assert Polynomial() + 3 == 3
    assert 3 + Polynomial() == 3
    assert Polynomial({() : 3, (1,) : 4}) != 3

    assert POLY3 != P3_DICT

def test_add():
    """ test addition """
    exp_poly = Polynomial({(): 3, (1,): 5, (2,): 7, (4,): 1, (5,): 7, (1, 3): 3, (2, 4): 4, (3, 4): 3})
    sum_poly = POLY1 + POLY3
    assert sum_poly == exp_poly
    assert POLY1 == POLY1_DUP

    sum_poly = POLY1
    sum_poly += POLY3
    assert sum_poly == exp_poly
    assert POLY1 == POLY1_DUP

    exp_poly = Polynomial({((Y, 2, 3), (X, 1)): 2, ((Y, 1, 2),): 3, () : 3})
    sum_poly = POLY2 + 3
    assert sum_poly == exp_poly

    sum_poly = POLY2
    sum_poly += 3
    assert sum_poly == exp_poly

    sum_poly = 3
    sum_poly += POLY2
    assert sum_poly == exp_poly

    with pytest.raises(TypeError, match="Can only add numbers or polynomials"):
        _ = POLY1 + (X, 1)
    with pytest.raises(TypeError, match="Expected variable type 'Integral', but got 'tuple'"):
        _ = POLY1 + POLY2

def test_sub():
    """ test subtraction """
    exp_poly = Polynomial({(): 3, (1,): 5, (2,): 5, (4,): 1, (5,): -7, (1, 3): 3, (2, 4): 2, (3, 4): -3})

    diff_poly = POLY1 - POLY3
    assert diff_poly == exp_poly
    assert POLY1 == POLY1_DUP

    diff_poly = POLY1
    diff_poly -= POLY3
    assert diff_poly == exp_poly
    assert POLY1 == POLY1_DUP

    exp_poly = Polynomial({((Y, 2, 3), (X, 1)): 2, ((Y, 1, 2),): 3, (): -3})
    diff_poly = POLY2 - 3
    assert diff_poly == exp_poly

    diff_poly = POLY2
    diff_poly -= 3
    assert diff_poly == exp_poly

    diff_poly = 3 - POLY2
    assert diff_poly == -1 * exp_poly

    diff_poly = 3
    diff_poly -= POLY2
    assert diff_poly == -1 * exp_poly

def test_mul():
    """ test multiplication """
    exp_poly = Polynomial({(2,): 3, (5,): 21,
                           (1, 2): 5, (1, 5): 35, (2, 2): 6, (2, 4): 4, (2, 5): 42, (3, 4): 9, (4, 5): 7,
                           (1, 2, 3): 3, (1, 2, 4): 5, (1, 3, 4): 15, (1, 3, 5): 21, (2, 2, 4): 9, (2, 3, 4): 18,
                           (2, 4, 4): 1, (2, 4, 5): 21, (3, 4, 4): 3,
                           (1, 2, 3, 4): 3, (1, 3, 3, 4): 9, (2, 2, 4, 4): 3, (2, 3, 4, 4): 9})

    prod_poly = POLY1 * POLY3
    assert prod_poly == exp_poly
    assert POLY1 == POLY1_DUP

    prod_poly = POLY1
    prod_poly *= POLY3
    assert prod_poly == exp_poly
    assert POLY1 == POLY1_DUP

    prod_poly = POLY1
    prod_poly *= POLY1
    assert POLY1 * POLY1 == prod_poly

    exp_poly = Polynomial({((Y, 2, 3), (X, 1)): 4, ((Y, 1, 2),): 6})
    prod_poly = POLY2 * 2
    assert prod_poly == exp_poly
    assert POLY2 == POLY2_DUP

    prod_poly = POLY2
    prod_poly *= 2
    assert prod_poly == exp_poly
    assert POLY2 == POLY2_DUP

    prod_poly = 2
    prod_poly *= POLY2
    assert prod_poly == exp_poly
    assert POLY2 == POLY2_DUP

    with pytest.raises(TypeError, match="Can only multiply with numbers or polynomials"):
        _ = POLY1 * (X, 1)
    with pytest.raises(TypeError, match="Expected variable type 'Integral', but got 'str'"):
        _ = POLY1 * Polynomial({X : 1})

    poly = Polynomial({((X, 1),): 2, ((X, "a"),): 1})
    with pytest.raises(ValueError, match="Sorting failed"):
        _ = poly * poly

def test_div():
    """ test division """
    poly = Polynomial({((Y, 2, 3), (X, 1)): 4, ((Y, 1, 2),): 6})
    div_poly = poly / 2
    assert div_poly == POLY2

    div_poly = poly
    div_poly /= 2
    assert div_poly == POLY2

    div_poly = 2
    with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for \/=: 'int' and 'Polynomial'"):
        div_poly /= poly
    with pytest.raises(TypeError, match="Divisor should be number"):
        _ = poly / POLY1

def test_pow():
    """ test potentiated polynomials """
    exp_poly = Polynomial({((X, 1), (X, 1)): 49, ((X, 2), (X, 2)): 4, ((X, 1), (X, 2)): 28})
    assert POLY4 ** 2 == exp_poly
    assert POLY4 ** 3 == exp_poly * POLY4

    with pytest.raises(TypeError, match="Exponent should be integer"):
        _ = POLY1 ** 1.4

def test_contains():
    """ test containment of monomials """
    assert (2, 4) in POLY1
    assert (4, 2) in POLY1
    assert ((Y, 2, 3), (X, 1)) in POLY2
    assert ((X, 1), (Y, 2, 3)) in POLY2

def test_get():
    """ test getting of coefficients of monomials """
    assert POLY1.get((2, 4)) == 3
    assert POLY1.get((4, 2)) == 3
    assert POLY2.get(((Y, 2, 3), (X, 1))) == 2
    assert POLY2.get(((X, 1), (Y, 2, 3))) == 2

def test_getitem():
    """ test getting of coefficients using items """
    assert POLY1[2, 4] == 3
    assert POLY1[4, 2] == 3
    assert POLY2[(Y, 2, 3), (X, 1)] == 2
    assert POLY2[(X, 1), (Y, 2, 3)] == 2

def test_repr():
    """ test string representation """
    assert repr(POLY1) == "Polynomial({(): 3, (1,): 5, (2,): 6, (4,): 1, (1, 3): 3, (2, 4): 3})"

def test_str():
    """ test string representation """
    assert str(POLY1) == "+3 +5 x1 +6 x2 +1 x4 +3 x1 x3 +3 x2 x4"

def test_copy():
    """ test copying """
    copied_poly = POLY1.copy()
    assert POLY1 == copied_poly
    assert POLY1 is not copied_poly

def test_degree():
    """ test degree """
    assert POLY3.degree == 2
    assert POLY4.degree == 1
    assert (POLY4 * POLY4).degree == 2

def test_is_quadratic():
    """ test check for degree at most 2 """
    assert POLY1.is_quadratic()
    assert POLY4.is_quadratic()

    prod_poly = POLY3 * POLY3
    assert not prod_poly.is_quadratic()

    prod_poly = POLY4 * POLY4
    assert prod_poly.is_quadratic()

def test_has_int_coefficients():
    """ check for integer polynomials """
    assert POLY1.has_int_coefficients()
    assert POLY4.has_int_coefficients()
    assert Polynomial({(1,): 1}).has_int_coefficients()
    assert not Polynomial({(1,): 1.01}).has_int_coefficients()

def test_is_flat():
    """ check for flat variables """
    assert POLY1.is_flat()
    assert not POLY2.is_flat()
    assert POLY3.is_flat()
    assert not POLY4.is_flat()
    assert POLY5.is_flat()

def test_is_compact():
    """ test check for compact variables """
    assert POLY5.is_compact()
    assert not POLY1.is_compact()
    assert not POLY2.is_compact()

    poly = Polynomial({(0,) : 1})
    assert poly.is_compact()
    assert (POLY1 + poly).is_compact()

    compact_poly = POLY1.compact()
    assert compact_poly.is_compact()
    compact_poly = POLY2.compact()
    assert compact_poly.is_compact()

    assert Polynomial().is_compact()
    assert Polynomial({() : 3}).is_compact()

def test_variables():
    """ test list of variables """
    exp_variables = [1, 2, 3, 4]
    assert VARIABLES not in POLY1.__dict__
    assert POLY1.variables == exp_variables
    assert VARIABLES in POLY1.__dict__
    assert POLY1.variables == exp_variables

    exp_variables = [(X, 1), (Y, 1, 2), (Y, 2, 3)]
    assert VARIABLES not in POLY2.__dict__
    assert POLY2.variables == exp_variables
    assert VARIABLES in POLY2.__dict__
    assert POLY2.variables == exp_variables

def test_offset():
    """ test constant offset """
    exp_offset = 3
    assert OFFSET not in POLY1.__dict__
    assert POLY1.offset == exp_offset

    exp_offset = 0
    assert OFFSET not in POLY2.__dict__
    assert POLY2.offset == exp_offset

def test_linear():
    """ test linear part """
    exp_linear = Polynomial({(1,): 5, (2,): 6, (3,): 0, (4,): 1})
    assert LINEAR not in POLY1.__dict__
    assert POLY1.linear == exp_linear

    exp_linear = Polynomial({((X, 1),): 0, ((Y, 1, 2),): 3, ((Y, 2, 3),): 0})
    assert LINEAR not in POLY2.__dict__
    assert POLY2.linear == exp_linear

def test_linear_plain():
    """ test linear part """
    exp_linear = {1: 5, 2: 6, 3: 0, 4: 1}
    assert LINEAR not in POLY1.__dict__
    assert POLY1.linear_plain == exp_linear

    exp_linear = {(X, 1): 0, (Y, 1, 2): 3, (Y, 2, 3): 0}
    assert LINEAR not in POLY2.__dict__
    assert POLY2.linear_plain == exp_linear

def test_quadratic():
    """ test quadratic part """
    exp_quadratic = Polynomial({(1, 3): 3, (2, 4): 3})
    assert QUADRATIC not in POLY1.__dict__
    assert POLY1.quadratic == exp_quadratic

    exp_quadratic = Polynomial({((X, 1), (Y, 2, 3)): 2})
    assert QUADRATIC not in POLY2.__dict__
    assert POLY2.quadratic == exp_quadratic

def test_get_variable_num():
    """ test number of variables """
    assert VARIABLES not in POLY1.__dict__
    assert POLY1.get_variable_num() == 4
    assert VARIABLES in POLY1.__dict__

    assert VARIABLES not in POLY2.__dict__
    assert POLY2.get_variable_num() == 3
    assert VARIABLES in POLY2.__dict__

def test_get_coefficient():
    """ test coefficients """
    assert POLY1.get_coefficient(1) == 5
    assert POLY1.get_coefficient(3) == 0

    assert POLY2.get_coefficient((Y, 1, 2)) == 3
    assert POLY2.get_coefficient((X, 2)) == 0

    assert POLY1.get_coefficient(1, 3) == 3
    assert POLY1.get_coefficient(3, 1) == 3
    assert POLY1.get_coefficient(1, 6) == 0

    assert POLY2.get_coefficient((X, 1), (Y, 2, 3)) == 2
    assert POLY2.get_coefficient((X, 2), (Y, 2, 3)) == 0

def test_sigmas():
    """ test sigma values """
    exp_sigmas = {1: (3, 0), 2: (3, 0), 3: (3, 0), 4: (3, 0)}
    assert POLY1.sigmas == exp_sigmas

    exp_sigmas = {(X, 1): (2, 0), (Y, 2, 3): (2, 0), (Y, 1, 2): (0, 0)}
    assert POLY2.sigmas == exp_sigmas

    exp_sigmas = {0: (0.9, -3), 1: (1.4, 0), 2: (4, -3), 3: (0.5, 0)}
    assert POLY5.sigmas == exp_sigmas

def test_remove_zero_coefficients():
    """ test removal of monomials with zero coefficient """
    poly1_with_zeros = Polynomial({(1,): 5, (2,): 6, (3,): 0, (3, 1): 3, (2, 4): 3, (4,): 1, (): 3, (1, 4): 0})
    assert dict(poly1_with_zeros) != dict(POLY1)
    assert poly1_with_zeros == POLY1

    poly1_without_zeros = poly1_with_zeros.remove_zero_coefficients()
    assert dict(poly1_without_zeros) == dict(POLY1)
    assert poly1_without_zeros == POLY1

def test_evaluate():
    """ test evaluation """
    # P1(x0, x1, x2, x3, x4) = 5 x1 + 6 x2 + 3 x1 x3 + x4 + 3 x2 x4 + 3
    # P1(0, 1, 0, 1, 1) = 5 + 3 + 1 + 3 = 12
    assert POLY1.evaluate([0, 1, 0, 1, 1]) == 12

    # P1(-1, 1, -1, 1, 1) = 5 - 6 + 3 + 1 - 3 + 3 = 3
    assert POLY1.evaluate([-1, 1, -1, 1, 1]) == 3

    # P1(-1, 1, -1, 1, 1) = 5 - 6 + 3 + 1 - 3 + 3 = 3
    assert POLY1.evaluate([-1, 1, -1, 1, 1], keep_poly=True) == Polynomial({(): 3})

    exp_poly = Polynomial({(): 2, (3,): 3, (4,): -2})
    assert POLY1.evaluate([-1, 1, -1]) == exp_poly

    var_assignment = [Polynomial({(i,) : -1}) for i in range(5)]
    exp_poly = Polynomial({(1,): -5, (2,): -6, (3, 1): 3, (2, 4): 3, (4,): -1, (): 3})
    assert POLY1.evaluate(var_assignment) == exp_poly

    var_assignment = [1, 1, Polynomial({(2,) : -1}), 0, -2]
    assert POLY1.evaluate(var_assignment) == 6

    exp_poly = Polynomial({(2,): 6, (3,): 3, (2, 4): 3, (4,): 1, (): 8})
    assert POLY1.evaluate({1: 1}) == exp_poly

    exp_poly = Polynomial({(2,): 6, (2, 4): 3, (4,): 1, (): 3})
    assert POLY1.evaluate({1: 0}) == exp_poly

    exp_poly = Polynomial({(): 21})
    assert POLY1.evaluate({v: 1 for v in [1, 2, 3, 4]}) == exp_poly

    with pytest.raises(ValueError, match="Kept variables and replaced variables are not compatible"):
        POLY3.evaluate({4: Polynomial({((X, 1),): 1})})

def test_affine_transformation():
    """ test affine transformation """
    transformed_poly = POLY1.affine_transform(3, 5)
    exp_poly = Polynomial.read_from_string("60 x1 + 63 x2 + 27 x1 x3 + 45 x3 + 48 x4 + 27 x2 x4 + 213")
    assert transformed_poly == exp_poly

def test_replace_variables():
    """ test replacement of variables """
    replacement = {1 : "b", 2 : "c", 3 : "d", 4 : "e"}
    exp_poly = Polynomial({("b",): 5, ("c",): 6, ("d", "b"): 3, ("c", "e"): 3, ("e",): 1, (): 3})
    assert POLY1.replace_variables(replacement) == exp_poly

    replacement = ["a", "b", "c", "d", "e"]
    exp_poly = Polynomial({("b",): 5, ("c",): 6, ("d", "b"): 3, ("c", "e"): 3, ("e",): 1, (): 3})
    assert POLY1.replace_variables(replacement) == exp_poly

    replacement = {(Y, 2, 3) : 0, (X, 1) : 1, (Y, 1, 2) : 2}
    exp_poly = Polynomial({(0, 1): 2, (2,): 3})
    assert POLY2.replace_variables(replacement) == exp_poly

    # only partially replacing with variables of a different type does not work
    # in different monomials
    replacement = {(Y, 2, 3): "a", (Y, 1, 2): "b"}
    with pytest.raises(ValueError, match="Replacement is invalid"):
        POLY2.replace_variables(replacement)
    # in single monomial
    replacement = {(Y, 2, 3) : "a", (X, 1) : "b"}
    with pytest.raises(ValueError, match="Replacement is invalid"):
        POLY2.replace_variables(replacement)

    replacement = {(Y, 2, 3) : ("z", 1), (X, 1) : ("z", 2)}
    exp_poly = Polynomial({(("z", 1), ("z", 2)): 2, ((Y, 1, 2),): 3})
    assert POLY2.replace_variables(replacement) == exp_poly

    replacement = {var : 0 for var in POLY1.variables}
    exp_poly = Polynomial({(0,): 12, (0, 0): 6, (): 3})
    assert POLY1.replace_variables(replacement) == exp_poly

    replacement = [0] * 5
    exp_poly = Polynomial({(0,): 12, (0, 0): 6, (): 3})
    assert POLY1.replace_variables(replacement) == exp_poly

    exp_poly = Polynomial({((X, 1),): 5, ((X, 2),): 6, ((X, 3), (X, 1)): 3, ((X, 2), (X, 4)): 2,
                             ((X, 4), (X, 2)): 1, ((X, 4),): 1, (): 3})
    assert POLY1.replace_variables(lambda x: (X, x)) == exp_poly

def test_replace_variables_by_ordering():
    """ test replacement of variables """
    replacement = [(Y, 2, 3), (X, 1), (Y, 1, 2)]
    exp_poly = Polynomial({(0, 1): 2, (2,): 3})
    assert POLY2.replace_variables_by_ordering(replacement) == exp_poly

def test_compact():
    """ test construction of compact polynomials """
    compact_poly = POLY2.compact()
    exp_poly = Polynomial({(0, 2): 2, (1,): 3})
    assert compact_poly == exp_poly
    assert compact_poly.variables == [0, 1, 2]

def test_round():
    """ test rounding """
    exp_poly = Polynomial({(0,): 5, (1,): 6, (2, 0): -3, (2, 2): 2, (1, 3): 0, (3,): -1, (0, 1): 1, (): 16})
    assert POLY5.round(0) == exp_poly

    exp_poly = Polynomial({(1,): 4, (2,): 5.78})
    assert Polynomial({(1,): 4, (2,): 5.7777}).round(2) == exp_poly

def test_get_coeff_list():
    """ test coefficients lists """
    assert len(POLY5.coefficients_lists) == 3
    assert POLY5.coefficients_lists[0] == [16]
    assert POLY5.coefficients_lists[1] == [-1, 0, 5, 6]
    assert POLY5.coefficients_lists[2] == [-3, 0.5, 0.9, 2.0]

def test_get_coefficients_info_by_degree():
    """ test coefficient calculation """
    exp_info = {"max_abs_coeff_degree_1":      6.0,
                "min_abs_coeff_degree_1":      1.0,
                "min_dist_degree_1":           1.0,
                "min_abs_dist_degree_1":       1.0,
                "max_min_ratio_degree_1":      6.0,
                "max_dist_ratio_degree_1":     6.0,
                "max_abs_dist_ratio_degree_1": 6.0}
    assert POLY5.get_coefficients_info_by_degree(1) == exp_info

    exp_info = {"max_abs_coeff_degree_2":      3.0,
                "min_abs_coeff_degree_2":      0.5,
                "min_dist_degree_2":           0.4,
                "min_abs_dist_degree_2":       0.4,
                "max_min_ratio_degree_2":      6.0,
                "max_dist_ratio_degree_2":     7.5,
                "max_abs_dist_ratio_degree_2": 7.5}
    assert POLY5.get_coefficients_info_by_degree(2) == exp_info

    exp_info = {"max_abs_coeff_degree_1":      7.0,
                "min_abs_coeff_degree_1":      2.0,
                "min_dist_degree_1":           2.0,
                "min_abs_dist_degree_1":       2.0,
                "max_min_ratio_degree_1":      3.5,
                "max_dist_ratio_degree_1":     3.5,
                "max_abs_dist_ratio_degree_1": 3.5,}
    assert POLY4.get_coefficients_info_by_degree(1) == exp_info
    assert not POLY4.get_coefficients_info_by_degree(2)

    with pytest.raises(ValueError, match="Provide degree greater than 0"):
        POLY4.get_coefficients_info_by_degree(0)

def test_get_all_coefficients_info():
    """ test coefficient calculation """
    exp_info = {"max_abs_coeff_degree_1":      6.0, "max_abs_coeff_degree_2":      3.0, "max_abs_coeff":      6.0,
                "min_abs_coeff_degree_1":      1.0, "min_abs_coeff_degree_2":      0.5, "min_abs_coeff":      0.5,
                "min_dist_degree_1":           1.0, "min_dist_degree_2":           0.4, "min_dist":           0.4,
                "min_abs_dist_degree_1":       1.0, "min_abs_dist_degree_2":       0.4, "min_abs_dist":       0.1,
                "max_min_ratio_degree_1":      6.0, "max_min_ratio_degree_2":      6.0, "max_min_ratio":      12.0,
                "max_dist_ratio_degree_1":     6.0, "max_dist_ratio_degree_2":     7.5, "max_dist_ratio":     15.0,
                "max_abs_dist_ratio_degree_1": 6.0, "max_abs_dist_ratio_degree_2": 7.5, "max_abs_dist_ratio": 60.0}
    assert POLY5.get_all_coefficients_info() == exp_info

    exp_info = {"max_abs_coeff_degree_1":      7.0, "max_abs_coeff":      7.0,
                "min_abs_coeff_degree_1":      2.0, "min_abs_coeff":      2.0,
                "min_dist_degree_1":           2.0, "min_dist":           2.0,
                "min_abs_dist_degree_1":       2.0, "min_abs_dist":       2.0,
                "max_min_ratio_degree_1":      3.5, "max_min_ratio":      3.5,
                "max_dist_ratio_degree_1":     3.5, "max_dist_ratio":     3.5,
                "max_abs_dist_ratio_degree_1": 3.5, "max_abs_dist_ratio": 3.5}
    assert POLY4.get_all_coefficients_info() == exp_info

    assert not Polynomial().get_all_coefficients_info()

def test_calc_coefficient_info_from_list():
    """ test coefficient calculation """
    coefficients_list = [10, -10, 8, 7, 0.1, 1.1, 1.15, 13, -1.12]
    exp_values = (0.1, 13, 0.05, 0.02, 13 / 0.1, 13 / 0.05, 13 / 0.02)
    values = _get_info_values(coefficients_list)
    assert values == pytest.approx(exp_values, abs=1e-9)
    _check_coefficient_info_calc(coefficients_list)
    assert _get_info_values([]) == (0, 0, 0, 0, 0, 0, 0)

def test_calc_coefficient_info_from_list_random():
    """ test coefficient calculation """
    np.random.seed(0)
    _check_coefficient_info_calc(list(np.random.randn(20)))
    _check_coefficient_info_calc(list(np.random.uniform(-10, 0, 20)))
    _check_coefficient_info_calc(list(np.random.uniform(0, 10, 20)))

def test_to_string():
    """ test string creation """
    assert str(POLY1) == "+3 +5 x1 +6 x2 +1 x4 +3 x1 x3 +3 x2 x4"
    assert str(POLY2) == "+3 y_1_2 +2 x_1 y_2_3"
    assert str(POLY3) == "+1 x2 +7 x5 +1 x2 x4 +3 x3 x4"
    assert str(Polynomial({X : 4, (X, Y) : 2})) == "+4 x +2 x y"
    assert str(Polynomial({((1, 1),) : 4, ((1, 2), (0, 2)) : 2})) == "+4 x_1_1 +2 x_0_2 x_1_2"

    exp_str = "+3 +4 x0 +6 x1 +3 x2 +8 x0 x1 +6 x1 x2 +3 x1 x3 +4 x0 x1 x3 +3 x1 x2 x3"
    assert str(Polynomial({1 : 2, (3, 1) : 1, () : 1}) * Polynomial({2 : 3, 0 : 4, () : 3})) == exp_str

def test_sorted_dict():
    """ test sorting of poly dictionary """
    poly = Polynomial({(3,): 2, (1, 2): 4, (1,): 1})
    assert str(dict(poly)) == "{(3,): 2, (1, 2): 4, (1,): 1}"
    assert str(poly) == "+1 x1 +2 x3 +4 x1 x2"
    assert str(dict(poly)) == "{(1,): 1, (3,): 2, (1, 2): 4}"

    sorted_poly_dict = sort_poly_dict(poly)
    assert list(sorted_poly_dict.keys()) == [(1,), (3,), (1, 2)]
    sorted_poly_dict = sort_poly_dict(poly, reverse_monomial_degree_order=True)
    assert list(sorted_poly_dict.keys()) == [(1, 2), (1,), (3,)]

    poly = Polynomial({((X, 1),): 2, ((X, Y),): 1})
    with pytest.raises(ValueError, match="Sorting failed"):
        str(poly)

def test_read_from_string():
    """ test reading in from strings """
    exp_poly = Polynomial({(2,): 3, (5,): 21,
                           (1, 5): 35, (1, 12): -5, (2, 2): 6, (2, 4): 4, (2, 5): 42, (3, 4): 9, (5, 41): -7,
                           (1, 2, 3): 3, (1, 2, 4): 5, (1, 3, 4): 15, (1, 3, 5): 21, (2, 2, 4): 9, (2, 3, 4): 18,
                           (2, 4, 4): 1, (3, 4, 4): 3,
                           (1, 2, 3, 4): 3, (1, 3, 3, 4): -9, (2, 2, 4, 4): 3, (2, 3, 4, 4): 9, (2, 4, 5, 7): 21})

    input_str = """3.0 x2 - 5 x1 x12 + 6. x2^2 + 3 x1 x2 x3 + 4 x2 x4 + 5 x1 x2 x4 + 9 x2^2 x4 + 9 x3 x4 + 15 x1 x3 x4
                   + 18 x2 x3 x4 + 3 x1 x2 x3 x4 - 9 x1 x3^2 x4 + 1 x2 x4^2 + 3 x2^2 x4^2 + 3 x3 x4^2 + 9 x2 x3 x4^2
                   + 21 x5 + 35 x1 x5 + 42 x2 x5 + 21 x1 x3 x5 - 7 x41 x5 + 21 x2 x4 x5 x7"""
    poly_from_str = Polynomial.read_from_string(input_str)
    assert poly_from_str == exp_poly

    output_str = str(poly_from_str)
    assert Polynomial.read_from_string(output_str) == poly_from_str

    with pytest.raises(ValueError, match="Double exponents are not supported"):
        Polynomial.read_from_string("1. x1^2^3")

def _check_coefficient_info_calc(coeff_list):
    exp_min_abs_coeff = min(abs(v) for v in coeff_list)
    exp_max_abs_coeff = max(abs(v) for v in coeff_list)
    exp_min_dist = min(abs(v1 - v2) for v1 in coeff_list for v2 in coeff_list if abs(v1 - v2) != 0)
    exp_min_abs_dist = min(abs(abs(v1) - abs(v2)) for v1 in coeff_list for v2 in coeff_list
                                 if abs(abs(v1) - abs(v2)) != 0)
    exp_max_min_ratio = exp_max_abs_coeff / exp_min_abs_coeff
    exp_max_dist_ratio = exp_max_abs_coeff / exp_min_dist
    exp_max_abs_dist_ratio = exp_max_abs_coeff / exp_min_abs_dist

    exp_coeff_info = (exp_min_abs_coeff, exp_max_abs_coeff, exp_min_dist, exp_min_abs_dist, exp_max_min_ratio,
                      exp_max_dist_ratio, exp_max_abs_dist_ratio)
    assert _get_info_values(coeff_list) == pytest.approx(exp_coeff_info, abs=1e-9)

def test_get_matrix_representation():
    """ test standard matrix representation """
    with pytest.warns(UserWarning, match="Constant offset of 16 is dropped"):
        linear, quadratic = POLY5.get_matrix_representation()
    assert np.array_equal(linear, POLY5_LINEAR)
    assert np.array_equal(quadratic, POLY5_QUADRATIC)

    poly1_linear = [0, 5, 6, 0, 1, 0]
    poly1_quadratic = [[0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 3, 0, 0],
                       [0, 0, 0, 0, 3, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0]]
    with pytest.warns(UserWarning, match="Constant offset of 3 is dropped"):
        linear, quadratic = POLY1.get_matrix_representation(num_variables=6)
    assert np.array_equal(linear, poly1_linear)
    assert np.array_equal(quadratic, poly1_quadratic)

    with pytest.raises(ValueError, match="Only applicable for flat polynomials"):
        POLY2.get_matrix_representation()
    with pytest.raises(ValueError, match="Either provide compact polynomial or the total number of variables"):
        POLY1.get_matrix_representation()
    with pytest.raises(ValueError, match="Only applicable for quadratic polynomials"):
        Polynomial({(1, 2, 3) : 1}).get_matrix_representation()

def test_get_from_matrix_representation():
    """ test conversion from matrix representation """
    poly = Polynomial.get_from_matrix_representation(POLY5_LINEAR, POLY5_QUADRATIC)
    assert poly == POLY5 - 16

    with pytest.raises(ValueError, match="Can only process matrices with at most two dimensions"):
        Polynomial.get_from_matrix_representation([[[1]]])

def test_get_graph():
    """ test graph generation """
    graph = POLY1.get_graph()
    exp_nodes = {1, 2, 3, 4}
    exp_edges = {(1, 3), (2, 4)}
    assert set(graph.nodes) == exp_nodes
    assert set(graph.edges) == exp_edges

    with pytest.raises(ValueError, match="Only applicable for quadratic polynomials"):
        (POLY1 * POLY1).get_graph()
