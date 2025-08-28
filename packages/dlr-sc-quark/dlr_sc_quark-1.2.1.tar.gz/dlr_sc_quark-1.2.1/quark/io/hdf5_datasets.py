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

""" module for helper functions for IO of datasets with HDF5 files """

import itertools
from numbers import Real
import warnings
import h5py
import numpy as np


KEYS = "keys"
VALS = "values"

ERROR_SCALAR    = "Given dataset is just a scalar, create attribute instead"
ERROR_TYPE      = "Storing of dataset with type '{}' is not supported"
ERROR_NON       = "Storing of dataset of non-homogeneous type is not supported"
ERROR_LIST      = "Storing of dataset with type list over '{}' is not supported"
ERROR_KEYS      = "Dictionary keys are not of homogeneous type"
ERROR_ITEMS     = "Key items are not of homogeneous type"
ERROR_NOT_FOUND = "Did not find dataset '{}' in group '{}' in HDF5 file '{}'"
ERROR_MISMATCH  = "Mismatched dictionary dataset in group '{}' with {} keys but {} values"


def write_dataset(group, name, obj=None, dataset=None):
    """
    write the dataset in the open group of an HDF5 file,
    either the dataset is taken from the provided object with the attribute name or needs to be given explicitly

    :param (h5py.Group) group: the group in the HDF5 file in which the dataset is stored
    :param (str) name: the name under which the dataset is stored
    :param obj: the object with an attribute called as name, whose value is taken as the dataset to be stored
    :param dataset: the explicit dataset which shall be stored if no object is given
    """
    # if the object is given it should have an attribute which is called name
    if obj and hasattr(obj, name):
        dataset = getattr(obj, name)

    if name in group:
        del group[name]

    if not isinstance(dataset, dict):
        _write_flat_dataset(group, name, dataset)
    else:
        _write_dict_dataset(group, name, dataset)


def write_datasets(group, obj=None, *names, **names_to_datasets):  # pylint: disable=keyword-arg-before-vararg
    """
    write several datasets in the open group of an HDF5 file,
    either provide the names of the attributes of the given object yielding the datasets or
    give the explicit dictionary of names to datasets as keyword arguments

    :param (h5py.Group) group: the HDF5 group to store the datasets in
    :param obj: the object whose attributes to take as datasets to be stored
    :param (str) names: attributes of the object that shall be stored (not to be used if no object is given)
    :param names_to_datasets: keyword arguments of explicit datasets with names,
                              if no object is given or additional values shall be stored
    """
    for name in names:
        write_dataset(group, name, obj)
    for name, dataset in names_to_datasets.items():
        write_dataset(group, name, dataset=dataset)


def _write_flat_dataset(group, name, dataset):
    """
    write lists or sets as datasets to the open group of an HDF5 file

    :param (h5py.Group) group: the group in the HDF5 file where the dataset is stored
    :param (str) name: the name under which the dataset is stored
    :param dataset: the dict which will be stored
    """
    # if it is a scalar, it should be stored as an attribute
    if np.isscalar(dataset):
        raise ValueError(ERROR_SCALAR)
    # if there is None stored or the length of the dataset is 0
    if dataset is None:
        np_dataset = np.nan
    else:
        # if is already transformed into a numpy array assume that it can be stored directly
        if isinstance(dataset, np.ndarray):
            np_dataset = dataset
        else:
            # we do not differ between sets/ tuples/ lists/ other iterables when storing
            if np.iterable(dataset):
                dataset = list(dataset)

            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                # in future numpy will not allow ragged nested arrays anymore
                try:
                    # but e.g. strings of different length are fine
                    np_dataset = np.array(dataset)
                except (np.exceptions.VisibleDeprecationWarning, ValueError):
                    np_dataset = np.array(dataset, dtype=object)

        if np_dataset.dtype.kind == "U":  # unicode should be converted to ascii for h5py
            np_dataset = np_dataset.astype("S")
        if np_dataset.dtype == object:
            np_dataset = _handle_object_dtype(dataset, np_dataset)

    group.create_dataset(name, data=np_dataset)


def _handle_object_dtype(dataset, np_dataset):
    if not isinstance(dataset, list):
        raise ValueError(ERROR_TYPE.format(type(dataset)))

    if all(np.iterable(x) for x in dataset):
        vlen_array = True
        elements_type = _get_homogeneous_type(itertools.chain.from_iterable(dataset))
    else:
        vlen_array = False
        elements_type = _get_homogeneous_type(dataset)

    if not elements_type:
        raise NotImplementedError(ERROR_NON)
    if elements_type not in np.ScalarType or elements_type == str:
        raise NotImplementedError(ERROR_LIST.format(elements_type))

    if vlen_array:
        vlen_type = h5py.special_dtype(vlen=np.dtype(elements_type))
        np_dataset = np.array([np.array(x, dtype=elements_type) for x in dataset], dtype=vlen_type)
    return np_dataset

def _get_homogeneous_type(sequence):
    type_set = set(type(element) for element in sequence)
    if len(type_set) == 1:
        return type_set.pop()

    if not type_set:
        return None

    # numbers can have different types
    if all(issubclass(t, Real) for t in type_set):
        return float
    return None


def _write_dict_dataset(group, name, dataset):
    """
    write dictionary as dataset to the open group of an HDF5 file
    by splitting it up into 'flat' parts

    :param (h5py.Group) group: the group in the HDF5 file where the dataset is stored
    :param (str) name: the name under which the dataset is stored
    :param dataset: the dict which will be stored
    """
    keys = dataset.keys()
    vals = dataset.values()
    # check if dict homogeneous
    # ignore float keys since not recommendable
    key_type = _get_homogeneous_type(keys)
    if not key_type and len(keys) > 0:
        raise TypeError(ERROR_KEYS)

    if key_type is tuple:
        items_in_tuples = [item for key in keys for item in key]
        item_type = _get_homogeneous_type(items_in_tuples)
        if len(items_in_tuples) > 0 and not item_type:
            raise TypeError(ERROR_ITEMS)

    # create group and write datasets
    dict_group = group.create_group(name)
    if keys:
        _write_flat_dataset(dict_group, KEYS, keys)
        _write_flat_dataset(dict_group, VALS, vals)


def read_dataset(group, name, check_existence=True):
    """
    read dataset from the open group of an HDF5 file

    :param (h5py.Group) group: the group in the HDF5 file where the dataset is stored
    :param (str) name: the name under which the dataset is stored
    :param (bool) check_existence: if True then an error will be thrown if the dataset is not found,
                                   if False None will be returned without error
    :return: the dataset
    """

    if name not in group:
        if check_existence:
            raise ValueError(ERROR_NOT_FOUND.format(name, group.name, group.file.filename))
        return None
    if isinstance(group[name], h5py.Group):
        return _read_dict_dataset(group[name])
    return _read_flat_dataset(group, name)


def _read_flat_dataset(group, name):
    """
    read a flat dataset from the open group of an HDF5 file

    :param (h5py.Group) group: the HDF5 group to read from
    :param (str) name: the name under which the dataset is stored
    :return: the dataset
    """
    dataset = group[name][()]
    if isinstance(dataset, float) and np.isnan(dataset):
        return None
    if dataset.dtype.kind == 'S':   # converts byte/string to Unicode
        return dataset.astype('U')
    return dataset


def _read_dict_dataset(group):
    """
    read a dictionary dataset from the open group of an HDF5 file

    :param (h5py.Group) group: the HDF5 group to read from
    """
    # keys and values
    ds_keys = None
    ds_vals = None

    if KEYS in group:
        ds_keys = _read_flat_dataset(group, KEYS)
    if VALS in group:
        ds_vals = _read_flat_dataset(group, VALS)
        ds_vals = [str(val) if isinstance(val, np.str_) else val for val in ds_vals]  # to convert np.str_ from numpy2

    if ds_keys is None or ds_vals is None:
        ds_keys = []
        ds_vals = []
    if len(ds_keys) != len(ds_vals):
        raise ValueError(ERROR_MISMATCH.format(group, len(ds_keys), len(ds_vals)))

    if len(ds_keys) == 0:
        return {}

    if isinstance(ds_keys[0], np.ndarray):
        ds_keys = [tuple(key) for key in ds_keys]

    return dict(zip(ds_keys, ds_vals))


def read_datasets(group, *names, check_existence=True):
    """
    read several datasets from the open group of an HDF5 file

    :param (h5py.Group) group: the group in the HDF5 file where the datasets are stored
    :param (str) names: the names under which the datasets are stored
    :param (bool) check_existence: if True then an error will be thrown if a dataset is not found,
                                   if False None will be returned without error
    :return: dictionary with the datasets keyed by names
    """
    return {name: read_dataset(group, name, check_existence) for name in names}
