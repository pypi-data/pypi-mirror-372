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

""" module for ConstraintBinary """

from numbers import Real
from warnings import warn, catch_warnings, warn_explicit

from .poly_binary import PolyBinary, Polynomial, get_binary_representation_polynomial, get_all_reduction_penalty_terms
from .utils.variables import to_string


CONSTRAINT = "constraint"
SLACK      = "slack"
REDUCTION  = "reduction"
X          = "x"
ORIGINAL   = "original"

ERROR_CONSTANT      = "Constant must be a number"
ERROR_BOTH          = "At least one bound needs to be given"
ERROR_LOWER         = "Lower bound must be less than or equal to upper bound"
ERROR_UNFULFILLABLE = "Unfulfillable constraint '{}'"
ERROR_INT           = "Inequality constraint must have integer coefficients and boundaries"
ERROR_POSITIVE      = "Positive coefficients do not suffice to get above the lower bound"
ERROR_NEGATIVE      = "Negative coefficients do not suffice to get below the upper bound"
ERROR_BINARY        = "At the moment can only handle PolyBinary"
ERROR_LINEAR        = "Method only makes sense for linear polynomials"

WARNING_EQUAL_VARS = "The two variables '{}' and '{}' are set to be equal, consider replacing one with the other"
WARNING_NEG_VARS   = "The two variables '{}' and '{}' are set to be negations of each other, " \
                     "consider replacing one with '1 - other'"
WARNING_USELESS    = "Useless constraint '{}'"
WARNING_FLAT       = "Flat variables are replaced by tuple variables"
WARNING_ADVANCE    = "Variables could be set in advance: {}"
WARNING_SHARPEN    = "{} bound could be sharpened to {}"
WARNING_FORCE      = "Force is only necessary to get a fully linear problem"


class ConstraintBinary:
    """
    A constraint restricts the values of a function, here a polynomial.
    We define an inequality constraint with lower_bound <= polynomial <= upper_bound,
    where we have an equality constraint if lower_bound == upper_bound.
    """

    def __init__(self, polynomial, lower_bound=None, upper_bound=None, _check=True):
        """
        initialize ConstraintBinary object,
        if only one bound is given, the other is calculated by worst case estimation,
        note that this can result in hugh feasibility intervals,
        which lead to a large number of slack variables in the QUBO formulation

        :param (PolyBinary) polynomial: binary polynomial which is bounded
        :param (Real or None) lower_bound: value of the lower bound
        :param (Real or None) upper_bound: value of the upper bound
        :param (bool) _check: whether all the consistencies are checked, switch off only with care!
         """
        self._check_input(polynomial, lower_bound, upper_bound)
        self.polynomial = polynomial
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        if self.lower_bound is None:
            # worst case estimation of lower bound
            self.lower_bound = sum(polynomial.negative.values()) + polynomial.offset
        if upper_bound is None:
            # worst case estimation of upper bound
            self.upper_bound = sum(polynomial.positive.values()) + polynomial.offset

        if _check:
            self.check_consistency()

    @staticmethod
    def _check_input(polynomial, lower_bound, upper_bound):
        """ check whether the input is correct """
        if lower_bound is None and upper_bound is None:
            raise ValueError(ERROR_BOTH)
        if not isinstance(polynomial, PolyBinary):
            raise ValueError(ERROR_BINARY)

    def check_consistency(self):
        """ check if the data is consistent and defines a meaningful constraint """
        if self.lower_bound > self.upper_bound:
            raise ValueError(ERROR_LOWER)
        if self.polynomial.is_constant():
            if not self.lower_bound <= self.polynomial.offset <= self.upper_bound:
                # the polynomial only consisting of a constant is not in between the bounds
                raise ValueError(ERROR_UNFULFILLABLE.format(self))
            # if the constant is between the bounds, it is simply a useless constraint
            warn(WARNING_USELESS.format(self))
            return

        # check edge cases by sums of all positive and all negative coefficients
        # lb <= p+(x) + p-(x) + c <= ub
        if sum(self.polynomial.positive.values()) + self.polynomial.offset < self.lower_bound:
            # lb > p+(1) + c (can only happen if offset c is negative)
            raise ValueError(ERROR_POSITIVE)
        if sum(self.polynomial.negative.values()) + self.polynomial.offset > self.upper_bound:
            # p-(1) + c > ub (can only if offset c is positive, thus no contradiction with above)
            raise ValueError(ERROR_NEGATIVE)

        # other preprocessable cases
        self.get_preprocessable_variables(_raise_warning=True)

        # the reversed edge cases can be used to check the strengths of the bounds
        if (sum(self.polynomial.positive.values()) + self.polynomial.offset <= self.upper_bound) \
                and (sum(self.polynomial.negative.values()) + self.polynomial.offset >= self.lower_bound):
            # lb <= p-(1) + c <= p+(x) + p-(x) + c <= p+(1) + c <= ub
            warn(WARNING_USELESS.format(self))
        elif sum(self.polynomial.positive.values()) + self.polynomial.offset < self.upper_bound:
            warn(WARNING_SHARPEN.format("Upper", sum(self.polynomial.positive.values()) + self.polynomial.offset))
        elif sum(self.polynomial.negative.values()) + self.polynomial.offset > self.lower_bound:
            warn(WARNING_SHARPEN.format("Lower", sum(self.polynomial.negative.values()) + self.polynomial.offset))

    def __add__(self, constant):
        """
        shift the constraint by adding the constant to the polynomial, the lower_bound and the upper_bound

        :param (Real) constant: constant value to be added
        :return: the shifted constraint
        """
        if not isinstance(constant, Real):
            raise ValueError(ERROR_CONSTANT)
        return ConstraintBinary(self.polynomial + constant, self.lower_bound + constant, self.upper_bound + constant,
                                _check=False)

    def __sub__(self, constant):
        """
        shift the constraint by subtracting the constant from the polynomial, the lower_bound and the upper_bound

        :param (Real) constant: constant value to be subtracted
        :return: the shifted constraint
        """
        return self.__add__(constant * -1)

    def __mul__(self, constant):
        """
        scale the constraint by multiplying the constant to the polynomial, the lower_bound and the upper_bound

        :param (Real) constant: constant value to be multiplied
        :return: the scaled constraint
        """
        if not isinstance(constant, Real) or constant == 0:
            raise ValueError(ERROR_CONSTANT)
        lower_bound, upper_bound = self.lower_bound * constant, self.upper_bound * constant
        if constant < 0:
            lower_bound, upper_bound = upper_bound, lower_bound
        return ConstraintBinary(self.polynomial * constant, lower_bound, upper_bound, _check=False)

    def __eq__(self, other):
        """
        check equality of constraints, in the polynomial monomials with zero coefficient are not considered,
        as well as possible shifting and scaling of the constraints
        """
        if not isinstance(other, ConstraintBinary):
            return False
        if self.polynomial.var_type != other.polynomial.var_type:
            return False

        # direct comparison check
        normalized_self = self.normalize()
        normalized_other = other.normalize()
        if normalized_self.polynomial == normalized_other.polynomial \
            and normalized_self.upper_bound == normalized_other.upper_bound:
            return True
        # shifting/scaling check
        if normalized_self.polynomial:
            var_tuple, coeff_self = next(iter(normalized_self.polynomial.items()))
            if var_tuple not in normalized_other.polynomial:
                return False
            poly_scale = coeff_self / normalized_other.polynomial[var_tuple]
            return normalized_self.polynomial == normalized_other.polynomial * poly_scale \
                   and normalized_self.upper_bound == normalized_other.upper_bound * poly_scale
        return False

    def __repr__(self):
        """ get nicely formatted representation of the constraint """
        return self.__class__.__name__ + f"({repr(self.polynomial)}, {self.lower_bound}, {self.upper_bound})"

    def __str__(self, revert_eq=False):
        """ get human-readable representation of the constraint """
        if self.is_equality_constraint() and not revert_eq:
            return f"{self.polynomial} == {self.upper_bound:n}"
        if self.is_equality_constraint():
            return f"{self.upper_bound:n} == {self.polynomial}"
        return f"{self.lower_bound:n} <= {self.polynomial} <= {self.upper_bound:n}"

    def copy(self):
        """ get a copy of the constraint """
        return ConstraintBinary(self.polynomial.copy(), self.lower_bound, self.upper_bound, _check=False)

    def is_equality_constraint(self):
        """ check if the constraint is an equality constraint """
        return self.lower_bound == self.upper_bound

    def is_integer(self, precision=1e-9):
        """
        check if the lower bound, the upper bound and the coefficients of the polynomial are all integer

        :param (Real) precision: precision value until which values are considered to be integer
        :return: True if all values are integer
        """
        return self.polynomial.has_int_coefficients(precision) \
               and abs(self.lower_bound - int(self.lower_bound)) < precision \
               and abs(self.upper_bound - int(self.upper_bound)) < precision

    def is_normal(self):
        """ check if the constraint is in normalized format """
        return self.lower_bound == 0 and _is_first_monomial_non_negative(self.polynomial)

    def round(self, decimal_cap=None):
        """
        round the coefficients of the polynomial and the bounds of the constraint according to the decimal cap

        :param (int or None) decimal_cap: the number of digits of the resulting coefficients,
                                          if None, they will be ints
        :return: the new constraint with rounded bounds and polynomial
        """
        rounded_lower_bound = round(self.lower_bound, decimal_cap)
        rounded_upper_bound = round(self.upper_bound, decimal_cap)
        return self.__class__(self.polynomial.round(decimal_cap), rounded_lower_bound, rounded_upper_bound)

    def normalize(self):
        """
        get the constraint with the normalized format where lower_bound=0
        by subtracting the lower bound
        """
        if self.is_normal() and not any(coeff == 0 for coeff in self.polynomial.values()):
            return self
        constraint = self if _is_first_monomial_non_negative(self.polynomial) else (self * -1)
        constraint -= constraint.lower_bound
        constraint.polynomial = constraint.polynomial.remove_zero_coefficients()
        return constraint

    def replace_variables(self, replacement, _check=True):
        """
        replace the variables in the polynomial with other variables

        :param (list or dict or function) replacement: mapping to the new variables, if replacement is a dictionary, it
                                                       should be of format {old_var : new_var}, can only be a list if
                                                       the polynomial is flat
        :param (bool) _check: whether all the consistencies are checked, switch off only with care!
        :return: the new ConstraintBinary with replaced variables
        """
        return ConstraintBinary(self.polynomial.replace_variables(replacement), self.lower_bound, self.upper_bound,
                                _check=_check)

    def preprocess(self):
        """ replace preprocessable variables, if existing, in the constraint polynomial """
        preprocessable = self.get_preprocessable_variables()
        new_poly = self.polynomial.evaluate(preprocessable)
        new_poly = PolyBinary(new_poly).remove_zero_coefficients()

        if new_poly.is_constant() and self.lower_bound <= new_poly.offset <= self.upper_bound:
            # fully processed constraint -> remaining part would be a useless constraint
            return None, preprocessable
        return ConstraintBinary(new_poly, self.lower_bound, self.upper_bound), preprocessable

    def get_preprocessable_variables(self, _raise_warning=False):
        """
        get the variables in the polynomial that can be preprocessed
        due to a specific structure of the constraint
        """
        normalized_constrained = self.normalize()

        if self.is_equality_constraint() and len(self.polynomial.variables) == 2:
            preprocessable = _get_preprocessable_variables_eq_or_neg(normalized_constrained.polynomial, _raise_warning)
            if preprocessable:
                return preprocessable

        preprocessable0, preprocessable1 = _get_preprocessable_variables_bounds(normalized_constrained.polynomial,
                                                                                normalized_constrained.upper_bound)
        if not set(preprocessable0).isdisjoint(preprocessable1):
            # if one variable should be set to two different values, there is a contradiction in the constraint
            raise ValueError(ERROR_UNFULFILLABLE.format(self))

        preprocessable0.update(preprocessable1)
        if _raise_warning and preprocessable0:
            warn(WARNING_ADVANCE.format(preprocessable0))
        return preprocessable0

    def to_equality_constraint(self, slack_variable_prefix=(SLACK,)):
        """
        transform the constraint into an equality constraint by automatically introducing slack variables if necessary

        :param (tuple or str) slack_variable_prefix: prefix for the additional slack variables that are created
        :return: the equality constraint
        """
        normalized_constraint = self.normalize()
        if self.is_equality_constraint():
            return normalized_constraint
        if not isinstance(slack_variable_prefix, tuple):
            slack_variable_prefix = (slack_variable_prefix,)

        slack_polynomial = get_binary_representation_polynomial(normalized_constraint.upper_bound,
                                                                variable_prefix=slack_variable_prefix)
        return ConstraintBinary(normalized_constraint.polynomial - slack_polynomial, 0, 0)

    def get_reductions(self, max_degree=1, use=None, force=False, reduction_strategy=None):
        """
        get the reduced constraint and the corresponding reductions,
        if the constraint encodes a reduction itself, we also retrieve this if forced

        :param (int or None) max_degree: the maximal degree of the final polynomial,
                                         if None only the given reductions are applied
        :param (list[tuples] or None) use: the reductions which shall be used,
                                           as a list with tuples in the format (var1, var2, reduction_var)
        :param (bool) force: if True also reduce quadratic polynomials to linear that could remain for the QUBO problem
        :param (str) reduction_strategy: the method how the reduction pairs are found, by default the fastest version
        :return the reduced constraint, a list of variable triples representing the reductions
        """
        if (not max_degree or max_degree > 1) and force:
            warn(WARNING_FORCE)
            force = False

        # TODO: reduce number of calls of _match_special_constraint_get_penalty_poly
        if max_degree and not force and self.provides_penalty_term_directly(None):
            # if the constraint polynomial already provides a valid penalty term of any degree,
            # we only reduce its degree below 2 if forced
            max_degree = max(max_degree, 2)

        # check whether the constraint encodes a reduction itself
        reduction = retrieve_reduction(self)
        if reduction:
            if force or (max_degree and max_degree == 1 and self.polynomial.degree >= 2):
                # if we are forced or if we have the quadratic reduction constraint r == x * y and want linear
                return None, [reduction]
            # otherwise we keep the linear or quadratic constraints
            return self, []

        # use already given reductions
        reduced_poly, _ = self.polynomial.reduce(None, use, reduction_strategy=reduction_strategy)
        if max_degree and reduced_poly == self.polynomial and self.polynomial.degree <= max_degree:
            # nothing has changed and has to be changed
            return self, []

        # when this point is reached, simply reduce to given max degree
        reduced_poly, reductions = reduced_poly.reduce(max_degree, reduction_strategy=reduction_strategy)
        with catch_warnings(record=True) as warnings:
            reduced_constraint = ConstraintBinary(reduced_poly, self.lower_bound, self.upper_bound)
        for warning in warnings:
            if issubclass(warning.category, UserWarning) and warning.message.args[0].startswith("Useless constraint"):
                # in case we have created a useless constraint, we do not return it
                reduced_constraint = None
            else:
                warn_explicit(message=warning.message, category=warning.category, filename=warning.filename,
                              lineno=warning.lineno, source=warning.source)
        return reduced_constraint, reductions

    def reduce(self, max_degree=1, use=None, force=False, reduction_strategy=None, reduced_constraint_name=ORIGINAL):
        """
        get a new constraint with just a polynomial with at most the given degree by substituting products of variables

        :param (int or None) max_degree: the maximal degree of the final polynomial,
                                         if None only the given reductions are applied
        :param (list[tuples] or None) use: the reductions which shall be used,
                                           as a list with tuples in the format (var1, var2, reduction_var)
        :param (bool) force: if True also reduce quadratic polynomials to linear that could remain for the QUBO problem
        :param (str) reduction_strategy: the method how the reduction pairs are found, by default the fastest version
        :param (str) reduced_constraint_name: the name of the created reduced constraint
        :return a dictionary with the reduced constraint and new constraints enforcing the reductions
        """
        reduced_constraint, reductions = self.get_reductions(max_degree, use, force, reduction_strategy)
        if not max_degree:
            assert not reductions
        constraints = {reduced_constraint_name: reduced_constraint} if reduced_constraint else {}
        for reduction in reductions:
            constraints.update(get_reduction_constraints(*reduction, max_degree=max_degree))
        return constraints

    def provides_penalty_term_directly(self, max_degree=2):
        """
        check whether the polynomial can be used itself as a penalty term

        :param (int or None) max_degree: the maximum degree to be allowed
        :return: whether the polynomial of the constraints directly provides a penalty polynomial
        """
        if not self.is_equality_constraint() or (max_degree and self.polynomial.degree > max_degree):
            return False

        normalized_constraint = self.normalize()
        if normalized_constraint.polynomial.is_non_negative():
            # if the polynomial is >=0 for all assignments and shall evaluate to 0,
            # it can be used itself as a penalty term
            assert normalized_constraint.polynomial.offset == 0  # invalid constructions should be caught by init
            return True

        return matches_special_penalty_constraint(normalized_constraint)

    def get_penalty_terms(self, name=CONSTRAINT, int_precision=1e-9, reduction_strategy=None,
                          check_special_constraints=True):
        """
        get a quadratic polynomial term which represents the constraint,
        that is, it evaluates to 0 if the constraint is fulfilled and to a positive value otherwise,
        (thus penalizes invalid variable assignments)

        if necessary, slack variables are added and/or a quadratic polynomial is reduced to a linear one,
        the latter causes additional penalty term(s), such that we get, e.g.,
            {name: penalty term directly derived from constraint,
            'reduction_x_1_y_1': penalty term for reduction of product x_1*y_1,
            ...}

        :param (str) name: name of the penalty term directly derived from constraint
        :param (Real) int_precision: precision value for checking if the polynomial is integer, which is needed in case
                                     of an inequality constraint, because those can only be handled if they are integer
        :param (str) reduction_strategy: the method how the reduction pairs are found, by default the fastest version
        :param (bool) check_special_constraints: if true, checks whether there are special constraints
                                                 that can be handled more efficiently than by standard transformation
        :return: the dictionary with names to terms
        """
        # TODO: add option to get penalty terms without prior reduction -> set max degree
        if self.polynomial.is_constant():
            # in this case the constraint is not actually a constraint
            # invalid constructions should be caught by initialization
            assert self.lower_bound <= self.polynomial.offset <= self.upper_bound
            return {}
        if not (self.is_integer(int_precision) or self.is_equality_constraint()):
            # we can only handle integer inequality constraints or arbitrary equality constraints
            raise ValueError(ERROR_INT)

        if check_special_constraints:
            penalty_poly = get_special_constraint_penalty_poly(self)
            if penalty_poly and penalty_poly.is_quadratic():
                # for some special cardinality constraints, the penalty terms are not quadratic
                # for now, we have decided that those will be handled as normal linear constraints
                # where slack variables are introduced rather than reductions applied
                return {name: penalty_poly}

        reduced_constraint, reductions = self.get_reductions(reduction_strategy=reduction_strategy)
        penalty_terms = get_all_reduction_penalty_terms(reductions)

        if reduced_constraint.provides_penalty_term_directly():
            penalty_poly = reduced_constraint.polynomial - reduced_constraint.polynomial.offset
        else:
            penalty_poly = get_standard_penalty_polynomial(reduced_constraint, (name + '_' + SLACK,))

        penalty_terms.update({name: penalty_poly})
        return penalty_terms

    def check_validity(self, var_assignment):
        """
        check if a given variable assignment fulfills the constraint

        :param (dict or list) var_assignment: mapping from variables to values
        :return: True if the constraint is fulfilled
        """
        poly_value = self.polynomial.evaluate(var_assignment)
        return self.lower_bound <= poly_value <= self.upper_bound


# helper methods

## normalization

def _is_first_monomial_non_negative(polynomial):
    """
    check if the polynomial has a non-negative first monomial (not being the offset)

    :param (PolyBinary) polynomial:
    :return: True if the first monomial has a non-negative coefficient
    """
    if polynomial.is_constant():
        return True
    polynomial = polynomial.remove_zero_coefficients()
    polynomial.sort_entries()
    first_monomial = list(polynomial.keys())[0] or list(polynomial.keys())[1]  # if the first is the offset take second
    return polynomial[first_monomial] >= 0

## preprocessing

POLY_EQUATION = PolyBinary({(0,): 1, (1,): -1})
POLY_NEGATION = PolyBinary({(0,): 1, (1,): 1, (): -1})

def _get_preprocessable_variables_eq_or_neg(polynomial, _raise_warning=False):
    """ get the preprocessable variables for polynomials enforcing an equality or a negation of variables """
    compact_poly = polynomial.compact()
    if compact_poly == POLY_EQUATION:  # case x == y
        if _raise_warning:
            warn(WARNING_EQUAL_VARS.format(polynomial.variables[0], polynomial.variables[1]))
        return {polynomial.variables[1]: Polynomial({(polynomial.variables[0],): 1})}

    if compact_poly == POLY_NEGATION:  # case x == 1 - y
        if _raise_warning:
            warn(WARNING_NEG_VARS.format(polynomial.variables[0], polynomial.variables[1]))
        return {polynomial.variables[1]: Polynomial({(polynomial.variables[0],): -1, (): 1})}

    return None

def _get_preprocessable_variables_bounds(polynomial, upper_bound):
    # want 0 <= p+(x) + p-(x) + c <= ub, have p-(1) <= p+(x) + p-(x) <= p+(1) for all x
    # invalid constructions should be caught by initialization
    assert sum(polynomial.positive.values()) + polynomial.offset >= 0
    if sum(polynomial.positive.values()) + polynomial.offset == 0:
        # p+(1) + c == 0 -- this means we are in general below the lower bound and only hit it in the extreme case
        # -> all summands in p+ need to be set to 1 and all summands in p- to 0
        # -> all variables of p+ need to be set to 1 and all variables of p-.linear need to be set to 0
        to_1 = {var: 1 for var in polynomial.positive.variables}
        to_0 = {var: 0 for var in polynomial.negative.linear.variables}
        return to_0, to_1

    assert sum(polynomial.negative.values()) + polynomial.offset <= upper_bound
    if sum(polynomial.negative.values()) + polynomial.offset == upper_bound:
        # p-(1) + c == ub -- this means we are in general above the upper bound and only hit it in the extreme case
        # -> all summands in p- need to be set to 1 and all summands in p+ to 0
        # -> all variables of p- need to be set to 1 and all variables of p+.linear need to be set to 0
        to_1 = {var: 1 for var in polynomial.negative.variables}
        to_0 = {var: 0 for var in polynomial.positive.linear.variables}
        return to_0, to_1

    return {}, {}

## standard linear constraint reformulation

def get_standard_penalty_polynomial(constraint, slack_variable_prefix=(SLACK,)):
    """
    get the squared polynomial penalty term representing the constraint,
    automatically introduces slack variables in case it is an inequality constraint

    this is done by transforming the inequality to an equality with 'polynomial == s' for '0 <= s <= upper_bound'
    where s is an integer slack variable, which gets replaced by a binary representation,
    then the penalty term is formed with '(polynomial - s)**2',
    if the upper bound is 0, we have no slack variables

    note that this only produces proper QUBO penalty terms when the polynomial of the constraint was linear

    :param (ConstrainedBinary) constraint: constraint which shall be transformed
    :param (tuple or str) slack_variable_prefix: prefix for the additional slack variables that are created
    :return: the polynomial representing the constraint
    """
    eq_constraint = constraint.to_equality_constraint(slack_variable_prefix)
    return eq_constraint.polynomial ** 2

## special constraints

### reduction constraints

#### standard linear reduction constraints
REDUCTION_CONSTRAINT_POLY_LIN2 = PolyBinary({(0,): 1, (1,): -1, (): 1})  # 2 variables
REDUCTION_CONSTRAINT_POLY_LIN3 = PolyBinary({(0,): 1, (1,): -1, (2,): -1, (): 1})  # 3 variables

REDUCTION_CONSTRAINT_LIN2 = ConstraintBinary(REDUCTION_CONSTRAINT_POLY_LIN2, 0, 1)  # x0 <=  x1
                                                                                # <=> (0 <=) x0 - x1 + 1 <= 1
REDUCTION_CONSTRAINT_LIN3 = ConstraintBinary(REDUCTION_CONSTRAINT_POLY_LIN3, 0, 1)  # x0 >= x1 + x2 - 1
                                                                             # <=>     0 <=   x0 - x1 - x2 + 1 (<= 2/1)
                                                                             # <=> (-1/0 <=) -x0 + x1 + x2      <= 1

#### original quadratic reduction constraint
REDUCTION_CONSTRAINT_POLY_QUAD  = PolyBinary({(0,): 1, (1, 2): -1})
REDUCTION_CONSTRAINT_QUAD = ConstraintBinary(REDUCTION_CONSTRAINT_POLY_QUAD, 0, 0)  # x0 == x1 * x2
                                                                                 # <=> 0 == x0 - x1 * x2

#### corresponding penalty polynomials, summing up to standard full reduction penalty polynomial
REDUCTION_PENALTY_POLY_LIN2 = PolyBinary({(0,): 1, (0, 1): -1})                        #    x0 -  x0 x1
                                              # analogously when second variable is 2  #    x0          -  x0 x2
REDUCTION_PENALTY_POLY_LIN3 = PolyBinary({(0,): 1, (0, 1): -1, (0, 2): -1, (1, 2): 1}) #    x0 -  x0 x1 -  x0 x2 + x1 x2
                                                                                       # ===============================
REDUCTION_PENALTY_POLY_FULL = PolyBinary({(0,): 3, (0, 1): -2, (0, 2): -2, (1, 2): 1}) # +3 x0 -2 x0 x1 -2 x0 x2 + x1 x2

#### constraints with penalty polynomials
REDUCTION_CONSTRAINT_PENALTY_L2 = ConstraintBinary(REDUCTION_PENALTY_POLY_LIN2, 0, 0)
REDUCTION_CONSTRAINT_PENALTY_L3 = ConstraintBinary(REDUCTION_PENALTY_POLY_LIN3, 0, 0)
REDUCTION_CONSTRAINT_PENALTY_FULL = ConstraintBinary(REDUCTION_PENALTY_POLY_FULL, 0, 0)

CONSTRAINT_2_PENALTY_POLY = [(REDUCTION_CONSTRAINT_LIN2,         REDUCTION_PENALTY_POLY_LIN2, False),
                             (REDUCTION_CONSTRAINT_PENALTY_L2,   REDUCTION_PENALTY_POLY_LIN2, True),
                             (REDUCTION_CONSTRAINT_LIN3,         REDUCTION_PENALTY_POLY_LIN3, False),
                             (REDUCTION_CONSTRAINT_QUAD,         REDUCTION_PENALTY_POLY_FULL, False),
                             (REDUCTION_CONSTRAINT_PENALTY_L3,   REDUCTION_PENALTY_POLY_LIN3, True),
                             (REDUCTION_CONSTRAINT_PENALTY_FULL, REDUCTION_PENALTY_POLY_FULL, True)]

def get_reduction_constraints(reduction_var, var1, var2=None, max_degree=1):
    """
    get the constraint(s) that enforce a variable to be equal to the product of two variables
    (the variables need to be of the same type, thus either tuple, int or str),
    if max_degree is 1, we add the 3 linearization constraints,
    if is greater than 1, then we simply add the constraint var1 * var2 = reduction_var,

    Remark: In the traditional linearization strategy, the lower bound of the third constraint is unset
            (warning.e., the lowest possible value of the polynomial would be -1,
            which our constraint would also default to).
            Here we set the lower bound to 0, which additionally excludes another variable constellation.
            This case is actually already excluded by the other constraints.
            But this setting allows later to handle the below constraints individually and
            nevertheless get the correct quadratic penalty term for the full reduction
            by adding the individual penalty terms.

    :param (tuple or int or str) reduction_var: new binary variable that substitutes var1 * var2
    :param (tuple or int or str) var1: first binary variable
    :param (tuple or int or str) var2: second binary variable
    :param (int) max_degree: the maximum degree of the constraint polynomials, by default 1
    :return: the constraint(s) that enforce var1 * var2 = reduction_var
    """
    if var2 is None:
        return {}  # TODO: return the single corresponding reduction variable here?
    name = to_string(reduction_var)
    if max_degree > 1:
        poly = REDUCTION_CONSTRAINT_POLY_QUAD.replace_variables([reduction_var, var1, var2])
        return {name: ConstraintBinary(poly, 0, 0)}

    name += "_{}"
    polys = [REDUCTION_CONSTRAINT_POLY_LIN2.replace_variables([reduction_var, var1]),
             REDUCTION_CONSTRAINT_POLY_LIN2.replace_variables([reduction_var, var2]),
             REDUCTION_CONSTRAINT_POLY_LIN3.replace_variables([reduction_var, var1, var2])]
    return {name.format(i): ConstraintBinary(poly, 0, 1) for i, poly in enumerate(polys)}

def _match_reduction_constraint_get_penalty_poly(constraint, only_penalty_constraints=False, return_variables=False):
    """ get the penalty polynomial (or the correspondingly permuted variables) corresponding to the constraint """
    normalized_constraint = constraint.normalize()
    variables = tuple(normalized_constraint.polynomial.variables)
    compact = ConstraintBinary(normalized_constraint.polynomial.compact(), 0, normalized_constraint.upper_bound,
                               _check=False)

    for permutation in [[0, 1, 2], [1, 0, 2], [2, 1, 0]]:  # 0 -> 1 -> 1, 1 -> 0 -> 2, 2 -> 2 -> 0
        constraint_permuted = compact.replace_variables(permutation, _check=False)
        variables_permuted = tuple(variables[i] for i in permutation if i < len(variables))
        for reduction_constraint, reduction_penalty_poly, is_penalty in CONSTRAINT_2_PENALTY_POLY:
            if (is_penalty or not only_penalty_constraints) and constraint_permuted == reduction_constraint:
                if return_variables:
                    return variables_permuted
                return reduction_penalty_poly.replace_variables(variables_permuted)

    return None

def retrieve_reduction(constraint):
    """
    check if the constraint corresponds to a reduction and if yes recover the reduction

    :param constraint: the constraint to recover the corresponding reduction from
    :return: the reduction variable triple
    """
    variables = _match_reduction_constraint_get_penalty_poly(constraint, return_variables=True)
    if variables:
        # we just sort the two variables that are reduced
        return (variables[0],) + tuple(sorted(variables[1:]))
    return None

### check for all special constraints (more are to be implemented)

def get_special_constraint_penalty_poly(constraint):
    """
    get the corresponding penalty polynomial if the given constraint fits to one of then special ones

    :param constraint: the constraint to be checked
    :return: the corresponding penalty polynomial
    """
    penalty_poly = _match_reduction_constraint_get_penalty_poly(constraint)
    if penalty_poly:
        return penalty_poly
    return None

def matches_special_penalty_constraint(constraint):
    """
    check whether the constraint matches a penalty polynomial of a special constraint

    :param constraint: the constraint to be checked
    """
    if _match_reduction_constraint_get_penalty_poly(constraint, only_penalty_constraints=True):
        return True
    return False
