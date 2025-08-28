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

"""
module for decorators for adding IO functions to classes

thanks to https://medium.com/@mgarod/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
"""

from functools import wraps

from . import hdf5


def self_method(cls, method_name=None):
    """
    get a decorator which adds the decorated function to the given class as a self method,
    for an object of the given class (obj = cls(...)) instead of calling the function with 'decorated_func(obj, ...)',
    the following method is available AT RUNTIME 'obj.decorated_func(...)' (if IO is loaded),
    by adding a 'method_name' the functionality is preserved, but the call changes to 'obj.method_name(...)',
    can be used to 'register' the class to provide a certain functionality

    :param cls: the class to add the method to
    :param (str or None) method_name: the name of the added method, by default name of the decorated function is used
    :return: the decorator
    """
    def decorator(decorated_func):
        """ the actual decorator """

        @wraps(decorated_func)  # preserve name and docstring
        def wrapper(self, *args, **kwargs):
            """ wrapper accepts self and inserts it as the first argument of the decorated function """
            return decorated_func(self, *args, **kwargs)

        # if no explicit name is given use the one of the decorated function
        name = method_name or decorated_func.__name__
        # add the function as a method to the class
        setattr(cls, name, wrapper)
        # with returning the decorated function, it can still be used normally
        return decorated_func

    return decorator


def class_method(cls, method_name=None):
    """
    get a decorator which adds the decorated function to the given class as a class method,
    for the given class instead of calling the function with 'decorated_func(cls, ...)',
    the following method is available AT RUNTIME 'cls.decorated_func(...)' (if IO is loaded),
    by adding a 'method_name' the functionality is preserved, but the call changes to 'cls.method_name(...)',
    can be used to 'register' the class to provide a certain functionality

    :param cls: the class to add the method to
    :param (str or None) method_name: the name of the added method, by default name of the decorated function is used
    :return: the decorator
    """
    def decorator(decorated_func):
        """ the actual decorator """

        @classmethod
        @wraps(decorated_func)  # preserve name and docstring
        def wrapper(*args, **kwargs):
            """ wrapper does not need cls or self """
            return decorated_func(*args, **kwargs)

        # if no explicit name is given use the one of the decorated function
        name = method_name or decorated_func.__name__
        # add the function as a method to the class
        setattr(cls, name, wrapper)
        # with returning the decorated function, it can still be used normally
        return decorated_func

    return decorator

def static_method(cls, method_name=None):
    """
    get a decorator which adds the decorated function to the given class as a static method,
    for the given class instead of calling the function with 'decorated_func(...)',
    the following method is available AT RUNTIME 'cls.decorated_func(...)' (if IO is loaded),
    by adding a 'method_name' the functionality is preserved, but the call changes to 'cls.method_name(...)',
    can be used to 'register' the class to provide a certain functionality

    :param cls: the class to add the method to
    :param (str or None) method_name: the name of the added method, by default name of the decorated function is used
    :return: the decorator
    """
    def decorator(decorated_func):
        """ the actual decorator """

        @staticmethod
        @wraps(decorated_func)
        def wrapper(*args, **kwargs):
            """ wrapper does not need cls or self """
            return decorated_func(*args, **kwargs)

        # if no explicit name is given use the one of the decorated function
        name = method_name or decorated_func.__name__
        # add the function as a method to the class
        setattr(cls, name, wrapper)
        # with returning the decorated function, it can still be used normally
        return decorated_func

    return decorator

def save_load_exists(the_class, module=hdf5, suffix="hdf5"):
    """
    add all IO methods to the class definition,
    those call e.g. hdf5.save, hdf5.load and hdf5.exists, respectively

    :param the_class: the class to which the methods shall be added
    :param module: the module from which the methods are taken
    :param suffix: the suffix to add to the method name
    """
    self_method(the_class, f"save_{suffix}")(module.save)
    class_method(the_class, f"load_{suffix}")(module.load)
    class_method(the_class, f"exists_{suffix}")(module.exists)
