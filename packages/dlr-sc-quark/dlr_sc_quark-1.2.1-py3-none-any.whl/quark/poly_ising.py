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

""" module for PolyIsing """

from collections import Counter
from functools import wraps
from math import copysign

from .polynomial import Polynomial
from . import poly_binary


ADD      = "add"
MULTIPLY = "multiply"

ERROR_INVERTED = "Cannot {} two PolyIsings with different inversions"
ERROR_BINARY   = "Cannot {} PolyIsing and PolyBinary"
ERROR_INVERT   = "Choose either to set certain inversion of or to invert the possible PolyIsing"


def _call_super_and_set_inverted(decorated_func):
    """
    a decorator which takes the returned Polynomial from the decorated method
    and returns a PolyIsing instead with the correctly set attribute '_inverted'

    :return: the new function
    """
    @wraps(decorated_func)
    def wrapper(self, *args, **kwargs):
        """
        the wrapper function executes the decorated function, executes its super function and, if the resulting
        polynomial is a PolyIsing, sets the inverted flag
        """
        # call decorated function
        decorated_func(self, *args, **kwargs)
        # get the super function
        super_func = getattr(super(PolyIsing, self), decorated_func.__name__)
        # get the resulting polynomial
        result_poly = super_func(*args, **kwargs)
        if isinstance(result_poly, PolyIsing):
            # set the correct inverted flag if it is an Ising polynomial
            result_poly._inverted = self.is_inverted()  #pylint: disable=protected-access
        return result_poly

    return wrapper


class PolyIsing(Polynomial):
    """
    An Ising polynomial is a special polynomial, where the variables can only take -1 or 1.
    Since (-1)^2 = 1^2 = 1, we can simplify the Polynomial by removing all even exponents,
    e.g.

        * (0, 0, 1, 1, 1): 1 -> (1,): 1,
        * (2, 2, 2, 2): 2    -> (): 2.

    We have the following conventions:

        *  PolyIsing == PolyIsing <=> poly == poly and inverted == inverted,
        *  PolyIsing == Polynomial <=> poly == poly,
        *  PolyIsing +/* Polynomial = PolyIsing,
        *  Polynomial +/* PolyIsing = Polynomial + Warning,
        *  PolyIsing(inverted=True) +/* PolyIsing(inverted=False) = Error,
        *  PolyIsing +/* PolyBinary = Error,
        *  copy/remove_zero_coefficients/replace_variables/get_rounded(PolyIsing) = PolyIsing
                (with correctly set inverted attribute),
        *  evaluate(PolyIsing, {var : Number}) = PolyIsing/Number,
        *  evaluate(PolyIsing, {var : Polynomial}) = Polynomial,
        *  evaluate(PolyIsing, {var : PolyIsing}) = Error,
        *  PolyBinary == PolyIsing = False.
    """

    def __init__(self, d=None, inverted=False, variable_tuples_already_formatted=False):
        """
        initialize PolyIsing object

        :param (dict) d: mapping from tuples of variables to coefficients
        :param (bool) variable_tuples_already_formatted: if True, d will be used as passed to save time on sorting,
                                                         use if d is, e.g., a dictionary of an existing Polynomial,
                                                         otherwise every key in d will be sorted
        :param (bool) inverted: flag that defines the relation to the binary format:
                                False : 0 <-> -1, 1 <-> 1
                                True  : 0 <-> 1, 1 <-> -1
        """
        self._inverted = inverted
        super().__init__(d, variable_tuples_already_formatted)

    def _format_variable_tuple(self, var_tuple):
        """
        transform the tuple of variables into the standard format, also checks the type of the variables,
        extends 'Polynomial._format_variable_tuple',
        since we have s * s = 1  for all s in {-1, +1}, all even powers can be removed
        """
        var_tuple = super()._format_variable_tuple(var_tuple)
        var_powers = Counter(var_tuple)
        if not len(var_powers) == len(var_tuple):
            var_tuple = tuple(var for var, power in var_powers.items() if power % 2 > 0)
        return var_tuple

    def __eq__(self, other):
        """
        check equality of polynomials, where PolyIsing is never equal to a PolyBinary,
        extends 'Polynomial.__eq__'
        """
        if isinstance(other, poly_binary.PolyBinary):
            return False
        if super().__eq__(other):
            if isinstance(other, PolyIsing):
                # if compared to another PolyIsing also check the inverted attribute
                return self.is_inverted() == other.is_inverted()
            # if PolyIsing is compared to Polynomial we ignore the attribute 'inverted'
            return True
        return False

    def _check_different(self, poly2, func_name):
        """ check if the type of the second Polynomial is feasible for an operation """
        if isinstance(poly2, PolyIsing) and poly2.is_inverted() != self.is_inverted():
            raise ValueError(ERROR_INVERTED.format(func_name))
        if isinstance(poly2, poly_binary.PolyBinary):
            raise ValueError(ERROR_BINARY.format(func_name))

    @_call_super_and_set_inverted
    def __add__(self, poly2):
        """
        add another polynomial or a scalar,
        extends 'Polynomial.__add__' since PolyBinary cannot be added to PolyIsing
        """
        self._check_different(poly2, ADD)

    @_call_super_and_set_inverted
    def __mul__(self, poly2):
        """
        multiply with another polynomial or a scalar,
        extends 'Polynomial.__mul__' since PolyBinary cannot be multiplied with PolyIsing
        """
        self._check_different(poly2, MULTIPLY)

    # pylint: disable=multiple-statements  # Better readability
    @_call_super_and_set_inverted
    def copy(self): pass

    @_call_super_and_set_inverted
    def remove_zero_coefficients(self): pass

    @classmethod
    def _is_valid_var_assignment(cls, var_assignment):
        """
        check whether the given input can be assigned to the variable,
        that means it is a Polynomial, PolyBinary, SCIP Expr or valid coefficient,
        extends 'Polynomial._is_valid_var_assignment' to not allow for PolyBinary
        """
        return not isinstance(var_assignment, PolyIsing) and super()._is_valid_var_assignment(var_assignment)

    @_call_super_and_set_inverted
    def evaluate(self, var_assignments, keep_poly=False): pass

    @_call_super_and_set_inverted
    def replace_variables(self, replacement): pass

    @_call_super_and_set_inverted
    def round(self, decimal_cap=None): pass

    # additional methods for Ising polynomials

    @classmethod
    def from_unknown_poly(cls, poly, inverted=None, invert=False):
        """
        convert a polynomial of unknown type into a PolyIsing

        :param (Polynomial) poly: the polynomial of unknown type
        :param (bool or None) inverted: if set to False the resulting PolyIsing will be not be an inverted one
                                        if set to True the resulting PolyIsing will be an inverted one
        :param (bool) invert: if set to True the resulting PolyIsing will be inverted
                              meaning if it was non-inverted PolyIsing before it will be inverted afterwards
                              resp. if it was an inverted PolyIsing before it will not be inverted anymore
                              (cannot be set if inverted is set)
        :return: the corresponding Ising polynomial
        """
        if not (inverted is None or not invert):
            raise ValueError(ERROR_INVERT)

        if isinstance(poly, poly_binary.PolyBinary):
            return poly.to_ising(inverted or invert)
        if isinstance(poly, cls):
            if inverted is not None and poly.is_inverted() != inverted:
                return poly.invert()
            if inverted is None and invert:
                return poly.invert()
            return poly
        return cls(poly, inverted=inverted or invert)

    def preprocess_minimize(self, unambitious=False):
        """
        simplify the polynomial by setting some variables to the values which are guaranteed to appear in an optimal
        solution when considering minimization

        :param (bool) unambitious:
            if True, only those variables will be set where their assignment is unambitious, that means, in all optimal
            solutions, they have the same value,
            if False, preprocess the variable to the straightforward value whether it might also get another value in an
            optimal solution, the objective values remains the same
        :return: the new reduced Polynomial and the assignment of the eliminated variables with variable to value
        """
        return super().preprocess(preprocess_rule, unambitious)

    def is_inverted(self):
        """ check if the PolyIsing is inverted """
        return self._inverted

    def invert(self):
        """ interchange 1 and -1 in solutions of the PolyIsing by applying the mapping s -> -s """
        result = self.affine_transform(-1)
        return PolyIsing(result, not self._inverted)

    def to_binary(self):
        """
        convert the Ising polynomial to the binary format
        by convention it is always from the not inverted ising,
        therefore if inverted is
            - False, we use the conversion -1 -> 0, 1 -> 1 with s = 2x - 1,
            - True, we use the conversion -1 -> 1, 1 -> 0 with s = -2x + 1

        :return: the corresponding PolyBinary
        """
        converted = self.affine_transform(-2, 1) if self.is_inverted() else self.affine_transform(2, -1)
        return poly_binary.PolyBinary(converted)


def preprocess_rule(var_sigmas, coeff, unambitious=False):
    """
    very simple preprocessing function:
    if the absolute weight of the variable extends all influences from the outside
    (i.e. the sum of all absolute strengths on couplings including this variable = positive sigma - negative sigma)
    the variable can be assigned in advance, such that the product of var_assignment * weight is negative
    therefore negative sign of the coefficient

    :param (tuple) var_sigmas: sigma values (combined incoming strengths) of a variable of the polynomial
    :param (Real) coeff: coefficient on the linear term of the variable
    :param (bool) unambitious: if True only those variables will be set where their assignment is unambitious,
                               that means, in all optimal solutions, they have the same value,
                               if False, preprocess the variable to the straightforward value whether it might also
                               get another value in an optimal solution, the objective values remains the same
    :return: the solution value or None if the variable cannot be preprocessed
    """
    if unambitious and abs(coeff) == var_sigmas[0] - var_sigmas[1]:
        return None
    if abs(coeff) >= var_sigmas[0] - var_sigmas[1]:
        return -copysign(1, coeff)
    return None
