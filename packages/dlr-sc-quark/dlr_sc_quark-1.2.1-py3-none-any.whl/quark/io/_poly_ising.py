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

""" module for the IO of the PolyIsing """

import ast

from quark import PolyIsing, Polynomial
from . import add, hdf5, hdf5_attributes


INVERTED = "_inverted"


@add.self_method(PolyIsing)
def write_hdf5(polynomial, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (PolyIsing) polynomial: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    hdf5.save_in(super(PolyIsing, polynomial), group)
    hdf5_attributes.write_attribute(group, INVERTED, polynomial)

@add.static_method(PolyIsing)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    init_kwargs = hdf5.load_data_from(super(PolyIsing, PolyIsing), group)
    init_kwargs.update(inverted=hdf5_attributes.read_attribute(group, INVERTED))
    return init_kwargs


@add.self_method(PolyIsing)
def write_txt(polynomial, txt_file):
    """
    write data in the opened text file

    :param (PolyIsing) polynomial: the object whose data shall be stored
    :param (file) txt_file: the file to store the data in
    """
    txt_file.write(f"{INVERTED}={polynomial.is_inverted()}\n")
    txt_file.write(super(Polynomial, polynomial).__repr__().replace(", (", ",\n ("))

@add.static_method(PolyIsing)
def read_txt(lines):
    """
    read data from the opened text file

    :param (list) lines: the loaded lines of the text file to read the data from
    :return: the data as keyword arguments
    """
    inverted = ast.literal_eval(str(lines[0]).replace(f"{INVERTED}=", ""))
    poly_line = "".join(lines[1:]).replace("\n", "")
    poly_dict = ast.literal_eval(poly_line)
    return {"d": poly_dict, "inverted": inverted}
