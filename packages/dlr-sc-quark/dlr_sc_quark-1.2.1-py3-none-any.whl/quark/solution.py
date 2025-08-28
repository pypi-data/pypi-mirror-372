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

""" module for Solution """

from numbers import Integral
from functools import partial

from .variable_mapping import VariableMapping
from .utils.variables import are_consecutive, to_string


ERROR_NEITHER     = "Solution is neither binary nor ising"
ERROR_MAPPING     = "Variable '{}' does not have a mapping to a new variable"
ERROR_EMPTY       = "Solution is empty, there are no variables to be replaced"
ERROR_VARIABLES   = "Number of provided variables is different than of contained variables"
ERROR_COMPACT     = "Solution is not compact"
ERROR_REPLACEMENT = "Dictionary of variables or VariableMapping is expected"

ADDITIONAL_INFO_ATTRS = ["objective_value",
                         "solving_success",
                         "solving_status",
                         "solving_time",
                         "total_time",
                         "dual_gap",
                         "dual_bound"]


class Solution(dict):
    """ A solution is a mapping from variables to values in the domain of the corresponding problem. """

    def __init__(self,
                 var_assignments=None,
                 objective_value=None,
                 solving_success=False,
                 solving_status=None,
                 solving_time=0,
                 total_time=None,
                 dual_gap=None,
                 dual_bound=None,
                 name=None):
        """
        initialize Solution object

        :param (dict or list) var_assignments: dictionary or list containing the solution,
                                               i.e., a mapping from variables to values in the corresponding domain,
                                               e.g., {('x', 1, 2): 1, ('x', 1, 1): 0},
                                               a list of values is considered as mapping from flat variables
        :param (float or None) objective_value: objective value or current best value returned by the solver
        :param (bool) solving_success: True if solver successfully optimized the model
        :param (str or None) solving_status: status of the solver at the end of the optimization, e.g. 'timeout'
        :param (float or None) solving_time: runtime of the optimization
        :param (float or None) total_time: time since model object was created
        :param (float or None) dual_gap: gap to the dual solution
        :param (float or None) dual_bound: value of the dual solution
        :param (str or None) name: identifying name to differ between several solutions
        """
        if isinstance(var_assignments, list):
            var_assignments = dict(enumerate(var_assignments))
        super().__init__(var_assignments or {})

        self.objective_value = objective_value
        self.solving_success = solving_success
        self.solving_status = solving_status
        self.solving_time = solving_time
        self.total_time = total_time
        self.dual_gap = dual_gap
        self.dual_bound = dual_bound
        self.name = name

    def __eq__(self, other):
        # we also allow for the comparison with plain dicts where the name and the additional info is irrelevant
        if isinstance(other, dict) and super().__eq__(other):
            if isinstance(other, Solution):
                return self.name == other.name and self._get_additional_info_dict() == other._get_additional_info_dict()
            return True
        return False

    def __ne__(self, other):
        # needs to be implemented otherwise would just use dict comparison
        return not self.__eq__(other)

    def __repr__(self):
        """ get nice string representation """
        self.sort_entries()
        return self.__class__.__name__ + f"({super().__repr__()}, {self.objective_value}, {repr(self.name)})"

    def __str__(self):
        """ convert the solution to a human-readable string """
        self.sort_entries()
        return "\n".join(to_string(var) + f" \t= {value}" for var, value in self.items())

    def sort_entries(self):
        """ does not change the solution but the ordering of its entries in the dict, mainly for nice output """
        sorted_items = {key: self[key] for key in sorted(self.keys())}
        super().clear()
        super().update(sorted_items)

    def has_only_binary_values(self):
        """ check if the solution has only binary values"""
        return all(v in (0, 1) for v in self.values())

    def has_only_ising_values(self):
        """ check if the solution hase only ising values"""
        return all(v in (-1, 1) for v in self.values())

    def apply_to_var_assignments(self, func, new_name=None):
        """
        apply the function to the variable assignments and thus extract another solution

        :param (callable) func: a mapping from the dictionary of variable assignments to a new one
        :param (str or None) new_name: name of the new solution, by default the original name is used
        :return: the new solution
        """
        return Solution(func(self), name=new_name or self.name, **self._get_additional_info_dict())

    def _get_additional_info_dict(self):
        return {attr: getattr(self, attr) for attr in ADDITIONAL_INFO_ATTRS}

    def to_ising(self, invert=False, new_name=None):
        """
        transform the solution into an Ising solution by applying the transformation (2x-1) resp. (-2x+1)
        or, if the solution is already an Ising solution, with invert=True it can be inverted

        :param (bool) invert: if True, the resulting Ising will additionally be inverted (1->-1, -1->1)
        :param (str or None) new_name: name of the new solution, by default the original name is used
        :return: the new solution with Ising values
        """
        if self.has_only_ising_values():
            if not invert:
                return self
            return self.apply_to_var_assignments(invert_ising, new_name)
        if self.has_only_binary_values():
            return self.apply_to_var_assignments(partial(binary_to_ising, invert=invert), new_name)
        raise ValueError(ERROR_NEITHER)

    def to_binary(self, is_inverted=False, new_name=None):
        """
        transform the solution into a binary solution by applying the transformation (x+1)/2 resp. (-x+1)/2

        :param (bool) is_inverted: if True, the given Ising solution is from an inverted Ising objective,
                                   therefore it gets inverted before the conversion to Ising
        :param (str or None) new_name: name of the new solution, by default the original name is used
        :return: the new solution with binary values
        """
        if self.has_only_binary_values():
            return self
        if self.has_only_ising_values():
            return self.apply_to_var_assignments(partial(ising_to_binary, is_inverted=is_inverted), new_name)
        raise ValueError(ERROR_NEITHER)

    def decompact(self, variables, new_name=None):
        """
        replace the variables in the solution with the original (non-compact) variables

        :param (list or dict or VariableMapping) variables: the original variables from the non-compact polynomial
        :param (str or None) new_name: name of the new solution, by default the original name is used
        :return: the solution with non-compact variables
        """
        if not self:
            raise ValueError(ERROR_EMPTY)
        if not len(self) == len(variables):
            raise ValueError(ERROR_VARIABLES)
        if not are_consecutive(set(self.keys())):
            raise ValueError(ERROR_COMPACT)
        return self.replace_variables(variables, new_name=new_name, check_all=False)

    def replace_variables(self, replacement, new_name=None, check_all=True):
        """
        replace the variables in the solution with different ones

        :param (list or dict or VariableMapping) replacement: mapping to the new variables,
                                                              if replacement is a dictionary, it should be of format
                                                                   {old_var : new_var},
                                                              can be a list if the polynomial is flat
        :param (str or None) new_name: name of the new solution, by default the original name is used
        :param (bool) check_all: if False, those variables which do not have a mapping will not be replaced
                                     and no error is thrown
                                 if True, will throw error if there is a variable which does not have a mapping
        :return: the solution with replaced variables
        """
        if isinstance(replacement, list):
            replacement = dict(enumerate(replacement))
        if not isinstance(replacement, (dict, VariableMapping)):
            raise ValueError(ERROR_REPLACEMENT)
        return self.apply_to_var_assignments(partial(_replace, replacement=replacement, check_all=check_all), new_name)


def binary_to_ising(var_assignment, invert=False):
    """
    convert the variable assignment to the one of the corresponding Ising problem

    :param (dict) var_assignment: solution to a binary problem as a mapping from variables to values
    :param (bool) invert: if True, convert binary to inverted Ising
    :return: the solution to the corresponding Ising problem
    """
    return {k: (-2*v+1 if invert else 2*v-1) for k, v in var_assignment.items()}

def ising_to_binary(var_assignment, is_inverted=False):
    """
    convert the variable assignment to the one of the corresponding binary problem

    :param (dict) var_assignment: solution to an Ising problem as a mapping from variables to values
    :param (bool) is_inverted: if True, the var_assignment is a solution of an inverted Ising problem and will thus be
                               inverted beforehand
    :return: the solution to the corresponding binary problem
    """
    return {k: ((int((-v+1)/2) if isinstance(v, Integral) else (-v+1)/2) if is_inverted
                else (int((v+1)/2)) if isinstance(v, Integral) else (v+1)/2)  # if was integer, keep integer
            for k, v in var_assignment.items()}

def invert_ising(var_assignment):
    """
    convert the variable assignment to the one of an inverted Ising problem or vice versa

    :param (dict) var_assignment: solution to an Ising or inverted Ising problem as a mapping from variables to values
    :return: the solution to the corresponding inverted Ising problem
    """
    return {k: -v for k, v in var_assignment.items()}

def _replace(var_assignment, replacement, check_all):
    # here replacement is a dictionary of the format {old_var : new_var}
    try:
        return {replacement[old_var] if check_all else replacement.get(old_var, old_var): coefficient
                for old_var, coefficient in var_assignment.items()}
    except KeyError as ke:
        raise ValueError(ERROR_MAPPING.format(ke.args[0])) from ke
