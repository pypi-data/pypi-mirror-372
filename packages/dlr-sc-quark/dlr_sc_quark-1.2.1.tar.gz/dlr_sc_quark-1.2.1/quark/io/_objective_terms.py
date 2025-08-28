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

""" module for the IO of the ObjectiveTerms """

from quark import ObjectiveTerms
from . import add, hdf5, hdf5_datasets
from .poly_utils import write_poly_with_type, read_poly_with_type


OBJECTIVE_TERMS        = "objective_terms"
CONSTRAINT_TERMS_NAMES = "constraint_terms_names"


add.save_load_exists(ObjectiveTerms)

@add.static_method(ObjectiveTerms)
def get_identifying_attributes():
    """ the attributes that identify an object of the class """
    return ["name"]

@add.self_method(ObjectiveTerms)
def write_hdf5(objective_terms, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (ObjectiveTerms) objective_terms: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    hdf5_datasets.write_dataset(group, CONSTRAINT_TERMS_NAMES, objective_terms)
    for name, poly in objective_terms.items():
        write_poly_with_type(group, poly, name)

@add.static_method(ObjectiveTerms)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    constraint_terms_names = hdf5_datasets.read_dataset(group, CONSTRAINT_TERMS_NAMES, check_existence=False)
    objective_terms = {}
    for name in group:
        if hdf5.is_subgroup(group, name):
            objective_terms[name] = read_poly_with_type(group, name)
    return {OBJECTIVE_TERMS: objective_terms, CONSTRAINT_TERMS_NAMES: constraint_terms_names}
