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

""" module for ObjectiveTerms """

from abc import abstractmethod
from warnings import warn

from .polynomial import _try_sorted, MIN_ABS_DIST
from .poly_binary import PolyBinary, get_all_reduction_penalty_terms
from .poly_ising import PolyIsing
from .objective import Objective
from .utils import variables


CONSTRAINT_TERMS_NAMES = "constraint_terms_names"
OBJECTIVE_TERMS = "objective_terms"
REDUCTION = "reduction"

ERROR_IMPL       = "Provide '{0}' on initialization or implement '_get_{0}' in inheriting 'ObjectiveTerms' class"
ERROR_NAMES      = "All constraint terms names should also be a key of the objective terms"
ERROR_MISMATCH   = "There is a mismatch between given and stored objective_terms names"
ERROR_TYPE       = "Cannot add PolyIsing and PolyBinary, make sure your objective terms are all of the same " \
                   "type by using the methods 'all_to_xxx'"
ERROR_DEGREE     = "Can only reduce to at least quadratic"
ERROR_REDUCTION  = "Reduction is currently only implemented for binary polynomials"
ERROR_OBJECTIVES = "Currently only one objective function is supported"
ERROR_INPUT      = "Either provide ObjectiveTerms objects or the constraint terms names separately"

WARNING_NOTHING     = "There is nothing in this ObjectiveTerms"
WARNING_DEPRECATION = "This way of instantiation is deprecated and will be removed soon, " \
                      "use method `get_from_instance` instead"
WARNING_SCALE       = "If the terms weights are given, the penalty scale is ignored"


class ObjectiveTerms(dict):
    """
    An objective term is a quadratic polynomial that belongs to a specific part of an objective function of a QUBO or
    an Ising problem. To distinguish the terms, they are named. Several objective terms are weighted and summed up to
    finally form the full objective polynomial.

    This class either serves as a container for pre-calculated objective terms
    or as the base class for the implementation of methods providing the objective terms.

    (It is an analogue to the ConstrainedObjective but with storing objective terms.)
    """

    def __init__(self, objective_terms=None, constraint_terms_names=None, name=None, instance=None):
        """
        initialize ObjectiveTerms object,
        either provide objective_terms to store them or
        provide instance for implemented subclass to construct the objective_poly and constraints from the instance

        :param (dict or None) objective_terms: mapping from names to objective terms
        :param (list[str] or None) constraint_terms_names: names of objective terms that correspond to constraints
        :param (str or None) name: identifying name to differ between several objective terms
        :param instance: instance object storing all data to construct the objective terms from
        """
        if instance:
            warn(WARNING_DEPRECATION, DeprecationWarning)
            self.constraint_terms_names = self._get_constraint_terms_names()
            self.name = name or self._get_name(instance)
            super().__init__(self._get_objective_terms(instance))
        else:
            self.constraint_terms_names = constraint_terms_names or []
            self.name = name
            super().__init__(objective_terms or {})

        self.check_consistency()

    def check_consistency(self):
        """ check if the data is consistent """
        if not set(self.constraint_terms_names) <= set(self.keys()):
            raise ValueError(ERROR_NAMES)
        if not self.constraint_terms_names and not self:
            warn(WARNING_NOTHING)

    def __eq__(self, other):
        if isinstance(other, ObjectiveTerms):
            if super().__eq__(other):
                return set(self.constraint_terms_names) == set(other.constraint_terms_names)
        return False

    def __ne__(self, other):
        # needs to be implemented otherwise would just use dict comparison
        return not self.__eq__(other)

    def __repr__(self):
        """ get nice string representation """
        return self.__class__.__name__ + f"({super().__repr__()}, {self.constraint_terms_names}, {repr(self.name)})"

    def __str__(self):
        """ get nice human-readable string representation of the objective terms """
        first_term = "min  P_{} * "
        other_terms = "\n     + P_{} * ".join(f"( {str(poly)} )" for poly in self.values())
        objective = (first_term + other_terms).format(*range(len(self)))
        domains = sorted(set(variables.to_domain_string(var, poly.__class__.__name__)
                             for poly in self.values() for var in poly.variables))
        domains = "\ns.t. " + ",\n     ".join(domains)
        return objective + domains

    def _check_names(self, names):
        if set(names) != set(self.keys()):
            raise ValueError(ERROR_MISMATCH)

    @classmethod
    def get_from_instance(cls, instance, name=None):
        """
        get the implemented inheriting ObjectiveTerms object based on the instance data

        :param (Instance or object) instance: An object of the implemented (inheriting) Instance class
        :param (str or None) name: the name of the resulting object
        :return: the initialized object
        """
        objective_terms = cls._get_objective_terms(instance)
        constraint_terms_names = cls._get_constraint_terms_names()
        name = name or cls._get_name(instance)
        return cls(objective_terms, constraint_terms_names, name)

    def reduce(self, max_degree=2, single_penalty_term=True, new_name=None, reduction_strategy=None):
        """
        reduce all appearing polynomials if the degrees are too large

        :param (int or None) max_degree: the maximal degree of the final polynomial,
                                         if None only the given reductions are applied
        :param (bool) single_penalty_term: True if all reductions shall be combined in a single penalty term
        :param (str or None) new_name: name of the new objective terms, by default the original name is used
        :param (str) reduction_strategy: the method how the reduction pairs are found, by default the fastest version
        :return: the reduced objective terms object
        """
        if max_degree < 2:
            raise ValueError(ERROR_DEGREE)
        if not all(isinstance(term, PolyBinary) for term in self.values()):
            raise ValueError(ERROR_REDUCTION)
        if all(term.degree <= max_degree for term in self.values()):
            return self

        new_terms = {}
        reductions = []
        for name, term in self.items():
            reduced_term, further_reductions = term.reduce(max_degree, use=reductions,
                                                           reduction_strategy=reduction_strategy)
            reductions += further_reductions
            new_terms[name] = reduced_term

        # apply reductions found in a later step also in already processed terms
        reductions = sorted(set(reductions))
        new_terms = {name: term.reduce(max_degree, use=reductions, reduction_strategy=reduction_strategy)[0]
                     for name, term in new_terms.items()}
        reduction_penalty_terms = get_all_reduction_penalty_terms(reductions)

        if not single_penalty_term:
            new_terms.update(reduction_penalty_terms)
            new_terms_names = self.constraint_terms_names + list(reduction_penalty_terms.keys())
        else:
            summed_reduction_penalty_term = sum(poly for poly in reduction_penalty_terms.values())
            new_terms[REDUCTION] = summed_reduction_penalty_term
            new_terms_names = self.constraint_terms_names + [REDUCTION]

        new_name = new_name or self.name
        return self.__class__(objective_terms=new_terms, constraint_terms_names=new_terms_names, name=new_name)

    def evaluate_terms(self, var_assignment):
        """
        get the values of all objective terms evaluated with the given variable assignment

        :param (dict) var_assignment: mapping from variables to values
        :return: the dictionary of objective terms names to values
        """
        return {name: objective_term.evaluate(var_assignment) for name, objective_term in self.items()}

    def check_validity(self, var_assignment):
        """
        check if the given variable assignment fulfills the condition
        that the value of all objective terms corresponding to constraints should be 0

        :param (dict) var_assignment: mapping from variables to values
        :return: True if all objective terms corresponding to constraints evaluate to 0
        """
        values = self.evaluate_terms(var_assignment)
        return all(values[name] == 0 for name in self.constraint_terms_names)

    def get_terms_weights_string(self, terms_weights):
        """
        get a string representation of the terms weights,
        the keys need to be the same as the objective term names
        the ordering in the string is defined by the ordering in the terms weights dictionary
        (e.g. 'myConstraint1.0_mySecondConstraint1.5')

        :param (dict) terms_weights: mapping of objective terms names to values
        :return: the name consisting of the objective terms names with the corresponding values
        """
        self._check_names(terms_weights)
        return get_string(terms_weights)

    def get_weighted_sum_polynomial(self, terms_weights):
        """
        get the weighted sum of the objective terms as a polynomial

        :param (dict) terms_weights: mapping of objective terms names to values
        :return: the weighted sum of the objective terms
        """
        self._check_names(terms_weights)
        try:
            return sum(value * self[name] for name, value in terms_weights.items())
        except ValueError as ve:
            raise ValueError(ERROR_TYPE) from ve

    def get_objective(self, terms_weights=None, penalty_scale=1, name=None):
        """
        get the objective with a polynomial objective function given by the weighted sum of the objective terms,

        if the resulting solutions are not feasible, i.e., they do not fulfill the constraints,
        increase the penalty scale or increase the single terms_weights correspondingly

        :param (dict) terms_weights: mapping of objective terms names to values
        :param (numbers.Real) penalty_scale: the scaling factor which is applied to the weights of terms corresponding
                                             to constraints, only if no terms_weights are given
        :param (str or None) name: name of the constructed objective, by default generated from terms weights
        :return: the Objective with the weighted sum of the objective terms as objective function
        """
        if terms_weights and penalty_scale != 1:
            warn(WARNING_SCALE)
        terms_weights = terms_weights or self.get_default_terms_weights(penalty_scale)
        poly = self.get_weighted_sum_polynomial(terms_weights)
        name = name or self.get_default_objective_name(terms_weights)
        return Objective(polynomial=poly, name=name)

    def get_default_terms_weights(self, penalty_scale=1, use_naive_bounds=False):
        """
        get a default weighting of the objective terms to create the objective,
        can be overwritten in subclass implementations to provide more meaningful weights

        :param (numbers.Real) penalty_scale: the scaling factor which is applied to the weights of terms corresponding
                                             to constraints
        :param (bool) use_naive_bounds: whether to use naive bound or not
        :return: the default terms weights
        """
        scaled_terms_weights = {name: penalty_scale if name in self.constraint_terms_names else 1 for name in self}
        if not use_naive_bounds:
            return scaled_terms_weights

        naive_terms_weights = get_naive_terms_weights(self)
        return {name: value * scaled_terms_weights[name] for name, value in naive_terms_weights.items()}

    def get_default_objective_name(self, terms_weights):
        """
        get the default name of the constructed objective

        :param (dict) terms_weights: mapping of objective terms names to values
        :return: the default name of the objective
        """
        prefix = "" if not self.name else f"{self.name}/"
        return prefix + self.get_terms_weights_string(terms_weights)

    def get_all_variables(self):
        """
        get all variables from all polynomials

        :return: the sorted list of all appearing variables
        """
        all_vars = set().union(*(term.variables for term in self.values()))
        return _try_sorted(all_vars)

    def combine_prefixes(self, *prefixes, new_name=None):
        """
        sum up those objective terms whose names share the given prefixes

        :param (str) prefixes: the prefixes of the objective terms names that shall be combined
        :param (str or None) new_name: name of the new objective terms, by default the original name is used
        :return: the new ObjectiveTerms object with fewer terms
        """
        new_terms = dict(self)
        new_names = set(self.constraint_terms_names)
        for prefix in prefixes:
            combine = {name: term for name, term in self.items() if name.startswith(prefix)}
            if combine:
                for name in combine.keys():
                    del new_terms[name]
                    if name in new_names:
                        new_names.remove(name)
                        new_names.add(prefix)
                new_terms[prefix] = sum(combine.values())

        new_name = new_name or self.name
        return self.__class__(objective_terms=new_terms, constraint_terms_names=sorted(new_names), name=new_name)

    def all_to_binary(self, new_name=None):
        """
        convert all objective terms to PolyBinary

        :param (str or None) new_name: name of the new objective terms, by default the original name is used
        :return: the new ObjectiveTerms with all terms as binary polynomials
        """
        new_name = new_name or self.name
        new_terms = {name: PolyBinary.from_unknown_poly(poly) for name, poly in self.items()}
        return self.__class__(objective_terms=new_terms,
                              constraint_terms_names=self.constraint_terms_names,
                              name=new_name)

    def all_to_ising(self, inverted=False, new_name=None):
        """
        convert all objective terms to PolyIsing

        :param (bool) inverted: if True, convert to inverted Ising
        :param (str or None) new_name: name of the new objective terms, by default the original name is used
        :return: the new ObjectiveTerms with all terms as Ising polynomials
        """
        new_name = new_name or self.name
        new_terms = {name: PolyIsing.from_unknown_poly(poly, inverted=inverted) for name, poly in self.items()}
        return self.__class__(objective_terms=new_terms,
                              constraint_terms_names=self.constraint_terms_names,
                              name=new_name)

    @staticmethod
    @abstractmethod
    def _get_constraint_terms_names():
        """
        get the names of the objective terms whose value must be zero to have the corresponding constraints fulfilled,
        which need to be a subset of all objective terms names,
        needs to be implemented in subclasses for automatic generation

        :return: the list of objective terms names representing the constraints
        """
        raise NotImplementedError(ERROR_IMPL.format(CONSTRAINT_TERMS_NAMES))

    @staticmethod
    @abstractmethod
    def _get_objective_terms(instance):
        """
        get the objective terms from the instance data,
        needs to be implemented in subclasses for automatic generation

        :param instance: instance object storing all data to construct the objective terms from
        :return: the dictionary with names to objective terms (Polynomials)
        """
        raise NotImplementedError(ERROR_IMPL.format(OBJECTIVE_TERMS))

    @staticmethod
    def _get_name(instance):  # pylint: disable=unused-argument
        """
        get the name from the instance data,
        can be implemented in subclasses for automatic generation, is not enforced

        :param instance: instance object storing all data to construct the name from
        :return: the name of the object
        """
        return None


def get_string(terms_weights):
    """
    get a string concatenating the given dictionary of terms weights,
    the ordering in the string is defined by the ordering in the terms weights dictionary
    (e.g. myConstraint1.0_mySecondConstraint1.5)

    :param (dict) terms_weights: mapping of objective terms names to values
    :return: the string consisting of the objective terms names with the corresponding values
    """
    return '_'.join(name + f'{weight:e}' for name, weight in terms_weights.items())

def get_naive_terms_weights(objective_terms, constraint_terms_names=None, gap=1):
    """
    get naive weights for the objective terms, derived from naive bounds on the objective and the constraint terms

    :param (dict) objective_terms: the objective_terms to calculate the weights for
    :param (list) constraint_terms_names: the names of the constraint terms to weight the objective against
    :param (float) gap: the difference between the objective and constraint terms
    :return: the naive terms weights
    """
    if isinstance(objective_terms, ObjectiveTerms):
        constraint_terms_names = objective_terms.constraint_terms_names
    if not constraint_terms_names:
        raise ValueError(ERROR_INPUT)

    # get the objective function
    objective_functions = set(objective_terms).difference(constraint_terms_names)
    if not objective_functions:
        # if there is no objective function, all constraint terms can be weighted equally
        return {name: 1 for name in constraint_terms_names}
    if len(objective_functions) > 1:
        raise ValueError(ERROR_OBJECTIVES)
    objective_name = objective_functions.pop()

    # get naive bound on the benefit in the objective
    obj_lower_bound = objective_terms[objective_name].naive_lower_bound
    obj_upper_bound = objective_terms[objective_name].naive_upper_bound
    objective_bound = obj_upper_bound - obj_lower_bound + gap

    # for constraint terms with non-integer coefficients, a normalizing factor needs to be applied
    normalizing_factors = {name: poly.coefficients_info[MIN_ABS_DIST] if not poly.has_int_coefficients() else 1
                           for name, poly in objective_terms.items()}

    return {name: objective_bound / normalizing_factors[name] if name in constraint_terms_names else 1
            for name in objective_terms.keys()}
