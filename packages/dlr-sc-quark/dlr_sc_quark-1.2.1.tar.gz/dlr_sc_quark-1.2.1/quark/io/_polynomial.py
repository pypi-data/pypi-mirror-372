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

""" module for the IO of the Polynomial """

import ast

from quark import Polynomial
from . import add, hdf5_datasets, hdf5_attributes, txt
from ._variable_mapping import write_variables, read_variables


FLAT_POLYNOMIAL = "flat_polynomial"


add.save_load_exists(Polynomial)

@add.self_method(Polynomial)
def write_hdf5(polynomial, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (Polynomial) polynomial: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    polynomial.sort_entries()
    if polynomial.is_flat():
        flat_polynomial = polynomial
    else:
        flat_polynomial = polynomial.compact()
        write_variables(polynomial.variables, group)
    hdf5_datasets.write_dataset(group, FLAT_POLYNOMIAL, dataset=flat_polynomial)
    hdf5_attributes.write_attributes(group, **polynomial.coefficients_info)

@add.static_method(Polynomial)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    flat_poly_dict_np = hdf5_datasets.read_dataset(group, FLAT_POLYNOMIAL)
    flat_poly_dict = {tuple(int(i) for i in k): v for k, v in flat_poly_dict_np.items()}
    poly = Polynomial(flat_poly_dict)

    composite_variables = read_variables(group)
    if composite_variables:
        poly = poly.replace_variables(composite_variables)
    return {"d": poly, "variable_tuples_already_formatted": True}


# Adding IO methods to Polynomial that call the corresponding ones of txt
add.save_load_exists(Polynomial, txt, "txt")

@add.self_method(Polynomial)
def write_txt(polynomial, txt_file):
    """
    write data in opened text file

    :param (Polynomial) polynomial: the polynomial to be saved
    :param (file) txt_file: the file to save the data in
    """
    txt_file.write(super(Polynomial, polynomial).__repr__().replace(", (", ",\n ("))

@add.static_method(Polynomial)
def read_txt(lines):
    """
    read data from opened text file

    :param (list[str]) lines: the loaded lines of the text file to load the data from
    :return: the data as keyword arguments
    """
    line = "".join(lines).replace("\n", "")
    return {"d": ast.literal_eval(line)}
