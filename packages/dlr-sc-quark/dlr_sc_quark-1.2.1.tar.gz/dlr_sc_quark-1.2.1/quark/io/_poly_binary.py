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

""" module for the IO of the PolyBinary """

import os
import ast
from warnings import warn

from quark import PolyBinary
from . import add


@add.self_method(PolyBinary)
def save_bp(polynomial, filename):
    """
    save polynomial in bp file (only one polynomial per file)

    :param polynomial: the polynomial to be saved
    :param (str) filename: the name of bp file
    """
    if not polynomial.is_quadratic() or not polynomial.is_flat() or polynomial.is_constant():
        raise ValueError("Can only write non-constant, flat and quadratic binary polynomials in this format")
    if polynomial.offset:
        warn("Offset will be ignored")

    with open(filename, mode="w", encoding="utf-8") as bp_file:
        # get the corresponding function for writing and call it
        bp_file.write(f"{max(polynomial.variables)} {len(polynomial.linear) + len(polynomial.quadratic)}\n")
        for (var,), coeff in polynomial.linear.items():
            bp_file.write(f"{var} {var} {coeff}\n")
        for (var1, var2), coeff in polynomial.quadratic.items():
            bp_file.write(f"{var1} {var2} {coeff}\n")

@add.class_method(PolyBinary)
def load_bp(cls, filename):
    """
    load polynomial of the given class from bp file

    :param cls: the type of the polynomial to be loaded
    :param (str) filename: the name of bp file
    """
    with open(filename, "r", encoding="utf-8") as bp_file:
        lines = bp_file.readlines()

    poly_dict = _get_poly_dict(lines)
    loaded_polynomial = cls(poly_dict)
    return loaded_polynomial

@add.class_method(PolyBinary)
def exists_bp(cls, filename):
    """
    check if a binary polynomial exists in the bp file

    :param cls: the type of object to be checked
    :param (str) filename: the name of bp file
    :return: True if there is already a binary polynomial in the file
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as pb_file:
            lines = pb_file.readlines()
        try:
            poly_dict = _get_poly_dict(lines)
            _ = cls(poly_dict)
            return True
        except ValueError:
            pass
    return False


def _get_poly_dict(lines):
    poly_dict = {}
    max_variable, num_terms = None, None
    for line in lines:
        if line == "\n" or line.startswith("#"):
            continue
        values = line.split(" ")
        if len(values) == 2:
            max_variable, num_terms = (ast.literal_eval(value) for value in values)
        else:
            var1, var2, coeff = (ast.literal_eval(value) for value in values)
            poly_dict[(var1, var2)] = coeff
    variables = set(var for var_tuple in poly_dict for var in var_tuple)
    if not max(variables) == max_variable or not len(poly_dict) == num_terms:
        raise ValueError("Something went wrong when reading the file")
    return poly_dict
