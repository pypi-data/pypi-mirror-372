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

""" module for the IO of the Embedding """

from quark import Embedding
from . import add, hdf5_datasets


VAR_NODES_MAP      = "var_nodes_map"
VAR_EDGES_MAP      = "var_edges_map"
COUPLING_EDGES_MAP = "coupling_edges_map"
EDGES              = "edges"


add.save_load_exists(Embedding)

@add.static_method(Embedding)
def get_identifying_attributes():
    """ the attributes that identify an object of the class """
    return ["name", "index"]

@add.self_method(Embedding)
def write_hdf5(embedding, group):
    """
    write data in attributes and datasets in the opened group of an HDF5 file

    :param (Embedding) embedding: the object whose data shall be stored
    :param (h5py.Group) group: the group to store the data in
    """
    edge_map = {edge: i for i, edge in enumerate(embedding.edges)}
    # replacing edges by their index in the edge list to be able to store it
    coupling_edges_map = {var: [edge_map[edge] for edge in edges]
                          for var, edges in embedding.coupling_edges_map.items()}
    var_edges_map = {var: [edge_map[edge] for edge in edges] for var, edges in embedding.var_edges_map.items()}

    hdf5_datasets.write_datasets(group, embedding, VAR_NODES_MAP, EDGES)
    hdf5_datasets.write_datasets(group, var_edges_map=var_edges_map, coupling_edges_map=coupling_edges_map)

@add.static_method(Embedding)
def read_hdf5(group):
    """
    read data from attributes and datasets of the opened group of an HDF5 file

    :param (h5py.Group) group: the group to read the data from
    :return: the data as keyword arguments
    """
    var_nodes_map = hdf5_datasets.read_dataset(group, VAR_NODES_MAP)
    init_kwargs = {VAR_NODES_MAP: {var: list(nodes) for var, nodes in var_nodes_map.items()}}

    edges = hdf5_datasets.read_dataset(group, EDGES, check_existence=False)
    if edges is not None:
        var_edges_map = _get_map(VAR_EDGES_MAP, group, edges)
        coupling_edges_map = _get_map(COUPLING_EDGES_MAP, group, edges)
        init_kwargs.update(var_edges_map=var_edges_map, coupling_edges_map=coupling_edges_map)
    return init_kwargs


def _get_map(name, group, edges):
    """ get and convert the corresponding dataset """
    edge_map = hdf5_datasets.read_dataset(group, name, check_existence=False)
    if edge_map is not None:
        edge_map = {var: [tuple(edges[i]) for i in edge_indices] for var, edge_indices in edge_map.items()}
    return edge_map
