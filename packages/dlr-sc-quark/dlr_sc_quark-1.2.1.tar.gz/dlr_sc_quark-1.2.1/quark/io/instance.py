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

""" module for Instance """

from abc import ABCMeta, abstractmethod

from . import hdf5


class NotSupportedError(NotImplementedError):
    """ additional error to indicate that the functionality is not supported (and is therefore not implemented) """

    def __init__(self, message="This functionality is not supported"):
        """ set a default message """
        super().__init__(message)


class Instance:
    """
    An instance is a container for all data defining a specific instance of a problem.
    This class serves as a base class with methods for saving in and loading from HDF5 files.
    It only needs to be inherited if IO functionality is needed.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """ initialize Instance object and check the consistency of the data """
        self.check_consistency()

    @abstractmethod
    def check_consistency(self):
        """
        check if the data is consistent,
        needs to be implemented in inheriting class
        """
        raise NotImplementedError()

    @abstractmethod
    def get_name(self):
        """
        get an expressive name representing the instance,
        needs to be implemented in inheriting class

        :return: an expressive name representing the instance
        """
        raise NotImplementedError()

    def get_constrained_objective(self, name=None):
        """
        get the constrained objective object based on this instance data,

        implement this method in your inheriting instance class to link to implemented constrained objective
        (usually you have implemented either ConstrainedObjective, ObjectiveTerms or Objective),
        do this by using the method `get_from_instance(self)`, which is inherited from the base ConstrainedObjective

        :param (str or None) name: the name of the object
        :return: the instantiated constrained objective
        """
        raise NotSupportedError()

    def get_objective_terms(self, *args, **kwargs):
        """
        get the objective terms object based on this instance data,

        this defaults back to the implementation of the constrained objective,

        overwrite this method in your inheriting instance class to link to the objective terms, if you have implemented
        this instead (usually you have implemented either ConstrainedObjective, ObjectiveTerms or Objective),
        do this by using the method `get_from_instance(self)`, which is inherited from the base ObjectiveTerms

        :return: the instantiated objective terms
        """
        constrained_objective = self.get_constrained_objective()
        return constrained_objective.get_objective_terms(*args, **kwargs)

    def get_objective(self, *args, **kwargs):
        """
        get the objective object based on this instance data,

        this defaults back to the implementation of the objective terms,

        overwrite this method in your inheriting instance class to link to the objective, if you have implemented
        this instead (usually you have implemented either ConstrainedObjective, ObjectiveTerms or Objective),
        do this by using the method `get_from_instance(self)`, which is inherited from the base Objective

        :return: the instantiated objective
        """
        objective_terms = self.get_objective_terms()
        return objective_terms.get_objective(*args, **kwargs)

    @abstractmethod
    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file,
        needs to be implemented in inheriting class, is called by 'save_hdf5'

        :param (h5py.Group) group: the group to store the data in
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file,
        needs to be implemented in inheriting class, is called by 'load_hdf5'

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        raise NotImplementedError()

    @staticmethod
    def get_identifying_attributes():
        """
        get the attributes that identify an object of the class,
        eventually needs to be overwritten in inheriting class
        """
        return []

    def save_hdf5(self, filename, prefix_group_name=None, full_group_name=None, mode='a'):
        """ save instance in an HDF5 file """
        hdf5.save(self, filename, prefix_group_name, full_group_name, mode)

    @classmethod
    def load_hdf5(cls, filename, prefix_group_name=None, full_group_name=None, **identifiers):
        """ load instance from an HDF5 file """
        return hdf5.load(cls, filename, prefix_group_name, full_group_name, **identifiers)

    @classmethod
    def exists_hdf5(cls, filename, prefix_group_name=None, full_group_name=None, **identifiers):
        """ check if an instance already exists in an HDF5 file """
        return hdf5.exists(cls, filename, prefix_group_name, full_group_name, **identifiers)
