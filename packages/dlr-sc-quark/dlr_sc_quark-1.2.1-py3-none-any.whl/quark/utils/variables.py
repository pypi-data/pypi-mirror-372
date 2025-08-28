# Copyright 2022 DLR-SC
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

""" module for polynomial variables utility functions """

from numbers import Integral


NOT_ITERABLE = "is not iterable"

ERROR_TYPE     = "Variable '{}' has invalid type '{}'"
ERROR_FORMAT   = "Tuple variable '{}' is not formatted correctly, should only contain ints and strings"
ERROR_EXPECTED = "Expected variable type '{}', but got '{}'"


def get_common_type(variables):
    """
    get the type of the variables in the iterable and check all variables against this type
    (use get_type on single variable instead if no check is needed)

    :param (list or set or tuple) variables: the set of variables to be checked
    :return: the common type of the variables
    """
    if not variables:
        return None
    try:
        var_iter = iter(variables)
        some_var = next(var_iter)
    except TypeError as te:
        assert te.args[0].endswith(NOT_ITERABLE)
        some_var = variables
        var_iter = []
    var_type = get_type(some_var)
    for var in var_iter:
        check_type_against(var, var_type)
    return var_type

def get_type(variable):
    """
    get and check the type of the variable

    :param variable: the variable to be checked
    :return: the type of the variable
    """
    var_type = type(variable)
    if issubclass(var_type, Integral) and not issubclass(var_type, bool):
        var_type = Integral
    if not is_valid_variable_type(var_type):
        raise TypeError(ERROR_TYPE.format(variable, var_type.__name__))
    if issubclass(var_type, tuple) and not has_valid_tuple_format(variable):
        raise ValueError(ERROR_FORMAT.format(variable))
    if issubclass(var_type, tuple):
        var_type = tuple
    return var_type

def is_valid_variable_type(var_type):
    """
    check if variable type corresponds to our convention: either int, str, tuple or None

    :param (type) var_type: the variable type to be checked
    :return: True, if the type is valid
    """
    return issubclass(var_type, Integral) and not issubclass(var_type, bool) \
           or issubclass(var_type, tuple) or var_type in (str, None)

def has_valid_tuple_format(variable):
    """
    check whether the variable has a valid format, i.e., the tuple only consists of strings and ints

    :param variable: the variable to be checked
    :return: True, if the variable has a valid format
    """
    return isinstance(variable, tuple) and all(isinstance(v, (str, Integral)) for v in variable)

def check_type_against(variable, expected_var_type):
    """
    check the actual type of the variable against the expected variable type

    :param variable: variable object whose type is checked
    :param (type) expected_var_type: the previously determined type the variable should have
    """
    var_type = get_type(variable)
    if expected_var_type and var_type != expected_var_type:
        raise TypeError(ERROR_EXPECTED.format(expected_var_type.__name__, var_type.__name__))

def are_consecutive(variables):
    """
    check if the variables tuples do only contain integers and all appearing variables are consecutive starting with 0

    :param (list or set) variables: the iterable of variables to be checked
    :return: True, if the variables are consecutive
    """
    if variables:
        try:
            return min(variables) == 0 and len(set(variables)) == max(variables) + 1
        except TypeError:
            return False
    return True

def to_string(variable, poly_type=None, placeholder=False):
    """
    get a nice string representation of the given variable

    :param (tuple or Integral or str) variable: the variable to be formatted
    :param (type or str) poly_type: the type of the polynomial, for Ising problems the standard letter is 's',
                                    while for binary it is 'x'
    :param (bool) placeholder: the indices will be replaced with the placeholder '*'
    :param poly_type: type of the polynomial, for Ising problems the standard letter is 's', while for binary 'x'
    :param placeholder: the indices will be replaced with the placeholder '*'
    :return: the nice string representation
    """
    if isinstance(poly_type, type):
        poly_type = poly_type.__name__
    var_letter = "s" if poly_type == "PolyIsing" else "x"
    if isinstance(variable, tuple):
        var_str, start = (f"{variable[0]}_", 1) if isinstance(variable[0], str) else (f"{var_letter}_", 0)
        return var_str + "_".join(str(v) if not placeholder else "*" for v in variable[start:])
    if isinstance(variable, Integral):
        return f"{var_letter}{variable if not placeholder else '*'}"
    return str(variable)

def to_domain_string(variable, poly_type=None):
    """
    get a nice string representation of the domain of the variable

    :param (tuple or Integral or str) variable: the variable to be formatted
    :param (type or str) poly_type: the type of the polynomial, for Ising problems the standard letter is 's',
                                    while for binary it is 'x'
    :return: the nice string representation
    """
    if isinstance(poly_type, type):
        poly_type = poly_type.__name__
    domain = "{-1, 1}" if poly_type == "PolyIsing" else "{0, 1}"
    return to_string(variable, poly_type, True) + " in " + domain

def replace_strs_by_ints(tuples):
    """
    replace the strings with ints in a list of tuples themselves containing either ints or strings,
    as strings in tuples cannot be stored easily therefore they need to be replaced with an int,
    they will be enumerated beginning with the largest contained int +1

    :param (list[tuple]) tuples: list of tuples themselves containing either ints or strings
    :return: list of tuples only containing ints and a mapping from the new ints to the old strings
    """
    all_parts = set(p for var in tuples for p in var)
    str_parts = sorted(set(p for p in all_parts if isinstance(p, str)))

    # if there are strings inside we replace them by numbers larger than the maximum number appearing
    if str_parts:
        max_int = max((p for p in all_parts if isinstance(p, Integral)), default=-1)
        int_to_str = dict(zip(range(max_int + 1, max_int + 1 + len(str_parts)), str_parts))
        str_to_int = {s: i for i, s in int_to_str.items()}
        tuples = replace_in_tuples(tuples, str_to_int)
        return tuples, int_to_str
    return tuples, None

def replace_in_tuples(tuples, replacement):
    """
    replace the elements of all tuples

    :param (list[tuple]) tuples: the list of tuples
    :param (list or dict or function) replacement: dictionary or function mapping from old variable to new one
    :return: the new tuples with replaced elements
    """
    return [replace_in_tuple(t, replacement) for t in tuples]

def replace_in_tuple(var_tuple, replacement):
    """
    create a new tuple with elements from the original tuple replaced by new values defined by replacement

    :param (tuple) var_tuple: the tuple in which the variables will be replaced
    :param (list or dict or function) replacement: dictionary or function mapping from old variable to new one
    :return: the new variable tuple
    """
    if callable(replacement):
        return tuple(map(replacement, var_tuple))
    return tuple(replacement[k] if k in replacement else k for k in var_tuple)
