# Copyright 2022 DLR-SC
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

""" module for the IO of the HardwareAdjacency """

from quark import HardwareAdjacency
from . import add, hdf5_datasets


EDGES = "edges"


add.save_load_exists(HardwareAdjacency)

@add.static_method(HardwareAdjacency)
def get_identifying_attributes():
    """ the attributes that identify an object of the class """
    return ["name"]

@add.self_method(HardwareAdjacency)
def write_hdf5(hardware_adjacency, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (HardwareAdjacency) hardware_adjacency: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    hdf5_datasets.write_dataset(group, EDGES, dataset=hardware_adjacency)


@add.static_method(HardwareAdjacency)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    return hdf5_datasets.read_datasets(group, EDGES)
