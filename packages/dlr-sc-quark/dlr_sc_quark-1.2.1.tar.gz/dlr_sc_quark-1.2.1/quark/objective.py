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

""" module for Objective """

from abc import abstractmethod
from functools import partial
from warnings import warn

from .variable_mapping import VariableMapping
from .polynomial import Polynomial
from .poly_binary import PolyBinary
from .poly_ising import PolyIsing
from .utils import variables


POLYNOMIAL = 'polynomial'
NAME = 'name'

ERROR_POLYNOMIAL = "Objective's polynomial is neither Polynomial, PolyIsing nor PolyBinary"
ERROR_ISING      = "Only supported for Ising models"
ERROR_ZERO       = "Only supported for Ising models without linear terms (zero local fields)"
ERROR_VARIABLE   = "Cannot find variable '{}' in polynomial"
ERROR_IMPL = "Provide '{0}' on initialization or implement '_get_{0}' in inheriting 'ConstrainedObjective' class"
WARNING_NOTHING = "There is nothing in this Objective"
WARNING_DEPRECATION = "This way of instantiation is deprecated and will be removed soon, " \
                      "use method `get_from_instance` instead"


class Objective:
    """
    An objective is a function that shall be optimized in an optimization problem.
    Here we deal with polynomial objective functions for QUBO or Ising problems.
    Therefore, at this stage, there are no further constraints (anymore).
    """

    def __init__(self, polynomial=None, name=None, instance=None):
        """
        initialize Objective object

        :param (Polynomial) polynomial: the actual objective function
        :param (str or None) name: identifying name to differ between several objectives
        :param instance: instance object storing all data to construct the objective from
        """
        if instance:
            warn(WARNING_DEPRECATION, DeprecationWarning)
            self.polynomial = self._get_polynomial(instance)
            self.name = name or self._get_name(instance)
        else:
            self.polynomial = polynomial
            self.name = name

        super().__init__()
        self.check_consistency()

    def check_consistency(self):
        """ check if the data is consistent """
        if not isinstance(self.polynomial, Polynomial):
            raise ValueError(ERROR_POLYNOMIAL)
        if not self.polynomial:
            warn(WARNING_NOTHING)

    def __eq__(self, other):
        if isinstance(other, Objective):
            return self.name == other.name and self.polynomial == other.polynomial
        return False

    def __repr__(self):
        """ get nice string representation """
        return self.__class__.__name__ + f"({repr(self.polynomial)}, {repr(self.name)})"

    def __str__(self):
        """ get nice human-readable string representation of the objective """
        objective = f"min  {self.polynomial}\ns.t. "
        domains = sorted(set(variables.to_domain_string(var, self.polynomial.__class__.__name__)
                             for var in self.polynomial.variables))
        domains = "\n     ".join(domains)
        return objective + domains

    @classmethod
    def get_from_instance(cls, instance, name=None):
        """
        get the implemented inheriting Objective object based on the instance data

        :param (Instance or object) instance: An object of the implemented (inheriting) Instance class
        :param (str or None) name: the name of the resulting object
        :return: the initialized object
        """
        polynomial = cls._get_polynomial(instance)
        name = name or cls._get_name(instance)
        return cls(polynomial, name)

    def is_binary(self):
        """
        check if the objective's polynomial is binary

        :return: True if the polynomial is binary
        """
        return isinstance(self.polynomial, PolyBinary)

    def is_ising(self, inverted=None):
        """ check if the objective's polynomial is Ising

        :param (bool or None) inverted: if None, only checks for Ising without the inverted flag
                                        if True, additionally checks if the Ising polynomial is inverted,
                                        if False, additionally checks if the Ising polynomial is not inverted
        :return: True if the polynomial is Ising
        """
        if inverted is None:
            return isinstance(self.polynomial, PolyIsing)
        if inverted:
            return isinstance(self.polynomial, PolyIsing) and self.polynomial.is_inverted()
        return isinstance(self.polynomial, PolyIsing) and not self.polynomial.is_inverted()

    def apply_to_polynomial(self, func, new_name=None):
        """
        apply the function to the polynomial and thus extract another objective

        :param (callable) func: a mapping from the polynomial to a new one
        :param (str or None) new_name: name of the new objective, by default the original name is used
        :return: the new objective
        """
        new_name = new_name or self.name
        new_poly = func(self.polynomial)
        return Objective(new_poly, new_name)

    def to_binary(self, new_name=None):
        """
        convert this objective to a binary one

        :param (str or None) new_name: name of the new objective, by default the original name is used
        :return: the new Objective with binary polynomial
        """
        if self.is_binary() and not new_name:
            return self
        return self.apply_to_polynomial(PolyBinary.from_unknown_poly, new_name)

    def to_ising(self, invert=False, new_name=None):
        """
        convert this objective to an Ising one, with invert set to True the inverted Ising objective can be obtained

        :param (bool) invert: if True, in case the objective is binary it will be converted to inverted Ising,
                              in case the objective is Ising already it will be inverted
        :param (str or None) new_name: name of the new objective, by default the original name is used
        :return: the new Objective with Ising polynomial
        """
        if self.is_ising() and not invert and not new_name:
            return self
        return self.apply_to_polynomial(partial(PolyIsing.from_unknown_poly, invert=invert), new_name)

    def compact(self, new_name=None):
        """
        get a new Objective with a compact Polynomial

        :param (str or None) new_name: name of the new objective, by default the original name is used
        :return: the Objective with a compacted polynomial,
                 the VariableMapping of the original polynomial to new one (or None if it was already compact)
        """
        if self.polynomial.is_compact():
            return self, None
        return self.apply_to_polynomial(Polynomial.compact, new_name), VariableMapping(self.polynomial.variables)

    def break_symmetry_by_fixing_variable(self, variable=-1, value=1, new_name=None):
        """
        in case there are no linear terms (no local fields) in the Ising polynomial,
        the inverted variable assignment yields the same objective value as the non-inverted,
        we can break the symmetry explicitly by fixing one variable to a given value,
        this reduces the complexity by one without loss of generality

        :param (int or str or tuple) variable: variable to be fixed,
                                               by default -1 corresponding to the last in the sorted list
        :param (int) value: value to which the variable is fixed, by default 1
        :param (str or None) new_name: name of the new objective, by default the original name is used
        :return: the new Objective with one variable evaluated to the value
        """
        if not self.is_ising():
            raise ValueError(ERROR_ISING)
        if any(self.polynomial.coefficients_lists[1]):
            raise ValueError(ERROR_ZERO)
        if variable != -1 and variable not in self.polynomial.variables:
            raise ValueError(ERROR_VARIABLE.format(variable))
        if variable == -1:
            variable = self.polynomial.variables[-1]
        return self.apply_to_polynomial(partial(Polynomial.evaluate, var_assignments={variable: value}), new_name)

    @staticmethod
    @abstractmethod
    def _get_polynomial(instance):
        """
        get the objective polynomial from the instance data,
        needs to be implemented in subclasses for automatic generation

        :param instance: instance object storing all data to construct the objective polynomial from
        :return: the polynomial representing the objective function
        """
        raise NotImplementedError(ERROR_IMPL.format(POLYNOMIAL))

    @staticmethod
    def _get_name(instance):  # pylint: disable=unused-argument
        """
        get the name from the instance data,
        can be implemented in subclasses for automatic generation, is not enforced

        :param instance: instance object storing all data to construct the name from
        :return: the name of the object
        """
        return None
