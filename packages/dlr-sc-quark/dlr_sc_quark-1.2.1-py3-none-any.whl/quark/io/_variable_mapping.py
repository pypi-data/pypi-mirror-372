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

""" module for the IO of the VariableMapping """

from quark import VariableMapping
from quark.utils.variables import replace_in_tuples, replace_strs_by_ints, are_consecutive
from . import add, hdf5_datasets


VARIABLES             = "variables"
COMPOSITE_VARIABLES   = "composite_variables"
STRING_VARIABLE_PARTS = "string_variable_parts"

DATASETS = ["keys", "values"]


add.save_load_exists(VariableMapping)

@add.self_method(VariableMapping)
def write_hdf5(variable_mapping, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (VariableMapping) variable_mapping: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    for ds_name in DATASETS:
        variables = getattr(variable_mapping, ds_name)()
        if not are_consecutive(variables):
            write_variables(variables, group, "_" + ds_name)

def write_variables(variables, group, suffix=""):
    """ extract the parts of the variables and write them into the group """
    int_variables, int_to_str = replace_strs_by_ints(variables)
    hdf5_datasets.write_dataset(group, COMPOSITE_VARIABLES + suffix, dataset=int_variables)
    if int_to_str:
        hdf5_datasets.write_dataset(group, STRING_VARIABLE_PARTS + suffix, dataset=int_to_str)

@add.static_method(VariableMapping)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    variables = [read_variables(group, "_" + ds_name) for ds_name in DATASETS]
    if not variables[0] and variables[1]:
        return {VARIABLES: zip(range(len(variables[1])), variables[1])}
    if not variables[1] and variables[0]:
        return {VARIABLES: zip(variables[0], range(len(variables[0])))}
    assert all(variables)
    return {VARIABLES: zip(*variables)}

def read_variables(group, suffix=""):
    """ retrieve the parts of the variables """
    composite_variables = hdf5_datasets.read_dataset(group, COMPOSITE_VARIABLES + suffix, check_existence=False)
    if composite_variables is not None:
        composite_variables = list(tuple(int(i) for i in v) for v in composite_variables)
        int_to_str = hdf5_datasets.read_dataset(group, STRING_VARIABLE_PARTS + suffix, check_existence=False)
        if int_to_str:
            composite_variables = replace_in_tuples(composite_variables, int_to_str)
    return composite_variables
