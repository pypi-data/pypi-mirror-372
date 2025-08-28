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

""" module for helper functions for IO with HDF5 files """

import os
import ast
from warnings import warn
import h5py


WRITE_HDF5 = "write_hdf5"
READ_HDF5 = "read_hdf5"
REQUIRED_POSITIONAL_ARGUMENT = "required positional argument"
GET_IDENTIFYING_ATTRIBUTES = "get_identifying_attributes"

ERROR_GROUP_NAMES = "Either provide prefix for default group name or full group name"
ERROR_WRITE       = "Object of type '{}' does not have a write_hdf5 method"
ERROR_READ        = "Class '{}' does not have a read_hdf5 method"
ERROR_IO          = "IO is not implemented correctly"
ERROR_IDENTIFIER  = "Either give identifier '{}' of the class or a full group name"
ERROR_GROUP       = "Did not find group '{}' in HDF5 file '{}'"
ERROR_SUPER       = "(Super?) Class does not have a {} method"

WARNING_EXISTED   = "Group '{}' already existed in file '{}' and got deleted"
WARNING_PARSE     = "Intermediate identifier is None, group name cannot be parsed back"
WARNING_STRING    = "Experimental parsing of attributes from group name"


def save(obj, filename, prefix_group_name=None, full_group_name=None, mode="a"):
    """
    save object in an HDF5 file

    :param obj: the object to be saved
    :param (str) filename: the name of the HDF5 file
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param (str or None) full_group_name: the full name of the HDF5 group inside the HDF5 file replacing the default,
                                          if the group name already exists in the file, it will be overwritten
    :param (str) mode: append to file ('a') or overwrite file ('w')
    """
    if prefix_group_name and full_group_name:
        raise ValueError(ERROR_GROUP_NAMES)

    if not full_group_name:
        identifiers = {identifier: getattr(obj, identifier) for identifier in get_identifying_attributes(obj)}
        _check_nones(list(identifiers.values()))
        group_name = get_group_name(type(obj), prefix_group_name, **identifiers)
    else:
        group_name = full_group_name

    with h5py.File(filename, mode) as h5file:
        save_in(obj, h5file, group_name)

def save_in(obj, h5_file_or_group, group_name=None):
    """
    save object in an already opened HDF5 file or a group in an HDF5 file

    :param obj: the object to be saved
    :param (h5py.File or h5py.Group) h5_file_or_group: the HDF5 file or the group
    :param (str or None) group_name: the name of the HDF5 group inside the given HDF5 file or group,
                                     if the group name already exists in the file it will be overwritten,
                                     if not given, no subgroup is created
    :raises ValueError if the object does not have a 'write_hdf5' method
    """
    if group_name:
        # if the group is already there, it is deleted and recreated
        if group_name in h5_file_or_group:
            del h5_file_or_group[group_name]
            warn(WARNING_EXISTED.format(group_name, h5_file_or_group.filename))
        group = h5_file_or_group.create_group(group_name)
    else:
        group = h5_file_or_group

    _try_write(obj, group)

def _try_write(obj, group):
    """
    try to call 'write_hdf5' on the object and raise error if it does not have it
    (this is either because the class does not have an IO implementation or the IO is not loaded properly)
    """
    try:
        obj.write_hdf5(group)
    except AttributeError as ae:
        # checking that the error is about the correct attribute
        assert WRITE_HDF5 in ae.args[0]
        raise ValueError(ERROR_WRITE.format(type(obj).__name__)) from ae
    except ValueError as ve:
        # Since the IO might be nested (some objects' IO might rely on the IO of another)
        # there might already be an ValueError thrown
        # catching it and re-raising it for better readability of the stack trace in console
        raise ve from ve

def _check_nones(values):
    if None in values:
        for i in range(len(values) - 1):
            if values[i] is None and values[i+1] is not None:
                warn(WARNING_PARSE)
                return


def load(cls, filename, prefix_group_name=None, full_group_name=None, **identifiers):
    """
    load object of a certain class from an HDF5 file

    :param cls: the type of the object to be loaded
    :param (str) filename: the name of HDF5 file
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param (str or None) full_group_name: the full name of the HDF5 group inside the HDF5 file replacing the default
    :param identifiers: keywords dict with {attribute_name : value} which are unique for an object of the given class
    :return the loaded object of the given class
    """
    if prefix_group_name and full_group_name:
        raise ValueError(ERROR_GROUP_NAMES)

    if full_group_name and not identifiers:
        # this is possible but should be avoided if identifiers can be given explicitly
        identifiers = parse_identifiers_from_group_name(cls, full_group_name)

    # get the group in the file
    group_name = full_group_name or get_group_name(cls, prefix_group_name, **identifiers)

    with h5py.File(filename, "r") as h5file:
        loaded_obj = load_from(cls, h5file, group_name=group_name, **identifiers)
    return loaded_obj

def load_from(cls, h5_file_or_group, group_name=None, **identifiers):
    """
    load object of a certain class from an already opened HDF5 file or a group in an HDF5 file

    :param cls: the type of the object to be loaded
    :param (h5py.File or h5py.Group) h5_file_or_group: the file or the group
    :param (str or None) group_name: the name of the HDF5 group inside the given HDF5 file or group,
                                     if the group name already exists in the file it will be overwritten,
                                     if not given, no subgroup is used
    :param identifiers: keywords dict with {attribute_name : value} which are unique for an object of the given class
    :raises ValueError if the object does not have a 'read_hdf5' method
    :return the loaded object of the given class
    """
    loaded_data = load_data_from(cls, h5_file_or_group, group_name=group_name, **identifiers)
    try:
        # initialize object with loaded data
        obj = cls(**loaded_data)
    except TypeError as te:
        assert REQUIRED_POSITIONAL_ARGUMENT in te.args[0]
        missing = te.args[0].split("'")[1]
        assert missing in get_identifying_attributes(cls), ERROR_IO
        raise ValueError(ERROR_IDENTIFIER.format(missing)) from te
    return obj

def load_data_from(cls, h5_file_or_group, group_name=None, **identifiers):
    """
    load data of object of a certain class from an already opened HDF5 file or a group in an HDF5 file

    :param cls: the type of object to be loaded
    :param (h5py.File or h5py.Group) h5_file_or_group: the file or the group
    :param (str or None) group_name: the name of the HDF5 group inside the given HDF5 file or group,
                                     if the group name already exists in the file it will be overwritten,
                                     if not given, no subgroup is used
    :param identifiers: keywords dict with {attribute_name : value} which are unique for an object of the given class
    :raises ValueError if the object does not have a 'read_hdf5' method
    :return the loaded data for an object of the given class
    """
    if group_name:
        if group_name not in h5_file_or_group:
            raise ValueError(ERROR_GROUP.format(group_name, h5_file_or_group.file.filename))
        group = h5_file_or_group[group_name]
    else:
        group = h5_file_or_group

    if group_name and not identifiers:
        # this is possible but should be avoided if identifiers can be given explicitly
        identifiers = parse_identifiers_from_group_name(cls, group_name)

    init_kwargs = _try_read(cls, group)
    init_kwargs.update(**identifiers)
    return init_kwargs

def _try_read(cls, group):
    """
    try to call 'read_hdf5' on the class and raise error if it does not have it
    (this is either because the class does not have an IO implementation or the IO is not loaded properly)
    """
    try:
        loaded_data = cls.read_hdf5(group)
    except AttributeError as ae:
        # checking that the error is about the correct attribute
        assert READ_HDF5 in ae.args[0]
        if hasattr(cls, "__name__"):
            raise ValueError(ERROR_READ.format(cls.__name__)) from ae
        raise ValueError(ERROR_SUPER.format(READ_HDF5)) from ae

    except ValueError as ve:
        # Since the IO might be nested (some objects' IO might rely on the IO of another)
        # there might already be an ValueError thrown
        # catching it and re-raising it for better readability of the stack trace in console
        raise ve from ve
    return loaded_data



def load_all(cls, filename, prefix_group_name=None, used_default=True, index_range=None):
    """
    load all objects of a certain class from the HDF5 file

    :param cls: the type of the objects to be loaded
    :param (str) filename: the name of the HDF5 file
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param (bool) used_default: if True, the default method was used for storing,
                                you can set this flag to False and no default class prefix will be added
                                but this could cause problems if there are different objects stored in the group
    :param (list or range or None) index_range: specify the objects which shall be loaded according to the index range
                                                they appear in
    :return: the loaded objects of the given type
    """
    with h5py.File(filename, "r") as h5file:
        loaded_objs = load_all_from(cls, h5file, prefix_group_name, used_default, index_range)
    return loaded_objs

def load_all_from(cls, h5_file_or_group, prefix_group_name=None, used_default=True, index_range=None):
    """
    load all objects of a certain class from an already opened HDF5 file or a group in an HDF5 file

    :param cls: the type of the objects to be loaded
    :param (h5py.File or h5py.Group) h5_file_or_group: the file or the group
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param (bool) used_default: if True, the default method was used for storing,
                                you can set this flag to False and no default class prefix will be added
                                but this could cause problems if there are different objects stored in the group
    :param (list or range or None) index_range: specify the objects which shall be loaded according to the index range
                                                they appear in
    :return: the loaded objects of the given type
    """
    depth = 0
    if used_default:
        prefix_group_name = (prefix_group_name or "") + "/" + cls.__name__
        depth = len(get_identifying_attributes(cls)) - 1
    all_subgroup_names = get_all_subgroup_names_from(h5_file_or_group, prefix_group_name, depth)
    if index_range:
        all_subgroup_names = [all_subgroup_names[i] for i in index_range]
    all_objs = []
    for name in all_subgroup_names:
        obj = load_from(cls, h5_file_or_group, name)
        all_objs.append(obj)
    return all_objs

def get_all_subgroup_names(filename, prefix_group_name=None, depth=0, complete=True):
    """
    get the names of all objects in the group in the HDF5 file

    :param (str) filename: the name of the HDF5 file
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param (int) depth: the number of subgroups to collect recursively
    :param (bool) complete: if True, the full group names are returned
    :return: the names of all objects stored in the file
    """
    with h5py.File(filename, "r") as h5file:
        names = get_all_subgroup_names_from(h5file, prefix_group_name, depth, complete)
    return names

def get_all_subgroup_names_from(h5_file_or_group, prefix_group_name=None, depth=0, complete=True):
    """
    get the names of all objects in an already opened HDF5 file or a group in an HDF5 file

    :param (h5py.File or h5py.Group) h5_file_or_group: the file or the group
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param (int) depth: the number of subgroups to collect recursively
    :param (bool) complete: if True, the full group names are returned
    :return: the names of all objects stored in the file
    """
    if prefix_group_name and not prefix_group_name in h5_file_or_group:
        return []
    if not prefix_group_name:
        group = h5_file_or_group
    else:
        group = h5_file_or_group[prefix_group_name]

    subgroup_names = _get_subgroup_names_recursive(group, depth)
    if complete and prefix_group_name:
        if not str(prefix_group_name).endswith("/"):
            prefix_group_name = prefix_group_name + "/"
        subgroup_names = sorted([prefix_group_name + str(name) for name in subgroup_names])

    return subgroup_names

def _get_subgroup_names_recursive(group, depth=0):
    """ go through all subdirectories recursively """
    if depth == 0:
        return sorted([str(name) for name in group.keys()])
    group_names = []
    for subgroup_name in group.keys():
        subgroup = group[subgroup_name]
        names = sorted([subgroup_name + "/" + str(name) for name in _get_subgroup_names_recursive(subgroup, depth-1)])
        group_names += names
    return group_names

def is_subgroup(h5_file_or_group, name):
    """
    check whether the given name is a group in the opened HDF5 file or a group in an HDF5 file
    (in contrast to e.g. a dataset)

    :param (h5py.File or h5py.Group) h5_file_or_group: the file or the group
    :param (str) name: the name of the group to be checked
    """
    if name in h5_file_or_group:
        sub_obj = h5_file_or_group[name]
        return isinstance(sub_obj, h5py.Group)
    return False


def exists(cls, filename, prefix_group_name=None, full_group_name=None, **identifiers):
    """
    check if an object of a certain class already exists in an HDF5 file

    :param cls: the type of the object to be checked
    :param (str) filename: the name of HDF5 file
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param (str or None) full_group_name: the full name of the HDF5 group inside the HDF5 file replacing the default
    :param identifiers: keywords dict with {attribute_name : value} which are unique for an object of the given class
    :return: True if there is already an object of the given type in the file
    """
    if prefix_group_name and full_group_name:
        raise ValueError(ERROR_GROUP_NAMES)

    if os.path.exists(filename):
        with h5py.File(filename, "r") as h5file:
            full_group_name = full_group_name or get_group_name(cls, prefix_group_name, **identifiers)
            return full_group_name in h5file
    return False

def get_identifying_attributes(cls):
    """
    get the identifiers of the class, if it implements them

    :param cls: the type of the class to be checked
    :return: the list of identifying attributes
    """
    if hasattr(cls, GET_IDENTIFYING_ATTRIBUTES) and callable(cls.get_identifying_attributes):
        return cls.get_identifying_attributes()
    return []

def get_group_name(cls, prefix_group_name=None, **identifiers):
    """
    get the default group name from the class

    :param cls: the class to get the group name from
    :param (str or None) prefix_group_name: the group hierarchy above the default group name
    :param identifiers: keywords dict with {attribute_name : value} which are unique for an object of the given class
    :return: the group name
    """
    group_name = (prefix_group_name + "/" if prefix_group_name else "") + cls.__name__
    expected_attributes = get_identifying_attributes(cls)
    for identifier in expected_attributes:
        if identifier in identifiers and not identifiers[identifier] is None:
            group_name += f"/{identifiers[identifier]}"
    return group_name

def parse_identifiers_from_group_name(cls, group_name):
    """
    parse the identifying attributes from the group name (experimental status),
    starts at end of group name string with last identifier and goes backwards in the group hierarchy

    :param cls: the class to get the identifiers for
    :param (str) group_name: the name of the group under which the object is stored
    :return: keywords dict with {attribute_name : value} which are unique for an object of the given class
    """
    sorted_identifiers = get_identifying_attributes(cls)
    subgroups = group_name.split("/")
    if subgroups[0] == cls.__name__:
        # in case of the default group name it starts with the class name, which we can drop here
        subgroups = subgroups[1:]
    # if we have less subgroups than identifiers then we only take the first identifiers
    sorted_identifiers = sorted_identifiers[:len(subgroups)][::-1]
    # trying to parse the subgroup name to the original values starting from last
    identifiers = {identifier : _try_parse(subgroups[-(i + 1)]) for i, identifier in enumerate(sorted_identifiers)}
    return identifiers

def _try_parse(value):
    """ try to parse the original value from the string """
    warn(WARNING_STRING)
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value
