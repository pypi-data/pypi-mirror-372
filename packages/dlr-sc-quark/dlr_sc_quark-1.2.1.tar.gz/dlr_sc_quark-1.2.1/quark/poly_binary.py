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

""" module for PolyBinary """

from collections import Counter
from functools import cached_property
from warnings import warn
from itertools import combinations

from .polynomial import Polynomial, sort_poly_dict
from . import poly_ising
from .utils.variables import to_string


ADD       = "add"
MULTIPLY  = "multiply"
REDUCTION = "reduction"
X         = "x"

ERROR_ISING      = "Cannot {} PolyBinary and PolyIsing"
ERROR_DEGREE     = "Not applicable for polynomials with degree larger than 2"
ERROR_UPPER      = "Upper bound needs to be larger than or equal to lower bound"
ERROR_INPUT      = "Either provide upper_bound or num_variables"
ERROR_MAX_DEGREE = "Provide integer max_degree larger than 0 or set to None to not use automatic reduction"

WARNING_VARS   = "Variables are replaced by tuple variables"
WARNING_IGNORE = "With upper_bound given, num_variables is ignored"

STRAIGHT = "straight"
SIMPLE   = "simple"
MEDIUM   = "medium"
BETTER   = "better"


class PolyBinary(Polynomial):
    """
    A binary polynomial is a special polynomial, where the variables can only take 0 or 1.
    Since 0^2 = 0 and 1^2 = 1, we can simplify the Polynomial by removing all exponents,
    e.g.

        * (0, 0, 1, 1, 1): 1 -> (0, 1): 1,
        * (2, 2, 2, 2): 2    -> (2,): 2.

    We have the following conventions:

        *  PolyBinary == PolyBinary <=> poly == poly,
        *  PolyBinary == Polynomial <=> poly == poly,
        *  PolyBinary +/* Polynomial = PolyBinary,
        *  Polynomial +/* PolyBinary = Polynomial + Warning,
        *  PolyIsing +/* PolyBinary = Error,
        *  copy/remove_zero_coefficients/replace_variables/get_rounded(PolyBinary) = PolyBinary,
        *  evaluate(PolyBinary, {var : Number}) = PolyBinary/Number,
        *  evaluate(PolyBinary, {var : Polynomial}) = Polynomial,
        *  evaluate(PolyBinary, {var : PolyBinary}) = Error,
        *  PolyBinary == PolyIsing = False.
    """

    @cached_property
    def positive(self):
        """ part of the polynomial with positive coefficients without offset """
        return self.__class__({var_tuple: coeff for var_tuple, coeff in self.items() if coeff > 0 and var_tuple},
                              variable_tuples_already_formatted=True)

    @cached_property
    def negative(self):
        """ part of the polynomial with negative coefficients without offset """
        return self.__class__({var_tuple: coeff for var_tuple, coeff in self.items() if coeff < 0 and var_tuple},
                              variable_tuples_already_formatted=True)

    @cached_property
    def naive_upper_bound(self):
        """
        a naive upper bound derived from the sum of all positive coefficients,
        it is a worst-case estimation and in general only tight, if the polynomial is linear,
        as it does not exploit any deeper structure in the polynomial
        """
        return sum(self.positive.values()) + self.offset

    @cached_property
    def naive_lower_bound(self):
        """
        returns a naive lower bound derived from the sum of all negative coefficients,
        it is a worst-case estimation and in general only tight, if the polynomial is linear,
        as it does not exploit any deeper structure in the polynomial
        """
        return sum(self.negative.values()) + self.offset

    def _format_variable_tuple(self, var_tuple):
        """
        transform the tuple of variables into the standard format, also checks the type of the variables,
        extends 'Polynomial._format_variable_tuple',
        since we have x * x = x  for all x in {0, 1}, all powers can be removed
        """
        var_tuple = super()._format_variable_tuple(var_tuple)
        var_tuple = tuple(sorted(set(var_tuple)))
        return var_tuple

    def __eq__(self, other):
        """
        check equality of polynomials, where PolyIsing is never equal to a PolyBinary,
        extends 'Polynomial.__eq__'
        """
        if isinstance(other, poly_ising.PolyIsing):
            return False
        return super().__eq__(other)

    @staticmethod
    def _check_different(poly2, func_name):
        """ check if the type of the second Polynomial is feasible for an operation """
        if isinstance(poly2, poly_ising.PolyIsing):
            raise ValueError(ERROR_ISING.format(func_name))

    def __add__(self, poly2):
        """
        add another polynomial or a scalar,
        extends 'Polynomial.__add__' since PolyIsing cannot be added to PolyBinary
        """
        self._check_different(poly2, ADD)
        return super().__add__(poly2)

    def __mul__(self, poly2):
        """
        multiply with another polynomial or a scalar,
        extends 'Polynomial.__mul__' since PolyIsing cannot be multiplied with PolyBinary
        """
        self._check_different(poly2, MULTIPLY)
        return super().__mul__(poly2)

    @classmethod
    def _is_valid_var_assignment(cls, var_assignment):
        """
        check whether the given input can be assigned to the variable,
        that means it is a Polynomial, PolyBinary, SCIP Expr or valid coefficient,
        extends 'Polynomial._is_valid_var_assignment' to not allow for PolyIsing
        """
        return not isinstance(var_assignment, PolyBinary) and super()._is_valid_var_assignment(var_assignment)

    def is_non_negative(self):
        """
        check if the polynomial has only non-negative coefficients
        and thus always evaluates to non-negative values
        """
        return all(coeff >= 0 for coeff in self.values())

    def get_matrix_representation(self, num_variables=None):
        """
        get the polynomial in the standard matrix representation

        :return: the quadratic matrix of the standard representation
        """
        linear, quadratic = super().get_matrix_representation(num_variables)
        for i, value in enumerate(linear):
            quadratic[i, i] = value
        return quadratic

    # additional methods for binary polynomials

    @classmethod
    def from_unknown_poly(cls, poly):
        """
        convert a polynomial of unknown type into a PolyBinary

        :param (Polynomial) poly: the polynomial of unknown type
        :return: the corresponding binary polynomial
        """
        return poly.to_binary() if isinstance(poly, poly_ising.PolyIsing) else cls(poly)

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

    def to_ising(self, inverted=False):
        """
        convert the binary polynomial to the Ising format

        :param (bool) inverted: if False, use conversion 0 -> -1, 1 -> 1 with x = 0.5s + 0.5,
                                if True, use conversion  0 -> 1, 1 -> -1 with x = -0.5s + 0.5
        :return: the corresponding PolyIsing
        """
        converted = self.affine_transform(-0.5, 0.5) if inverted else self.affine_transform(0.5, 0.5)
        return poly_ising.PolyIsing(converted, inverted)

    def reduce(self, max_degree=1, use=None, reduction_variable_prefix=(REDUCTION,), reduction_strategy=None):
        """
        reduce the polynomial by substituting every variable product with a new variable until it is quadratic
        and get the corresponding penalty terms enforcing the reduction

        :param (int or None) max_degree: the maximal degree of the final polynomial,
                                         if None only the given reductions are applied
        :param (list[tuples] or set[tuples] or None) use: the predefined reductions which shall be used,
                                                          set with tuples in the format (var1, var2, reduction_var)
        :param (tuple or str) reduction_variable_prefix: prefix for the additional reduction variables that are created
        :param (str or None) reduction_strategy: the strategy how to choose the next variable pair
        :return: the reduced polynomial, the dictionary of penalty terms enforcing the reductions
        """
        if max_degree is not None and (not isinstance(max_degree, int) or max_degree < 1):
            raise ValueError(ERROR_MAX_DEGREE)

        max_degree = max_degree or self.degree
        poly = _apply_reduction(self, use)  # try here already in case the reductions are on flat variables
        if poly.degree <= max_degree:
            return poly, []

        if self.is_flat():
            # in the following we need to introduce new variables which are of type tuple
            # as we cannot mix up different types of variables we need to rename the flat variables
            warn(WARNING_VARS)
            poly = poly.replace_variables(lambda i: (X, i))
        elif self.var_type == str:
            warn(WARNING_VARS)
            poly = poly.replace_variables(lambda s: (s,))
        if not isinstance(reduction_variable_prefix, tuple):
            reduction_variable_prefix = (reduction_variable_prefix,)

        # try again in case the reductions are on non-flat variables
        poly = _apply_reduction(poly, use)
        return _reduce_poly_successively(poly, max_degree, reduction_variable_prefix, reduction_strategy)


def preprocess_rule(var_sigmas, coeff, unambitious=False):
    """
    very simple preprocessing function:
    if the weight of the variable is positive and extends the influence of incoming negative couplings,
    the variable can be assigned to 0,
    if the weight is negative and extends the influence of incoming positive couplings, can be assigned to 1

    :param (tuple) var_sigmas: sigma values (combined incoming strengths) of a variable of the polynomial
    :param (Real) coeff: coefficient on the linear term of the variable
    :param (bool) unambitious: if True, only those variables will be set where their assignment is unambitious,
                               that means, in all optimal solutions, they have the same value,
                               if False, preprocess the variable to the straightforward value whether it might also
                               get another value in an optimal solution, the objective values remains the same
    :return: the solution value or None if the variable cannot be preprocessed
    """
    if unambitious and coeff == -var_sigmas[1]:
        return None
    if coeff >= -var_sigmas[1]:
        return 0
    if coeff <= -var_sigmas[0]:
        return 1
    return None


def _apply_reduction(poly, reductions):
    if not reductions:
        return poly
    reductions = [reduction for reduction in reductions if len(reduction) == 3]
    change = True
    poly_dict = poly
    while change:
        # we need to have several iterations as reductions might be based upon each other
        for reduction_var, var1, var2 in reductions:
            poly_dict, change = _replace_variable_pair(poly_dict, var1, var2, reduction_var, return_change=True)
    return PolyBinary(poly_dict)

def _reduce_poly_successively(poly_dict, max_degree, reduction_variable_prefix, reduction_strategy):
    reductions = []
    poly_dict = sort_poly_dict(poly_dict, reverse_monomial_degree_order=True)  # sorted by decreasing monomial degrees
    current_degree = len(next(iter(poly_dict.keys())))

    while current_degree > max_degree:
        reduction_strategy = SIMPLE if current_degree <= 2 else (reduction_strategy or SIMPLE)
        var1, var2 = _get_best_variable_pair(poly_dict, current_degree, max_degree, strategy=reduction_strategy)
        reduction_var = reduction_variable_prefix + var1 + var2
        poly_dict = _replace_variable_pair(poly_dict, var1, var2, reduction_var)
        reductions.append((reduction_var, var1, var2))
        current_degree = max(map(len, poly_dict.keys()))
    return PolyBinary(poly_dict), sorted(set(reductions))

def _get_best_variable_pair(poly_dict, degree, max_degree, strategy=BETTER):
    if strategy == STRAIGHT:
        # simply get the first variable pair in the first monomial with degree larger than max_degree
        monomials = iter(poly_dict.keys())
        monomial = next(monomials)
        while len(monomial) <= max_degree:
            value = poly_dict.pop(monomial)
            poly_dict[monomial] = value  # append the monomial at the end of the poly dict again
            monomial = next(monomials)
        var1, var2 = monomial[0:2]
        return var1, var2

    if strategy == SIMPLE:
        # get the largest monomial (or one of them) and from it the first variable pair
        max_monomial = max(poly_dict.keys(), key=len)
        var1, var2 = max_monomial[0:2]
        return var1, var2

    if strategy == MEDIUM:
        # get the variable pair which appears in the most monomials of the largest degree
        max_var_pairs = sum((list(combinations(var_tuple, 2))
                            for var_tuple in poly_dict.keys() if len(var_tuple) == degree), start=[])
        return Counter(max_var_pairs).most_common(1)[0][0]

    if strategy == BETTER:
        # get the variable pair which appears most in all monomials
        all_var_pairs = sum((list(combinations(var_tuple, 2)) for var_tuple in poly_dict.keys()), start=[])
        return Counter(all_var_pairs).most_common(1)[0][0]

    raise ValueError(f"Unknown strategy '{strategy}'")

def _replace_variable_pair(poly_dict, var1, var2, reduction_var, return_change=False):
    reduced_poly_dict = {}
    change = False
    for var_tuple, coeff in poly_dict.items():
        if var1 in var_tuple and var2 in var_tuple:
            # the new variable tuple has the reduction variable at the end, which prefers non-reduction variables later,
            # this is kept until the polynomial is instantiated, then the variable tuples might be resorted
            new_var_tuple = tuple(var for var in var_tuple if var not in [var1, var2]) + (reduction_var,)
            reduced_poly_dict[new_var_tuple] = reduced_poly_dict.get(new_var_tuple, 0) + coeff
            change = True
        else:
            reduced_poly_dict[var_tuple] = reduced_poly_dict.get(var_tuple, 0) + coeff
    return reduced_poly_dict if not return_change else (reduced_poly_dict, change)


REDUCTION_PENALTY_POLY_FULL = PolyBinary({(0,): 3, (0, 1): -2, (0, 2): -2, (1, 2): 1}) # +3 x0 -2 x0 x1 -2 x0 x2 + x1 x2

def get_reduction_penalty_polynomial(product_xy, factor_x, factor_y):
    """
    get the quadratic polynomial that enforces a variable to be equal to the product of two variables
    (the variables need to be of the same type, thus either tuple, int or str)

    :param (tuple or int or str) product_xy: new binary variable that substitutes x*y
    :param (tuple or int or str) factor_x: first binary variable
    :param (tuple or int or str) factor_y: second binary variable
    :return: the PolyBinary that is zero if x * y = xy and positive otherwise
    """
    return REDUCTION_PENALTY_POLY_FULL.replace_variables([product_xy, factor_x, factor_y])

def get_all_reduction_penalty_terms(reductions):
    """
    get the corresponding penalty terms to the reductions

    :param (list[tuple]) reductions: list of 3-tuples with reduction variables
    :return: the penalty terms to enforce the reductions
    """
    penalty_terms = {}
    for reduction_var, var1, var2 in reductions:
        reduction_name = to_string(reduction_var)
        penalty_terms[reduction_name] = get_reduction_penalty_polynomial(reduction_var, var1, var2)
    return penalty_terms


def get_binary_representation_polynomial(upper_bound=None, lower_bound=0, num_variables=None, variable_prefix=(X,),
                                         split_signs=False):
    """
    get the linear polynomial representing an integer variable bounded between the lower bound and the upper bound
    using the binary representation with binary variables,
    the polynomial will be empty if upper_bound == lower_bound == 0,
    by providing the number of desired variables instead, the polynomial will represent integer numbers up to 2**n-1

    :param (Integer) upper_bound: value of the upper bound, can be 0 but not negative unless the lower bound is also set
    :param (Integer) lower_bound: value of the lower bound
    :param (Integer) num_variables: the number of binary variables to be used
    :param (tuple or str) variable_prefix: prefix for the binary variables that are created
    :param (bool) split_signs: if the lower bound is negative and the upper bound is positive,
                               the negative part and the positive part will be treated separately,
                               this leads to more variables but no constant and lower absolute coefficients,
                               note that this also means the representation of a value is not unique anymore
    :return: the linear polynomial representing the integer variable
    """
    if upper_bound is None and not num_variables:
        raise ValueError(ERROR_INPUT)
    if upper_bound is not None and num_variables:
        warn(WARNING_IGNORE)
        num_variables = None
    if upper_bound and upper_bound < lower_bound:
        raise ValueError(ERROR_UPPER)

    if not isinstance(variable_prefix, tuple):
        variable_prefix = (variable_prefix,)

    if lower_bound and upper_bound:
        diff = upper_bound - lower_bound
        if upper_bound <= 0:
            # invert to get the lowest possible constant and shift
            return -1 * get_binary_representation_polynomial(diff, 0, None, variable_prefix) + upper_bound
        if split_signs:
            positive_part = get_binary_representation_polynomial(upper_bound, 0, None, variable_prefix + ("+",))
            negative_part = -1 * get_binary_representation_polynomial(-lower_bound, 0, None, variable_prefix + ("-",))
            return positive_part + negative_part
        # shift bounds to use as few variables as possible
        return get_binary_representation_polynomial(diff, 0, None, variable_prefix) + lower_bound

    num_variables = num_variables or int(upper_bound).bit_length() - 1
    poly = PolyBinary({((*variable_prefix, i),): 2 ** i for i in range(num_variables)})
    if not upper_bound:
        return poly

    remaining = upper_bound - 2 ** num_variables + 1
    return poly + PolyBinary({((*variable_prefix, num_variables),): remaining})

def get_unary_representation_polynomial(upper_bound, lower_bound=0, variable_prefix=(X,)):
    """
    get the linear polynomial representing an integer variable bounded between the lower bound and the upper bound
    using the unary representation with binary variables,
    the polynomial will be empty if upper_bound == lower_bound == 0

    :param (Integer) upper_bound: value of the upper bound, can be 0 but not negative unless the lower bound is also set
    :param (Integer) lower_bound: value of the lower bound
    :param (tuple or str) variable_prefix: prefix for the binary variables that are created
    :return: the linear polynomial representing the integer variable
    """
    if upper_bound and upper_bound < lower_bound:
        raise ValueError(ERROR_UPPER)

    if not isinstance(variable_prefix, tuple):
        variable_prefix = (variable_prefix,)

    if upper_bound < 0:
        # without the mirroring to the negative numbers the constant would be much larger
        return -1 * get_unary_representation_polynomial(-1 * lower_bound, -1 * upper_bound, variable_prefix)
    poly = PolyBinary({((*variable_prefix, i),): 1 for i in range(upper_bound - lower_bound)})
    if lower_bound:
        poly += lower_bound
    return poly
