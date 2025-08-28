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

""" module for the IO of the ConstraintBinary """

from quark import ConstraintBinary
from . import add, hdf5_attributes
from .poly_utils import write_poly_with_type, read_poly_with_type


POLYNOMIAL  = "polynomial"
LOWER_BOUND = "lower_bound"
UPPER_BOUND = "upper_bound"


add.save_load_exists(ConstraintBinary)

@add.self_method(ConstraintBinary)
def write_hdf5(constraint_binary, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (ConstraintBinary) constraint_binary: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    hdf5_attributes.write_attributes(group, constraint_binary, LOWER_BOUND, UPPER_BOUND)
    write_poly_with_type(group, constraint_binary.polynomial)

@add.static_method(ConstraintBinary)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    init_kwargs = hdf5_attributes.read_attributes(group, LOWER_BOUND, UPPER_BOUND)
    init_kwargs.update(polynomial=read_poly_with_type(group))
    return init_kwargs
