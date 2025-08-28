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

""" module for helper functions for storing different types of Polynomials """

from quark import Polynomial, PolyIsing, PolyBinary
from . import hdf5, hdf5_attributes


# Register mapping from group name to type
POLY_TYPES = [Polynomial, PolyIsing, PolyBinary]
POLY_STR_2_TYPE = {hdf5.get_group_name(poly_type): poly_type for poly_type in POLY_TYPES}

TYPE = "type"

ERROR_GROUP    = "Did not find Polynomial '{}' in group '{}' in hdf5 file '{}'"
ERROR_TOO_MUCH = "Found too much Polynomials in group '{}'"
ERROR_NO       = "Found no Polynomials in group '{}'"


def write_poly_with_type(group, polynomial, name=None):
    """
    write the polynomial in the opened group of an HDF5 file,
    either under the provided name or under the default group name for the Polynomial type
    (thus only one polynomial can be stored in the group if used without name)

    :param (h5py.Group) group: the group to store the data in
    :param (Polynomial) polynomial: the polynomial that shall be stored
    :param (str or None) name: the name of the group under which the polynomial is stored,
                               by default the Polynomial type is used
    """
    group_name = name or hdf5.get_group_name(type(polynomial))
    hdf5.save_in(polynomial, group, group_name=group_name)
    if name:
        # if the polynomial is stored under a different name, save the type as an attribute
        _add_poly_type(group, polynomial, name)

def _add_poly_type(group, polynomial, name):
    # if a name is given, the type of the Polynomial needs to be stored additionally
    poly_group = group[name]
    poly_type_str = hdf5.get_group_name(type(polynomial))
    # the type is added as an attribute
    hdf5_attributes.write_attribute(poly_group, TYPE, value=poly_type_str)


def read_poly_with_type(group, name=None):
    """
    read the polynomial from the opened group of an HDF5 file,
    if no name is given, the default group name is the Polynomial type
    (thus there should only be one Polynomial in the group without a name)

    :param (h5py.Group) group: the group to read the data from
    :param (str or None) name: the name of the group under which the polynomial is stored,
                               by default the first found Polynomial type is used
    :return: the loaded Polynomial
    """
    poly_type = _get_poly_type(group, name)
    group_name = name or hdf5.get_group_name(poly_type)
    return hdf5.load_from(poly_type, group, group_name=group_name)

def _get_poly_type(group, name=None):
    if name:
        if name not in group:
            raise ValueError(ERROR_GROUP.format(name, group.name, group.file.filename))
        poly_group = group[name]
        # read the type of the polynomial
        poly_type_str = hdf5_attributes.read_attribute(poly_group, TYPE, check_existence=False)
        # if we found no type check if the name itself corresponds to a valid type
        if not poly_type_str and name in POLY_STR_2_TYPE:
            poly_type_str = name
    else:
        # if no name is given, we need to find the stored Polynomial
        # check if there is some Polynomial among the stored objects in the group
        poly_type_strs = [entry for entry in group.keys() if entry in POLY_STR_2_TYPE]
        if len(poly_type_strs) > 1:
            # we do not know which Polynomial to choose when there are several
            raise ValueError(ERROR_TOO_MUCH.format(group.name))
        if len(poly_type_strs) < 1:
            raise ValueError(ERROR_NO.format(group.name))
        poly_type_str = poly_type_strs[0]

    poly_type = POLY_STR_2_TYPE.get(poly_type_str, Polynomial)
    return poly_type
