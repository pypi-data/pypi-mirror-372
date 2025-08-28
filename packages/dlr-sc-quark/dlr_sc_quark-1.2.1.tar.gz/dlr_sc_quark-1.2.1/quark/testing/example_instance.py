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

""" module for ExampleInstance """

from quark.io import Instance, hdf5_datasets
from . import example_constrained_objective


EDGES = "edges"
DENSITY = "density"
COLORS = "colors"

ERROR_PREFIX = "Instance is not consistent: "
ERROR_EDGES  = "No edges given"
ERROR_COLORS = "No colors given"
ERROR_TWO    = "Edges need to have two nodes"


class ExampleInstance(Instance):
    """ An example implementation of an Instance for testing based on the MaxColorableSubgraph problem """

    def __init__(self, edges, colors):
        """
        an instance contains

        :param (list or set) edges: undirected edges of the graph -> define the set of nodes
        :param (list or set or int) colors: set of colors or int defining range of colors
        """
        self.edges = set(tuple(sorted(edge)) for edge in edges)
        self.nodes = set(node for edge in self.edges for node in edge)
        self.colors = set(range(colors)) if isinstance(colors, int) else set(colors)
        super().__init__()

    def check_consistency(self):
        """ check if the data is consistent """
        if len(self.edges) == 0:
            raise ValueError(ERROR_PREFIX + ERROR_EDGES)
        if len(self.colors) == 0:
            raise ValueError(ERROR_PREFIX + ERROR_COLORS)
        if not all(len(edge) == 2 for edge in self.edges):
            raise ValueError(ERROR_PREFIX + ERROR_TWO)

    def get_name(self):
        """ get an expressive name representing the instance """
        density = round(2 * len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1)), 2)
        return "_".join([self.__class__.__name__, DENSITY, f"{density}", COLORS, f"{len(self.colors)}"])

    def get_constrained_objective(self, name=None):
        """
        get the constrained objective object based on this instance data

        :param (str or None) name: the name of the object
        :return: the constrained objective
        """
        return example_constrained_objective.ExampleConstrainedObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_datasets(group, self, EDGES, COLORS)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        kwargs = hdf5_datasets.read_datasets(group, EDGES, COLORS)
        kwargs[EDGES] = [tuple(edge) for edge in kwargs[EDGES]]
        kwargs[COLORS] = list(kwargs[COLORS])
        return {**kwargs}
