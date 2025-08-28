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

""" module for ConstraintObjective """

from abc import abstractmethod
from warnings import warn

from .variable_mapping import VariableMapping
from .polynomial import _try_sorted
from .poly_binary import PolyBinary, get_all_reduction_penalty_terms
from .constraint_binary import get_reduction_constraints
from .constraint_binary import ConstraintBinary
from .objective_terms import ObjectiveTerms
from .utils import variables


OBJECTIVE      = "objective"
REDUCTION      = "reduction"
OBJECTIVE_POLY = "objective_poly"
CONSTRAINTS    = "constraints"

ERROR_INIT = "Currently only binary objective functions are supported for the ConstrainedObjective"
ERROR_IMPL = "Provide '{0}' on initialization or implement '_get_{0}' in inheriting 'ConstrainedObjective' class"
ERROR_UNFULFILLABLE = "Unfulfillable set of constraints"
ERROR_TYPE = "Objective polynomial's and constraints' variable types do not match"
WARNING_NOTHING = "There is nothing in this ConstrainedObjective"
WARNING_DUPLICATED = "The ConstrainedObjective contains {} redundant constraint(s)"
WARNING_DEPRECATION = "This way of instantiation is deprecated and will be removed soon, " \
                      "use method `get_from_instance` instead"


class ConstrainedObjective(dict):
    """
    An objective function combined with usually multiple constraints, restricting the set of feasible solutions,
    together provide an optimization problem.

    This class either serves as a container for a pre-calculated objective polynomial with constraints
    or as a base class for the implementation of methods providing the objective polynomial and the constraints.

    (It is analogue to ObjectiveTerms but with storing constraints.)
    """

    def __init__(self, objective_poly=None, constraints=None, name=None, instance=None,
                 check_redundant_constraints=True):
        """
        initialize a ConstrainedObjective object,
        either provide objective_poly and constraints to store them or
        provide instance for implemented subclass to construct the objective_poly and constraints from the instance

        :param (PolyBinary or None) objective_poly: polynomial representing the objective function
        :param (dict or None) constraints: dictionary with names to constraints
        :param (str or None) name: identifying name to differ between several constrained objectives
        :param instance: instance object storing all data to construct the constrained objective from
        """
        if instance:
            warn(WARNING_DEPRECATION, DeprecationWarning)
            self.objective_poly = self._get_objective_poly(instance)
            self.name = name or self._get_name(instance)
            super().__init__(self._get_constraints(instance))
        else:
            self.objective_poly = objective_poly or PolyBinary()
            self.name = name
            super().__init__(constraints or {})

        # TODO: implement redundancy check based on expected complexity/time
        self.check_consistency(check_redundant_constraints)

    def check_consistency(self, check_redundant_constraints):
        """ check if the data is consistent """
        if not isinstance(self.objective_poly, PolyBinary):
            raise ValueError(ERROR_INIT)
        if not self.objective_poly and not self:
            warn(WARNING_NOTHING)

        if check_redundant_constraints:
            redundant_cons = self.get_redundant_constraints()
            if redundant_cons:
                warn(WARNING_DUPLICATED.format(len(redundant_cons)))
                # TODO: detect more contradicting constraints? -> preprocess

            # check the variables from the objective polynomial and the constraints
        _ = self.get_all_variables()

    def __eq__(self, other):
        if isinstance(other, ConstrainedObjective):
            if super().__eq__(other):
                return self.objective_poly == other.objective_poly and self.name == other.name
        return False

    def __ne__(self, other):
        # needs to be implemented otherwise would just use dict comparison
        return not self.__eq__(other)

    def __repr__(self):
        """ get nice string representation """
        return self.__class__.__name__ + f"({repr(self.objective_poly)}, {super().__repr__()}, {repr(self.name)})"

    def __str__(self):
        """ get nice human-readable string representation of the constrained objective """
        objective = f"min  {self.objective_poly}\ns.t. "
        domains = sorted(set(variables.to_domain_string(var) for var in self.get_all_variables()))

        lens_lower_bounds = [len(str(constraint.lower_bound)) for constraint in self.values()]
        max_len_lower_bound = max(lens_lower_bounds, default=0)
        const_prefixes = [" " * (max_len_lower_bound - len_lower_bound) for len_lower_bound in lens_lower_bounds]
        constraints = [prefix + constraint.__str__(revert_eq=True)
                       for prefix, constraint in zip(const_prefixes, self.values())
                       if constraint.is_equality_constraint()]
        constraints += [prefix + str(constraint)
                        for prefix, constraint in zip(const_prefixes, self.values())
                        if not constraint.is_equality_constraint()]
        constraints = [constraint for prefix, constraint in zip(const_prefixes, constraints)]

        subject_to = ",\n     ".join(constraints + domains)
        return objective + subject_to

    @classmethod
    def get_from_instance(cls, instance, name=None):
        """
        get the implemented inheriting ConstrainedObjective object based on the instance data

        :param (Instance or object) instance: An object of the implemented (inheriting) Instance class
        :param (str or None) name: the name of the resulting object
        :return: the initialized object
        """
        objective_poly = cls._get_objective_poly(instance)
        constraints = cls._get_constraints(instance)
        name = name or cls._get_name(instance)
        return cls(objective_poly, constraints, name)

    def get_broken_constraints(self, var_assignment):
        """
        get the names of the constraints that the variable assignment does not fulfill

        :param (dict or list) var_assignment: mapping from variables to values
        :return: the names of the constraints that are not fulfilled
        """
        return [name for name, constraint in self.items() if not constraint.check_validity(var_assignment)]

    def get_redundant_constraints(self):
        """
        get the redundant constraints

        :return: the names of redundant constraints
        """
        non_redundant_cons = {}
        for name, constraint in self.items():
            if constraint not in non_redundant_cons.values():
                non_redundant_cons[name] = constraint
        redundant_cons = set(self.keys()) - set(non_redundant_cons.keys())
        return redundant_cons

    def remove_redundant_constraints(self):
        """
        remove redundant constraints

        :return: a ConstrainedObjective without redundant constraints
        """
        redundant_constraints = self.get_redundant_constraints()
        if redundant_constraints:
            constraints = {name: constraint.copy() for name, constraint in self.items()
                           if not name in redundant_constraints}
            return self.__class__(self.objective_poly.copy(), constraints)
        return self

    def check_validity(self, var_assignment):
        """
        check if the variable assignment fulfills the constraints

        :param (dict or list) var_assignment: mapping from variables to values
        :return: True if all constraints are fulfilled
        """
        return not self.get_broken_constraints(var_assignment)

    def is_compact(self):
        """
        determine if the ConstraintObjective is compact
        :return: bool
        """
        return variables.are_consecutive(self.get_all_variables())

    def compact(self, new_name=None):
        """
        get a new ConstrainedObjective with a compact Polynomial for the
        objective and constraints

        :param (str or None) new_name: name of the new objective, by default
                                       the original name is used
        :return: the ConstrainedObjective with a compacted polynomial,
                 the VariableMapping of the original polynomial to new one
                 (or None if it was already compact)
        """
        if self.is_compact():
            return self, None

        new_name = new_name or self.name
        all_variables = self.get_all_variables()
        compact_objective_poly = self.objective_poly.replace_variables_by_ordering(all_variables)
        compact_constraints = {}
        for name, constraint in self.items():
            compact_poly = constraint.polynomial.replace_variables_by_ordering(all_variables)
            compact_constraints[name] = ConstraintBinary(compact_poly, constraint.lower_bound, constraint.upper_bound)
        return self.__class__(compact_objective_poly, compact_constraints, new_name), VariableMapping(all_variables)

    def get_reductions(self, max_degree=1, use=None, force=False, reduction_strategy=None):
        """
        get new constrained objective where all appearing polynomials are reduced if the degrees are too large

        :param (int or None) max_degree: the maximal degree of the final polynomial,
                                         if None only the given reductions are applied
        :param (list[tuples] or None) use: the reductions which shall be used,
                                           as a list with tuples in the format (var1, var2, reduction_var)
        :param (bool) force: if True also reduce quadratic polynomials to linear that could remain for the QUBO problem
        :param (str) reduction_strategy: the method how the reduction pairs are found, by default the fastest version
        :return: the reduced constrained objective object, the applied reductions
        """
        # TODO: combine all polynomials to get corresponding possibly better reductions for full object
        reduced_objective_poly, reductions = self.objective_poly.reduce(1 if force else max(2, max_degree), use=use,
                                                                        reduction_strategy=reduction_strategy)
        use = use or []
        reduced_constraints = {}
        for name, constraint in self.items():
            reduced_constraint, further_reductions = constraint.get_reductions(max_degree, use + reductions, force,
                                                                               reduction_strategy=reduction_strategy)
            reductions += further_reductions
            if reduced_constraint:
                reduced_constraints[name] = reduced_constraint

        # go through constraints again and apply reductions found in a later step also in earlier processed constraints
        reductions = sorted(set(reductions))
        for name, constraint in reduced_constraints.items():
            reduced_constraints_single = constraint.reduce(None, use=reductions, reduction_strategy=reduction_strategy,
                                                           reduced_constraint_name=name)
            assert len(reduced_constraints_single) == 1  # no reduction constraints should be added
            reduced_constraints.update(reduced_constraints_single)

        return reduced_objective_poly, reduced_constraints, reductions

    def reduce(self, max_degree=1, use=None, force=False, new_name=None, reduction_strategy=None):
        """
        get new constrained objective where all appearing polynomials are reduced if the degrees are too large
        and the corresponding reduction constraints are added

        :param (int or None) max_degree: the maximal degree of the final polynomial,
                                         if None only the given reductions are applied
        :param (list[tuples] or None) use: the reductions which shall be used,
                                           as a list with tuples in the format (var1, var2, reduction_var)
        :param (bool) force: if True also reduce quadratic polynomials to linear that could remain for the QUBO problem
        :param (str or None) new_name: name of the new constrained objective, by default the original name is used
        :param (str) reduction_strategy: the method how the reduction pairs are found, by default the fastest version
        :return: the reduced constrained objective object, the applied reductions
        """
        reduced_obj_poly, reduced_constraints, reductions = self.get_reductions(max_degree, use, force,
                                                                                reduction_strategy=reduction_strategy)
        for reduction in reductions:
            reduced_constraints.update(get_reduction_constraints(*reduction, max_degree=max_degree))

        new_name = new_name or self.name
        return self.__class__(reduced_obj_poly, reduced_constraints, new_name)

    def get_objective_terms(self, objective_name=OBJECTIVE, combine_prefixes=(REDUCTION,), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """
        get an ObjectiveTerms object with the objective as one term
        and automatically generated penalty terms for each constraint

        :param (str) objective_name: name of the term that corresponds to the objective
        :param (tuple or str) combine_prefixes: prefixes in the names of the constraints whose corresponding
                                                objective terms shall be combined to a single objective term,
                                                by default all terms starting with "reduction" are combined
        :param (str or None) name: name of the objective terms, by default the name of the constrained objective is used
        :param (str) reduction_strategy: the method how the reduction pairs are found, by default the fastest version
        :param (bool) check_special_constraints: whether special constraints shall be considered
        :return: the ObjectiveTerms object
        """
        # TODO: catch constraints setting two variables to be equal and use polynomial.evaluate -> preprocess?
        # TODO: option to get objective terms without automatic reduction?
        reduced_obj_poly, reduced_constraints, reductions = self.get_reductions(reduction_strategy=reduction_strategy)

        objective_terms = {}
        for constraint_name, constraint in reduced_constraints.items():
            objective_terms.update(constraint.get_penalty_terms(constraint_name,
                                                                check_special_constraints=check_special_constraints))
        # after the reduction there should be a single penalty term for each constraint
        assert len(reduced_constraints) == len(objective_terms)

        reduction_penalty_terms = get_all_reduction_penalty_terms(reductions)
        objective_terms.update(reduction_penalty_terms)
        constraint_terms_names = list(objective_terms.keys())

        if not reduced_obj_poly == 0:
            # only in case the objective polynomial is not empty we do want to add it as an additional term
            objective_terms.update({objective_name: reduced_obj_poly})

        name = name or self.name
        obj = ObjectiveTerms(objective_terms=objective_terms, constraint_terms_names=constraint_terms_names, name=name)
        if combine_prefixes:
            combine_prefixes = combine_prefixes if isinstance(combine_prefixes, tuple) else (combine_prefixes,)
            return obj.combine_prefixes(*combine_prefixes)
        return obj

    def get_all_variables(self):
        """
        get all variables from all polynomials

        :return: the sorted list of all appearing variables
        """
        all_vars = set(self.objective_poly.variables).union(*(const.polynomial.variables for const in self.values()))
        try:
            _ = variables.get_common_type(all_vars)
        except TypeError as te:
            assert "Expected variable type" in te.args[0]
            raise TypeError(ERROR_TYPE) from te
        return _try_sorted(all_vars)

    @staticmethod
    @abstractmethod
    def _get_objective_poly(instance):
        """
        get the objective polynomial from the instance data,
        needs to be implemented in subclasses for automatic generation

        :param instance: instance object storing all data to construct the objective polynomial from
        :return: the polynomial representing the objective function
        """
        raise NotImplementedError(ERROR_IMPL.format(OBJECTIVE_POLY))

    @staticmethod
    @abstractmethod
    def _get_constraints(instance):
        """
        get the constraints from the instance data,
        needs to be implemented in subclasses for automatic generation

        :param instance: instance object storing all data to construct the constraints from
        :return: the dictionary with names to constraints
        """
        raise NotImplementedError(ERROR_IMPL.format(CONSTRAINTS))

    @staticmethod
    def _get_name(instance):  # pylint: disable=unused-argument
        """
        get the name from the instance data,
        can be implemented in subclasses for automatic generation, is not enforced

        :param instance: instance object storing all data to construct the name from
        :return: the name of the object
        """
        return None
