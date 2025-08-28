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

""" module for Polynomial """

from functools import cached_property
from itertools import product
from numbers import Real, Integral
from warnings import warn
from typing_extensions import Self
import numpy as np
from pyscipopt import Expr
import networkx as nx

from .utils import variables


DEGREE             = "degree"
VARIABLES          = "variables"
QUADRATIC          = "quadratic"
SIGMAS             = "sigmas"
COEFFICIENTS_LISTS = "coefficients_lists"
COEFFICIENTS_INFO  = "coefficients_info"
EXPECTED           = "Expected variable type"
PREPROCESS_RULE    = "preprocess_rule"
LINEAR             = "linear"
MIN_ABS_COEFF      = "min_abs_coeff"
MAX_ABS_COEFF      = "max_abs_coeff"
MIN_DIST           = "min_dist"
MIN_ABS_DIST       = "min_abs_dist"
MAX_MIN_RATIO      = "max_min_ratio"
MAX_DIST_RATIO     = "max_dist_ratio"
MAX_ABS_DIST_RATIO = "max_abs_dist_ratio"
VALUES_INFO_KWARGS = [MIN_ABS_COEFF, MAX_ABS_COEFF, MIN_DIST, MIN_ABS_DIST,
                     MAX_MIN_RATIO, MAX_DIST_RATIO, MAX_ABS_DIST_RATIO]

ERROR_COEFF      = "Invalid coefficient '{}'"
ERROR_IMMUTABLE  = "Cannot modify immutable Polynomial object"
ERROR_ADD        = "Can only add numbers or polynomials"
ERROR_MULTIPLY   = "Can only multiply with numbers or polynomials"
ERROR_EXPONENT   = "Exponent should be integer"
ERROR_DIVISOR    = "Divisor should be number"
ERROR_ASSIGN     = "Can only assign numbers or polynomials"
ERROR_REPLACE    = "Replacement is invalid, the resulting polynomial has different variable types"
ERROR_PREPROCESS = "No preprocess rule implemented, needs to be provided"
ERROR_QUADRATIC  = "Only applicable for quadratic polynomials"
ERROR_FLAT       = "Only applicable for flat polynomials"
ERROR_COMPACT    = "Either provide compact polynomial or the total number of variables"
ERROR_MATRIX     = "Can only process matrices with at most two dimensions"
ERROR_DOUBLE     = "Double exponents are not supported"
ERROR_KEPT       = "Kept variables and replaced variables are not compatible"
ERROR_SORTING    = "Sorting failed, this is most likely due to variables with the same prefix but different " \
                   "structure, as e.g. `('x', 1)` and `('x', 'a')`"
ERROR_DEGREE     = "Provide degree greater than 0"

WARNING_CAST        = "{} will be cast to Polynomial when added or multiplied from the right"
WARNING_CONSTANT    = "Constant offset of {} is dropped"


# pylint: disable=too-many-public-methods
class Polynomial(dict):
    """
    A polynomial is defined as the sum of weighted monomials, like

        P = P0
            * +sum_{i} P1_{i} x_i
            * +sum_{i, j} P2_{i, j} x_i x_j
            * +sum_{i, j, k} P3_{i, j, k} x_i x_j x_k
            * +...,

    where x_i are variables.

    In particular, P is stored as a Python dictionary mapping the tuple of variables, e.g. here indices,
    to the value of the coefficient:

        * var_tuple --> coefficient
        * `()`      --> P0            (offset)
        * `(i,)`    --> P1_{i}        (linear monomials)
        * `(i, j)`  --> P2_{i, j}     (quadratic monomials)
        * ...

    The variables in the tuples of the polynomial can be either of type

        * ints              (e.g. `(1, 2)`),
        * strings           (e.g. `('x', 'y')`),
        * tuples themselves (e.g. `(('x', 1), ('x', 2))`)     (only containing ints and strings),

    but the cases cannot be mixed up, since they cannot be compared with each other for sorting
    (therefore `(('x', 1), 'y')` is for instance not possible).

    The type of the variables can be unset if the Polynomial is empty or just a constant.
    """

    def __init__(self, d=None, variable_tuples_already_formatted=False):
        """
        initialize Polynomial object

        :param (dict) d: mapping from tuples of variables to coefficients
        :param (bool) variable_tuples_already_formatted: if True, d will be used as passed to save time on sorting,
                                                         use if d is, e.g., a dictionary of an existing Polynomial
                                                         (be careful with other cases, this avoids also type checks...),
                                                         otherwise every key in d will be sorted
        """
        self.var_type = None  # type of the variables

        if isinstance(d, self.__class__) or variable_tuples_already_formatted:
            super().__init__(d)
            some_key = next((k for k in self.keys() if k), None)
            self.var_type = variables.get_common_type(some_key)
            return

        if self._is_valid_coefficient(d):
            # just a constant was passed
            super().__init__({(): d})
            return

        d = d or {}
        poly = {}
        for var_tuple, coeff in d.items():
            if var_tuple and not self.var_type:
                self.var_type = variables.get_common_type(var_tuple)
            var_tuple = self._format_variable_tuple(var_tuple)
            if not self._is_valid_coefficient(coeff):
                raise ValueError(ERROR_COEFF.format(coeff))
            _add_monomial(poly, var_tuple, coeff)
        super().__init__(poly)

    def _format_variable_tuple(self, var_tuple):
        """
        transform the tuple of variables into the standard format, also checks the type of the variables

        :param (tuple or int or str) var_tuple: unordered tuple of variables
        :return: the formatted and ordered tuple of variables
        """
        #  if there is a single int or string, it should be a tuple of length one
        if not isinstance(var_tuple, tuple):
            var_tuple = (var_tuple,)
        # check if all variables in the tuple have the same preset type
        for var in var_tuple:
            variables.check_type_against(var, self.var_type)
        var_tuple = tuple(_try_sorted(var_tuple))
        return var_tuple

    @staticmethod
    def _is_valid_coefficient(coeff):
        """ check if the coefficient has the correct type (just numbers) """
        return isinstance(coeff, Real)

    @staticmethod
    def _immutable(*args, **kwargs):
        """ workaround to make some inherited functions unusable """
        raise TypeError(ERROR_IMMUTABLE)

    __setitem__ = _immutable
    __delitem__ = _immutable
    pop = _immutable
    popitem = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable

    # for caching of computed values

    @cached_property
    def degree(self):
        """ the degree of the polynomial, i.e., the largest appearing size of a monomial """
        return max((len(var_tuple) for var_tuple in self.remove_zero_coefficients()), default=0)

    @cached_property
    def variables(self):
        """ the list of variables """
        return _try_sorted(set(var for var_tuple in self for var in var_tuple))

    @cached_property
    def offset(self):
        """ the coefficient of the empty monomial """
        return self.get((), 0)

    @cached_property
    def linear_plain(self):
        """
        the weights on the variables in the linear part of the polynomial, also known as local fields

        we need to separate this method from 'Polynomial.linear' due to the representation of variables as tuples,
        which we do not want here
        """
        return {var : self.get_coefficient(var) for var in self.variables}

    @cached_property
    def linear(self):
        """ the linear part of the polynomial """
        poly = self.__class__({(var,) : value for var, value in self.linear_plain.items()},
                              variable_tuples_already_formatted=True)
        return poly.remove_zero_coefficients()

    @cached_property
    def quadratic(self):
        """ the quadratic part of the polynomial """
        quadratic_monomials = _try_sorted(var_tuple for var_tuple in self.keys() if len(var_tuple) == 2)
        return self.__class__({var_tuple : self.get_coefficient(*var_tuple) for var_tuple in quadratic_monomials},
                              variable_tuples_already_formatted=True).remove_zero_coefficients()

    @cached_property
    def coefficients_lists(self):
        """ list of lists containing the linear, quadratic, cubic, etc. coefficients """
        coefficients = [[] for _ in range(self.degree + 1)]
        for var_tuple, coeff in self.items():
            coefficients[len(var_tuple)].append(coeff)
        coeff_lists = [sorted(set(cs)) for cs in coefficients]
        return coeff_lists

    @cached_property
    def coefficients_info(self):
        """ dictionary with various coefficient information """
        # the first coefficient list is just the offset, this can be ignored
        if len(self.coefficients_lists) > 1:
            return get_info(sum(self.coefficients_lists[1:], []))
        return {}

    @cached_property
    def maximum_int_deviation(self):
        """ the largest difference from a coefficient to the closest int value """
        return max(abs(coeff - round(coeff)) for coeff_list in self.coefficients_lists for coeff in coeff_list)

    @cached_property
    def sigmas(self):
        """
        the dictionary the combined influences on a single variable, with
        variable -> (sum of all positive coupling coefficients, sum of all negative coupling coefficients)
        """
        sigmas_pos = {}
        sigmas_neg = {}
        for couple, strength in self.quadratic.items():
            for var in couple:
                if strength > 0:
                    sigmas_pos[var] = sigmas_pos.get(var, 0) + strength
                else:
                    sigmas_neg[var] = sigmas_neg.get(var, 0) + strength
        return {var : (sigmas_pos.get(var, 0), sigmas_neg.get(var, 0)) for var in self.variables}

    def __repr__(self):
        """ get nice string representation """
        self.sort_entries()
        return self.__class__.__name__ + "(" + super().__repr__() + ")"

    def __str__(self):
        """
        convert the polynomial to a human-readable string,
        non-flat polynomials might look weird and cannot be parsed back again
        """
        if self.is_constant():
            return f"{self.offset}"
        result = ''
        coeff_str = ' {:+n}'
        self.sort_entries()
        for var_tuple, coeff in self.items():
            var_str = ''
            if var_tuple:
                var_str = ' ' + ' '.join(variables.to_string(var, self.__class__) for var in var_tuple)
            result += coeff_str.format(coeff) + var_str
        return result.strip()

    def __eq__(self, other):
        """
        check equality of polynomials, monomials with zero coefficient are not considered,
        if other is a number and the polynomial is constant and has this value, we also consider them to be equal
        """
        if self._is_valid_coefficient(other):
            # we also return true also if a number is inserted and the polynomial is constant and has this value
            other = Polynomial({() : other})
        if isinstance(other, Polynomial):
            # monomials with 0 coefficient are not considered
            return super(Polynomial, self.remove_zero_coefficients()).__eq__(other.remove_zero_coefficients())
        return False

    def __ne__(self, other):
        """ check if objects are not equal, overwrites dicts not equal to use polynomials equal implementation """
        return not self.__eq__(other)

    def _warn_different_types(self, poly2):
        """ check for different types of polynomials, because of inheritance there might be more than one """
        # pylint: disable=unidiomatic-typecheck  # Check for the exact type, excluding subtypes
        if type(self) is Polynomial and not type(poly2) is Polynomial:
            poly2_type = type(poly2).__name__
            warn(WARNING_CAST.format(poly2_type), stacklevel=3)

    def __add__(self, poly2):
        """ add another polynomial or a scalar """
        result = dict(self)
        if self._is_valid_coefficient(poly2):
            _add_monomial(result, (), poly2)
        elif isinstance(poly2, Polynomial):
            self._warn_different_types(poly2)
            for var_tuple, coeff in poly2.items():
                var_tuple = self._format_variable_tuple(var_tuple)
                _add_monomial(result, var_tuple, coeff)
        else:
            try:
                return poly2.__add__(self)
            except TypeError as te:
                raise TypeError(ERROR_ADD) from te
        return self.__class__(result, variable_tuples_already_formatted=True)

    def __radd__(self, poly2):
        """ add self to another polynomial or a scalar """
        return self.__add__(poly2)

    def __sub__(self, poly2):
        """ subtract a polynomial or a scalar """
        return self.__add__(-1 * poly2)

    def __rsub__(self, poly2):
        """ subtract self from a polynomial or a scalar """
        return (-1 * self).__add__(poly2)

    def __mul__(self, poly2):
        """ multiply another polynomial or a scalar """
        if self._is_valid_coefficient(poly2):
            result = {var_tuple: coeff * poly2 for var_tuple, coeff in self.items()}
        elif isinstance(poly2, Polynomial):
            self._warn_different_types(poly2)
            result = {}
            for (vt1, c1), (vt2, c2) in product(self.items(), poly2.items()):
                var_tuple = self._format_variable_tuple(vt1 + vt2)
                _add_monomial(result, var_tuple, c1 * c2)
        else:
            try:
                return poly2.__mul__(self)
            except TypeError as te:
                raise TypeError(ERROR_MULTIPLY) from te
        return self.__class__(result, variable_tuples_already_formatted=True)

    def __rmul__(self, poly2):
        """ multiply self to another polynomial or a scalar """
        return self.__mul__(poly2)

    def __truediv__(self, other):
        """ dividing by scalar """
        if not self._is_valid_coefficient(other):
            raise TypeError(ERROR_DIVISOR)
        return self * (1 / other)

    def __pow__(self, exponent):
        """ raise to the power of the given integer exponent """
        if not isinstance(exponent, Integral):
            raise TypeError(ERROR_EXPONENT)
        result = 1
        for _ in range(exponent):
            result *= self
        return result

    def __contains__(self, variable_tuple):
        """ check whether the variables are contained as a monomial in the polynomial """
        return super().__contains__(self._format_variable_tuple(variable_tuple))

    def __getitem__(self, variable_tuple):
        return super().__getitem__(self._format_variable_tuple(variable_tuple))

    def get(self, variable_tuple, default=None):
        """ get the coefficient of the corresponding monomial in the polynomial """
        # but we catch the case where the variable monomial is given but by the formatting results in the empty tuple
        formatted_tuple = self._format_variable_tuple(variable_tuple)
        if variable_tuple and not formatted_tuple:
            return 0
        return super().get(formatted_tuple, default)

    def sort_entries(self):
        """ does not change the polynomial but the ordering of its entries in the dict, mainly for nice output """
        sorted_poly = sort_poly_dict(self)
        super().clear()
        super().update(sorted_poly)

    def copy(self) -> Self:
        """ get a copy of the polynomial """
        return self.__class__(self, variable_tuples_already_formatted=True)

    def is_constant(self):
        """ check if the polynomial contains at maximum the offset entry, hence a tuple of length 0 """
        return self.degree == 0

    def is_linear(self):
        """ check if the polynomial has a degree of at most 1 """
        return self.degree <= 1

    def is_quadratic(self):
        """ check if the polynomial has a degree of at most 2 """
        return self.degree <= 2

    def has_int_coefficients(self, precision=1e-9):
        """
        check if all coefficients of the polynomial are integers up to a certain precision

        :param (Real) precision: the deviation up to which values are considered to be integers
        """
        return self.maximum_int_deviation < precision

    def is_flat(self):
        """ check if the polynomial has only integer variables """
        return self.var_type is None or issubclass(self.var_type, Integral)

    def is_compact(self):
        """ check if the polynomial has integer variables which are consecutive starting with 0 """
        return variables.are_consecutive(self.variables)

    def get_variable_num(self):
        """ get the number of variables """
        return len(self.variables)

    def get_coefficient(self, *variables_in_monomial):
        """ get the coefficient for the tuple of variables or if not present 0 """
        return self.get(variables_in_monomial, 0)

    def get_coefficients_info_by_degree(self, degree=1):
        """
        extract the interesting information for the coefficients list of a certain degree

        :param (int) degree: the degree of the polynomial for which the coefficients info should be extracted
        :return: the coefficients info
        """
        if not degree or degree <= 0:
            raise ValueError(ERROR_DEGREE)
        if degree > len(self.coefficients_lists) - 1:
            return {}
        suffix = f"_degree_{degree}"
        return get_info(self.coefficients_lists[degree], suffix)

    def get_all_coefficients_info(self):
        """ extract the interesting information from several coefficients lists and combine the dictionaries """
        info_by_degree = {}
        for degree in range(1, len(self.coefficients_lists)):
            info_by_degree.update(self.get_coefficients_info_by_degree(degree))
        info_by_degree.update(self.coefficients_info)
        return info_by_degree

    def remove_zero_coefficients(self):
        """ remove all monomials with coefficients 0 from this polynomial """
        filtered = {var_tuple: coeff for var_tuple, coeff in self.items() if coeff != 0}
        return self.__class__(filtered, variable_tuples_already_formatted=True)

    def affine_transform(self, coefficient, offset=0):
        """
        apply the following transformation to every variable x: x -> (coefficient * x + offset)

        :param (Real) coefficient: linear coefficient of the transformation function
        :param (Real) offset: constant term of the transformation function
        :return: the new Polynomial resulting from the transformation or value if the final Polynomial is constant
        """
        transformations = {var: Polynomial({(var,): coefficient, (): offset}, variable_tuples_already_formatted=True)
                           for var in self.variables}
        return self.evaluate(transformations)

    @classmethod
    def _is_valid_var_assignment(cls, var_assignment):
        """
        check whether the given input can be assigned to the variable,
        that means it is a Polynomial, SCIP Expr or valid coefficient
        """
        return isinstance(var_assignment, (Polynomial, Expr)) or cls._is_valid_coefficient(var_assignment)

    def evaluate(self, var_assignments, keep_poly=False):
        """
        substitute all variables v with var_assignment[v], where var_assignment[v] can be either a value or Polynomial,
        the var_assignment can contain all or just a subset of the variables,
        if the Polynomial is flat, the var_assignment can also be a list with indices according to the variables

        if there is a Polynomial in the variable assignment the result will be a Polynomial,
        otherwise inherited classes will be kept (e.g. PolyIsing), if the result is constant a number will be returned

        this method can also be used to evaluate a SCIP Expr, however, in this case all variables need an assignment!

        :param (dict or list) var_assignments: mapping from variables to values or Polynomials
        :param (bool) keep_poly: if True, force to keep the result as an object of the polynomial class
                                 even if it evaluates to a constant
        :return: the new Polynomial resulting from the evaluation or value if the final Polynomial is constant
        """
        if isinstance(var_assignments, list):
            var_assignments = dict(enumerate(var_assignments))
        if any(not self._is_valid_var_assignment(va) for va in var_assignments.values()):
            raise ValueError(ERROR_ASSIGN)

        # we can only keep the originally inherited class type (e.g. PolyIsing), if we only evaluate numbers
        all_numbers = all(self._is_valid_coefficient(va) for va in var_assignments.values())
        resulting_type = self.__class__ if all_numbers else Polynomial
        try:
            result = sum(_get_evaluated_poly(*monomial, var_assignments, resulting_type) for monomial in self.items())
        except TypeError as te:
            raise ValueError(ERROR_KEPT) from te

        # check if the resulting Polynomial is just a constant, in this case only return the value, if not keep_poly
        if isinstance(result, Polynomial):
            result = result.remove_zero_coefficients()
            if result.is_constant() and not keep_poly:
                return result.get((), 0)
        if self._is_valid_coefficient(result) and keep_poly:
            return self.__class__({(): result})
        return result

    def replace_variables(self, replacement):
        """
        replace the variables in the polynomial with other variables

        :param (list or tuple or dict or function) replacement: mapping to the new variables,
                                                                if replacement is a dictionary, it should be of format
                                                                    {old_var : new_var},
                                                                can only be a list if the polynomial is flat
        :return: the new Polynomial with replaced variables
        """
        if isinstance(replacement, (list, tuple)):
            replacement = dict(enumerate(replacement))

        # here replacement of format {old_var : new_var} or function : old_var -> new_var
        result = {}
        for var_tuple, coeff in self.items():
            # e.g. from var_tuple (('x', 1), ('x', 2)) will get (0, 1) with replacement {('x', 1): 0, ('x', 2): 1}
            _add_monomial(result, variables.replace_in_tuple(var_tuple, replacement), coeff)
        try:
            return self.__class__(result)
        except TypeError as te:
            assert te.args[0].startswith(EXPECTED)
            raise ValueError(ERROR_REPLACE) from te

    def replace_variables_by_ordering(self, ordered_variables, check_all=True):
        """
        replace the variables in the polynomial by the index at which they appear in the provided list,
        if the list is complete the resulting polynomial will be compact

        :param (list) ordered_variables: list of variables of polynomial
        :param (bool) check_all: if True, checks if the given list is complete meaning all variables need a replacement,
                                 if False, only subset of variables can be replaced, they however need to have the same
                                 type as the original ones
        :return: the new Polynomial with replaced variables
        """
        if check_all:
            assert len(ordered_variables) >= self.get_variable_num()
            assert set(ordered_variables) >= set(self.variables)
        replacement = {var: i for i, var in enumerate(ordered_variables)}
        return self.replace_variables(replacement)

    def compact(self):
        """
        replace the variables in the polynomial with a consecutive indexing starting at 0,
        the indices are taken from sorting of the list of variables of the original polynomial

        :return: the new Polynomial with compact variables
        """
        return self.replace_variables_by_ordering(self.variables, False)

    def round(self, decimal_cap=None):
        """
        round the coefficients of the polynomial according to the decimal cap

        :param (int or None) decimal_cap: the number of digits of the resulting coefficients,
                                          if None, they will be ints
        :return: the new Polynomial with rounded coefficients
        """
        result = {}
        for var_tuple, coeff in self.items():
            result[var_tuple] = round(coeff, decimal_cap)
        return self.__class__(result, variable_tuples_already_formatted=True)

    def preprocess(self, preprocess_rule, unambitious=False):
        """
        simplify the polynomial according to the preprocessing rule,
        this means some variables are set to the values which are guaranteed to appear in an optimal solution

        :param (function) preprocess_rule:
            method which provides a mapping from variable sigmas and coefficient to the value to which the variable
            should be assigned, if it returns None, the variable will not be preprocessed
        :param (bool) unambitious:
            if True, only those variables will be set where their assignment is unambitious, that means, in all optimal
            solutions, they have the same value,
            if False, preprocess the variable to the straightforward value whether it might also get another value in an
            optimal solution, the objective values remains the same
        :return: the new reduced Polynomial and the assignment of the eliminated variables with variable to value
        """
        result = self.remove_zero_coefficients()

        sth_changed = True
        preprocessed_vars = {}
        while sth_changed:
            sth_changed = False
            current_pp_vars = {}
            for var in result.variables:
                coeff = result.get_coefficient(var)
                var_value = preprocess_rule(result.sigmas[var], coeff, unambitious)
                if var_value is not None:
                    current_pp_vars[var] = var_value
            if current_pp_vars:
                result = result.evaluate(current_pp_vars)
                sth_changed = not is_constant(result)
                preprocessed_vars.update(current_pp_vars)
        return result, preprocessed_vars

    def get_matrix_representation(self, num_variables=None):
        """ get the standard matrix representation of the polynomial """
        if not self.is_quadratic():
            raise ValueError(ERROR_QUADRATIC)
        if not self.is_flat():
            raise ValueError(ERROR_FLAT)
        if not self.is_compact():
            if not num_variables or num_variables < max(self.variables) + 1:
                raise ValueError(ERROR_COMPACT)
        if self.offset != 0:
            warn(WARNING_CONSTANT.format(self.offset))

        num_variables = num_variables or self.get_variable_num()
        linear = np.array([self.get_coefficient(i) for i in range(num_variables)])
        quadratic = np.array([[self.get_coefficient(i, j) if i >= j else 0
                               for i in range(num_variables)]
                              for j in range(num_variables)])
        return linear, quadratic

    @classmethod
    def get_from_matrix_representation(cls, *matrices):
        """
        get the polynomial from the standard matrix formulation

        :param matrices: arrays of different dimensions with equal size
        """
        poly = cls()
        for matrix in matrices:
            matrix = np.array(matrix)
            if len(matrix.shape) == 1:
                poly += cls(dict(enumerate(matrix)))
            if len(matrix.shape) == 2:
                poly += cls({(i, j) : val for i, ll in enumerate(matrix) for j, val in enumerate(ll)})
            if len(matrix.shape) > 2:
                raise ValueError(ERROR_MATRIX)
        return poly.remove_zero_coefficients()

    @classmethod
    def read_from_string(cls, string):
        """
        read in a polynomial from a string of the form, e.g.,
            '9 + 30.1 x1 - 25 x1^3 + 36*x2 + 60 x1 x2 + 36 x2^2 + 18 x1 x3'

        WARNING: Experimental status
        """
        # remove whitespace and multiplications
        parsed = string.replace(" ", "").replace("\n", "").replace("*", "").replace("-", "+-")
        monomials = [m for m in parsed.split('+') if m]  # take non-empty terms

        result = {}
        for m in monomials:
            factors = m.split('x')
            if factors[0] in ['', '-']:
                factors[0] = factors[0] + '1'
            coeff = float(factors[0])
            var_tuple = ()
            for f in factors[1:]:
                var_str, _, exp_str = f.partition('^')
                if exp_str.count('^'):
                    raise ValueError(ERROR_DOUBLE)
                var = int(var_str)
                exp = int(exp_str) if exp_str else 1
                var_tuple += tuple([var] * exp)
            result[var_tuple] = result.get(var_tuple, 0) + coeff
        return cls(result)

    def get_graph(self):
        """ get a graph representing the connectivity """
        if not self.is_quadratic():
            raise ValueError(ERROR_QUADRATIC)
        graph = nx.Graph()
        graph.add_nodes_from(self.linear_plain.keys())
        graph.add_edges_from(self.quadratic.keys())
        return graph


def is_constant(value_or_poly):
    """ check if the given object is either a number or a constant polynomial """
    return isinstance(value_or_poly, Real) or (isinstance(value_or_poly, Polynomial) and value_or_poly.is_constant())

def sort_poly_dict(poly_dict, reverse_monomial_degree_order=False):
    """ sort the polynomial dictionary according to the structure of the monomials """
    sorted_1 = _try_sorted(poly_dict.items(), key=lambda x: x[0])
    return dict(_try_sorted(sorted_1, key=lambda x: len(x[0]), reverse=reverse_monomial_degree_order))

def _try_sorted(iterable, key=None, reverse=False):
    """ try sorting and provide meaningful error in case it fails """
    try:
        if key:
            return sorted(iterable, key=key, reverse=reverse)
        return sorted(iterable)
    except TypeError as te:
        assert "'<' not supported" in te.args[0]
        raise ValueError(ERROR_SORTING) from te

def _add_monomial(poly_dict, var_tuple, coeff):
    """
    add a monomial (coeff * variables) to the dictionary of the polynomial

    :param (dict) poly_dict: dictionary of a polynomial with already formatted keys
    :param (tuple) var_tuple: has to be a formatted tuple of variables, can be empty for the constant term
    :param (Real) coeff: valid coefficient
    """
    poly_dict[var_tuple] = poly_dict.get(var_tuple, 0) + coeff

def _get_evaluated_poly(var_tuple, coeff, var_assignments, resulting_type):
    """ evaluate a single monomial with the given variable assignments """
    if coeff == 0:
        return 0

    term = coeff
    kept_vars = ()
    for var in var_tuple:
        if var in var_assignments.keys():
            # might have e.g. type(term) == PolyIsing and type(var_assignment[var]) == Polynomial
            # causes a warning, which we ignore, as in this case the convention is to return just a Polynomial
            # at this point we can only have either a number or a Polynomial (or a SCIP Expr)
            term *= var_assignments[var]
        else:
            kept_vars += (var,)
    if kept_vars:
        term *= resulting_type({kept_vars: 1})
    return term

def get_info(values, suffix='', precision_digits=9):
    """
    extract the interesting information from the list of values

    :param (list) values: the list of values
    :param (str) suffix: the suffix added to the keywords for differing degrees
    :param (int) precision_digits: the number of digits for the precision
    :return:
    """
    kwargs = [kw + suffix for kw in VALUES_INFO_KWARGS]
    return dict(zip(kwargs, _get_info_values(values, precision_digits)))

def _get_info_values(values, precision_digits=9):
    """
    extract the interesting values from the list of values

    :param (list) values: list of values
    :param (int) precision_digits: the number of digits for the precision
    :return: tuple (min non-zero absolute value among all values,
                    max non-zero absolute value among all values,
                    min difference between any two values,
                    min difference between any two absolute values,
                    max absolute value / min absolute value,
                    max absolute value / min differance,
                    max absolute value / min absolute difference)
    """
    if not values:
        return (0,) * 7
    precision = 10 ** (-precision_digits)

    sorted_values = sorted(set(values + [0]))
    min_dist = float('inf')
    for i in range(len(sorted_values) - 1):
        dist = sorted_values[i + 1] - sorted_values[i]
        if dist < min_dist and abs(dist) > precision:
            min_dist = dist

    sorted_absolute_values = sorted(set(abs(value) for value in sorted_values if abs(value) > precision))
    min_abs_value = sorted_absolute_values[0]
    max_abs_value = sorted_absolute_values[-1]

    min_abs_dist = min_abs_value  # distance to 0
    for i in range(len(sorted_absolute_values) - 1):
        dist = sorted_absolute_values[i + 1] - sorted_absolute_values[i]
        if dist < min_abs_dist and abs(dist) > precision:
            min_abs_dist = dist

    max_min_ratio = max_abs_value / min_abs_value
    max_dist_ratio = max_abs_value / min_dist
    max_abs_dist_ratio = max_abs_value / min_abs_dist
    values = min_abs_value, max_abs_value, min_dist, min_abs_dist, max_min_ratio, max_dist_ratio, max_abs_dist_ratio
    rounded_values = tuple(round(value, precision_digits) for value in values)
    return rounded_values
