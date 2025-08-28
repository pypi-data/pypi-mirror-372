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

""" module for VariableMapping """

from functools import cached_property
from bidict import bidict

from .utils.variables import get_common_type, check_type_against, to_string


KEY   = "key"
VALUE = "value"
TYPE  = "type_{}s"

ERROR_INCONSISTENT = "The {}s have inconsistent types"
ERROR_INVALID =      "Invalid {} type"


class VariableMapping(bidict):
    """ A VariableMapping stores the variable conversion of Polynomials. """

    def __init__(self, variables=None):
        """
        initialize VariableMapping object

        :param (list or dict) variables: the mapping of the variables,
                                         if it is a list, the indices are mapped to the variables
        """
        if isinstance(variables, list):
            variables = dict(enumerate(variables))
        elif variables is None:
            variables = {}  # or raise a specific error if None is not allowed
        super().__init__(variables)

    @cached_property
    def type_keys(self):
        """ cache for the type of the keys """
        try:
            return get_common_type(list(self.keys()))
        except TypeError as te:
            raise ValueError(ERROR_INCONSISTENT.format(KEY)) from te

    @cached_property
    def type_values(self):
        """ cache for the type of the values """
        try:
            return get_common_type(list(self.values()))
        except TypeError as te:
            raise ValueError(ERROR_INCONSISTENT.format(VALUE)) from te

    def _clear_types(self):
        """ clear the cached types """
        for attr in [TYPE.format(KEY), TYPE.format(VALUE)]:
            for obj in [self, self.inverse]:
                try:
                    delattr(obj, attr)
                except AttributeError:
                    pass

    def _write(self, newkey, newval, oldkey, oldval, unwrites):
        """ extends 'bidict._prep_write' to check for the cached types """
        try:
            check_type_against(newkey, self.type_keys)
        except TypeError as te:
            raise ValueError(ERROR_INVALID.format(KEY)) from te
        try:
            check_type_against(newval, self.type_values)
        except TypeError as te:
            raise ValueError(ERROR_INVALID.format(VALUE)) from te
        if not self:
            self._clear_types()
        return super()._write(newkey, newval, oldkey, oldval, unwrites)

    def _pop(self, key):
        """ extends 'bidict._pop' to clear cached types if necessary """
        v = super()._pop(key)
        if not self:
            self._clear_types()
        return v

    def clear(self):
        """
        remove all elements from the dictionary,
        extends 'bidict.clear' to clear cached types
        """
        super().clear()
        self._clear_types()

    def __str__(self):
        """ get nice human-readable string representation of the variable mapping """
        sorted_vars = sorted(self.keys())
        max_length = max(len(to_string(var)) for var in sorted_vars)
        return "\n".join(to_string(var) + " " * (max_length - len(to_string(var))) + f" <-> {to_string(self[var])}"
                         for var in sorted_vars)
