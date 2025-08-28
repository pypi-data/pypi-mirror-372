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

""" module for helper functions for IO of attributes with HDF5 files """

import collections.abc
from numbers import Integral, Real
import numpy as np


ERROR_DATASET   = "Given value does not have an easy data structure, create dataset instead"
ERROR_NOT_FOUND = "Did not find attribute '{}' at group '{}' in HDF5 file '{}'"


def write_attribute(group, name, obj=None, value=None):
    """
    write attribute at the open group of an HDF5 file,
    either the value of the attribute is taken from the provided object or needs to be given explicitly

    :param (h5py.Group) group: the group in the HDF5 file at which the attribute will be attached
    :param (str) name: the name under which the attribute is stored
    :param obj: the object with an attribute called as name, whose value is taken as the attribute to be stored
    :param value: the explicit attribute value which shall be stored if no object is given
    """
    # if the object is given it should have an attribute which is called name
    if obj is not None and hasattr(obj, name):
        value = getattr(obj, name)
    value = _format_attribute(value)

    # if the attribute already exists at the group it will be deleted and overwritten
    if name in group.attrs:
        del group.attrs[name]
    group.attrs.create(name, value)

def write_attributes(group, obj=None, *names, **names_to_values):  # pylint: disable=keyword-arg-before-vararg
    """
    write several attributes at the open group of an HDF5 file,
    either provide the names of the attributes of the given object yielding the values or
    give the explicit dictionary of names to values as keyword arguments

    :param (h5py.Group) group: the HDF5 group to store the attributes at
    :param obj: the object whose attributes to take as attributes to be stored
    :param (str) names: attributes of the object that shall be stored (not to be used if no object is given)
    :param names_to_values: keyword arguments of explicit attribute values with names,
                            if no object is given or additional values shall be stored
    """
    for name in names:
        write_attribute(group, name, obj)
    for name, value in names_to_values.items():
        write_attribute(group, name, value=value)

def _format_attribute(value):
    """
    check if value has correct type and reformat it if necessary

    :param value: the attribute value
    :return the corrected value
    """
    if value is None:
        return np.nan
    if isinstance(value, str):
        return np.bytes_(value)  # replaced np.string_() with np.bytes_ as suggested in changelog
    if not np.isscalar(value):
        if isinstance(value, set):
            value = list(value)
        if not isinstance(value, collections.abc.Sequence) or not all(np.isscalar(v) for v in value):
            raise ValueError(ERROR_DATASET)
    return value

def read_attribute(group, name, check_existence=True):
    """
    read attribute from the open group of an HDF5 file

    :param (h5py.Group) group: the group in the HDF5 file where the attribute is stored
    :param (str) name: the name under which the attribute is stored
    :param (bool) check_existence: if True then an error will be thrown if the attribute is not found,
                                   if False None will be returned without error
    :return: the attribute value
    """
    # if it is there and not Nan the found value will be returned
    if name in group.attrs:
        value = group.attrs[name]
        if not (isinstance(value, float) and np.isnan(value)):
            if isinstance(value, bytes):
                return value.decode()
            if isinstance(value, Integral):
                return int(value)
            if isinstance(value, Real):
                return float(value)
            return value

    # if is not found and the existence is obligatory
    elif check_existence:
        raise ValueError(ERROR_NOT_FOUND.format(name, group.name, group.file.filename))

    # if it does not exist or is Nan
    return None

def read_attributes(group, *names, check_existence=True):
    """
    read several attributes from the open group of an HDF5 file

    :param (h5py.Group) group: the group in the HDF5 file where the attributes are stored
    :param (str) names: the names under which the attributes are stored
    :param (bool) check_existence: if True then an error will be thrown if an attribute is not found,
                                   if False None will be returned without error
    :return: dictionary with the attributes keyed by names
    """
    return {name : read_attribute(group, name, check_existence) for name in names}
