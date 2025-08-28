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

""" module for helper functions for IO with txt files """

import os


ERROR_ANY = "The file does not contain any object of type '{}'"
ERROR_FEW = "The file does not contain so much objects of type '{}'"


def save(obj, filename, mode="w"):
    """
    save object in txt file (by default only one object per file)

    :param obj: the object to be saved
    :param (str) filename: the name of txt file
    :param (str) mode: append to file ('a') or overwrite file ('w')
    """
    with open(filename, mode=mode, encoding="utf-8") as txt_file:
        if os.stat(filename).st_size > 0:
            txt_file.write("\n")
        # file should start with class name
        txt_file.write(type(obj).__name__ + "\n")
        # get the corresponding function for writing and call it
        obj.write_txt(txt_file)
        txt_file.write("\n")


def load(cls, filename, index=0):
    """
    load object of the given class from txt file

    :param cls: the type of the object to be loaded
    :param (str) filename: the name of txt file
    :param (int) index: if several objects of the same type are stored,
                        take the one with appears at index, by default the first
    """
    with open(filename, "r", encoding="utf-8") as txt_file:
        loaded_lines = txt_file.readlines()

    # search for correct place in the lines
    obj_lines = _get_lines(cls.__name__, loaded_lines, index)

    # get the corresponding read method and call it
    loaded_data = cls.read_txt(obj_lines)
    loaded_object = cls(**loaded_data)
    return loaded_object

def _get_lines(cls_name, lines, index=0):
    # remove artifacts
    lines = [line.replace("\n", "") for line in lines]

    start = -1
    end = None
    counter = -1
    for line_number, line in enumerate(lines):
        if line == cls_name:
            counter += 1
            if counter == index:
                # skip line with object name
                start = line_number + 1
        elif counter == index and line == "":
            end = line_number
            break

    if counter < 0:
        raise ValueError(ERROR_ANY.format(cls_name))
    if start < 0:
        raise ValueError(ERROR_FEW.format(cls_name))

    return lines[start:end]

def exists(cls, filename):
    """
    check if an object of the given class already exists in the txt file

    :param cls: the type of object to be checked
    :param (str) filename: the name of txt file
    :return: True if there is already an object of the given type in the file
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()

        try:
            _get_lines(cls.__name__, lines)
            return True
        except ValueError:
            pass
    return False
