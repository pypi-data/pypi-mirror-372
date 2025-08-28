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

""" module for the IO of the ConstrainedObjective """

from quark import ConstrainedObjective, ConstraintBinary
from . import add, hdf5
from .poly_utils import write_poly_with_type, read_poly_with_type


OBJECTIVE_POLY = "objective_poly"
CONSTRAINTS    = "constraints"


add.save_load_exists(ConstrainedObjective)

@add.static_method(ConstrainedObjective)
def get_identifying_attributes():
    """ the attributes that identify an object of the class """
    return ["name"]

@add.self_method(ConstrainedObjective)
def write_hdf5(constrained_objective, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (ConstrainedObjective) constrained_objective: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    write_poly_with_type(group, constrained_objective.objective_poly, OBJECTIVE_POLY)
    for name, constraint in constrained_objective.items():
        hdf5.save_in(constraint, group, name)

@add.static_method(ConstrainedObjective)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    objective_poly = read_poly_with_type(group, OBJECTIVE_POLY)
    constraints = {}
    for name in group:
        if name != OBJECTIVE_POLY:
            constraints[name] = hdf5.load_from(ConstraintBinary, group, group_name=name)
    return {OBJECTIVE_POLY: objective_poly, CONSTRAINTS: constraints}
