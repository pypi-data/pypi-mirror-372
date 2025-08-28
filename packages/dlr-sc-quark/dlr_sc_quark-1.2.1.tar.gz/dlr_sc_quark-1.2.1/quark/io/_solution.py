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

""" module for the IO of the Solution """

from numbers import Integral

from quark import Solution
from . import add, hdf5_attributes, hdf5_datasets
from ._variable_mapping import write_variables, read_variables


ATTRS_IMPORTANT   = ["objective_value", "solving_success", "solving_status", "solving_time"]
ATTRS_UNIMPORTANT = ["total_time", "dual_gap", "dual_bound"]
ATTRS = ATTRS_IMPORTANT + ATTRS_UNIMPORTANT
VAR_ASSIGNMENTS = "var_assignments"


add.save_load_exists(Solution)

@add.static_method(Solution)
def get_identifying_attributes():
    """ the attributes that identify an object of the class """
    return ["name"]

@add.self_method(Solution)
def write_hdf5(solution, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (Solution) solution: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    hdf5_attributes.write_attributes(group, solution, *ATTRS)
    if all(isinstance(var, Integral) for var in solution.keys()):
        var_assignments = solution
    else:
        # the variables are more complicated and need to be stored differently
        var_assignments = solution.replace_variables({var: index for index, var in enumerate(solution.keys())})
        write_variables(solution.keys(), group)
    hdf5_datasets.write_dataset(group, VAR_ASSIGNMENTS, dataset=var_assignments)


@add.static_method(Solution)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    init_kwargs = hdf5_attributes.read_attributes(group, *ATTRS_IMPORTANT)
    init_kwargs.update(hdf5_attributes.read_attributes(group, *ATTRS_UNIMPORTANT, check_existence=False))

    var_assignments = hdf5_datasets.read_dataset(group, VAR_ASSIGNMENTS)
    composite_variables = read_variables(group)
    if composite_variables:
        var_assignments = {composite_variables[index]: value for index, value in var_assignments.items()}

    init_kwargs[VAR_ASSIGNMENTS] = var_assignments
    return init_kwargs
