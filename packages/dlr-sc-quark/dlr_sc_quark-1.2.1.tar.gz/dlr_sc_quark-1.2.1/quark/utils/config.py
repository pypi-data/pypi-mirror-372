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

""" module for a base class for configurations """

import ast
import configparser
import os
from abc import ABCMeta, abstractmethod


SECTION = "section"
OPTION  = "option"
TYPE    = "type"
DEFAULT = "default"
HELP    = "help"

ERROR_ATTRIBUTE = "There is no attribute '{}'"
ERROR_FILE      = "Configuration file '{}' does not exists"
ERROR_MISSING   = "Missing {} '{}' in configuration file '{}'"
ERROR_FORMAT    = "Configuration value is not well formatted"
ERROR_TYPE      = "The value is of type '{}' and not the intended type '{}'"

FEASIBLE_SCALAR_TYPES = (int, float, str, bool)
FEASIBLE_TYPES = (int, float, str, bool, dict, list)

ERROR_SCALAR = "Values must be of one of the types int, float, str or bool, not '{}'"
ERROR_NESTED = "Values must be of one of the types int, float, str, bool, list or dict, not '{}'"
ERROR_KEYS   = "Keys must be of type str not '{}'"
ERROR_LEVEL  = "Level of nested dictionaries exceeds specified maximal depth {}"


class Config(dict):
    """
    A configuration is a container to store several values.
    This serves as a base class for the implementation of different configurations.
    """
    __metaclass__ = ABCMeta

    def __init__(self, set_defaults=False, **kwargs):
        """
         initialize configuration object

        :param set_defaults: if True, sets default values to the configuration options, otherwise None is set
        """
        super().__init__(**kwargs)
        if set_defaults:
            self.set_defaults(False)

    def __getattr__(self, option):
        """
        get the value of the option of the configuration,
        where attributes and items of the internal dictionary are handled equivalently,
        thus we have `cfg.__getattr__('option') == cfg.option == cfg['option']`
        """
        return self[option]

    def __setattr__(self, option, value):
        """ change the value of the option of the configuration """
        self[option] = value

    def __delattr__(self, option):
        """
        delete the option from the configuration, resets value to None,
        raises an exception if the option does not exist
        """
        del self[option]

    def __getitem__(self, option):
        """ get the value of a specific option of the configuration """
        if option in self:
            return super().__getitem__(option)
        raise AttributeError(ERROR_ATTRIBUTE.format(option))

    def __delitem__(self, option):
        """ reset the option to None, raises an exception if the option does not exist """
        if option in self:
            self[option] = None
        else:
            raise AttributeError(ERROR_ATTRIBUTE.format(option))

    @classmethod
    def get_name(cls):
        """ get the name of the configuration """
        return cls.__name__

    @staticmethod
    @abstractmethod
    def get_options_dict():
        """
        get the dictionary of options and additional information,
        needs to be implemented in inheriting class
        """
        raise NotImplementedError()

    def update(self, **kwargs):
        """ update the given options, raises an exception if some option does not exist """
        for option in kwargs:
            if option not in self.get_options_dict().keys():
                raise AttributeError(ERROR_ATTRIBUTE.format(option))
        super().update(kwargs)

    def set_defaults(self, override=True):
        """
        set the values to the default ones,
        defaults need to be specified by an implementation of the `get_options_dict` method
        """
        kwargs = self.get_defaults()
        if not override:
            for key in list(kwargs):
                if self[key] is not None:
                    kwargs.pop(key)
        else:
            for key in list(kwargs):
                if kwargs[key] is None:
                    kwargs.pop(key)
        self.update(**kwargs)

    def to_string(self, max_depth=4, omit_keys=None):
        """
        get a unique string from the configuration,
        can only be applied, if the configuration contains the suitable entries

        :param (int) max_depth: the maximum number of the recursive resolution of dicts in dicts,
                                gives a warning and incomplete result if the configuration exceeds it
        :param (list) omit_keys: list of strings providing the keys that should be omitted during the string conversion,
                                 the corresponding key-value pairs will be omitted on all depth levels in case we have
                                 nested dictionaries
        :returns: unique string from configuration file if possible, None otherwise
        """
        return dict_to_string(self, max_depth=max_depth, omit_keys=omit_keys)

    def save(self, filename):
        """
        save the configuration in a file

        :param (str) filename: path to the file where to store the configuration file in
        """
        with open(filename, "w", encoding="utf-8") as config_file:
            cfg_parser = configparser.ConfigParser()
            section = self.get_name()
            options = self.get_options_dict().keys()
            cfg_parser.add_section(section)
            for option in options:
                cfg_parser.set(section=section, option=str(option), value=str(self[option]))
            cfg_parser.write(config_file)

    @classmethod
    def load(cls, filename):
        """
        load configuration from a file

        :param (str) filename: path to configuration file
        :returns: the loaded configuration
        """
        if not os.path.exists(filename):
            raise ValueError(ERROR_FILE.format(filename))
        cfg_name = cls.get_name()
        options = cls.get_options_dict()
        config_parser = configparser.ConfigParser()
        config_parser.read(filename)

        if not config_parser.has_section(cfg_name):
            raise ValueError(ERROR_MISSING.format(SECTION, cfg_name, filename))
        init_kwargs = {}
        for option in options:
            if not config_parser.has_option(cfg_name, option):
                raise ValueError(ERROR_MISSING.format(OPTION, option, filename))
            intended_type = options[option].get(TYPE)
            init_kwargs[option] = cls._cast_type(config_value=config_parser.get(cfg_name, option),
                                                 intended_type=intended_type)
        return cls(**init_kwargs)

    @classmethod
    def _cast_type(cls, config_value, intended_type):
        """
        cast the loaded elements of the configuration to the correct type

        :return: cast value of given config_value or None if there is a missmatch between intended type and actual type
        """
        try:
            config_value = ast.literal_eval(config_value)
        except (ValueError, SyntaxError):
            assert isinstance(config_value, str), ERROR_FORMAT
        if isinstance(config_value, intended_type):
            return config_value
        if config_value is None:
            return None
        if intended_type is str:
            return str(config_value)
        raise TypeError(ERROR_TYPE.format(type(config_value), intended_type))

    @classmethod
    def get_defaults(cls):
        """ get default values specified in `get_options_dict` """
        return {name: d.get(DEFAULT, None) for name, d in cls.get_options_dict().items()}

    @classmethod
    def get_help(cls):
        """ get description/help that is specified in 'get_options_dict' """
        cfg_name = cls.get_name()
        options = cls.get_options_dict()
        n = max(len(name) for name in options.keys()) + 1
        lines = ""
        for name in options:
            help_str = options[name].get(HELP, "")
            lines += "\t" + name + " " * (n - len(name)) + f"= <{help_str}>\n"
        return f"configuration file with the following entries:\n\t[{cfg_name}]\n{lines}"


def dict_to_string(dictionary, max_depth, omit_keys=None, _depth_counter=0):
    """
    get a unique string from an ordered dictionary if possible,
    the keys of the dictionary can be dictionaries themselves,
    in this case they are recursively resolved up until a maximal depth

    :param (dict) dictionary: dictionary to be formatted
    :param (int) max_depth: maximum level of nested dicts that should be resolved, if exceeded, return None
    :param (list or None) omit_keys: list of keys that should be omitted during the string conversion,
                                     the corresponding key-value pairs will be omitted on all depth levels in case we
                                     have nested dictionaries
    :param (int) _depth_counter: counting the levels of nested dictionaries that have been resolved
    :return: unique string if formatting is possible
    """
    dict_string = ""
    for key, value in dictionary.items():
        if omit_keys and key in omit_keys:
            continue
        if not isinstance(key, str):
            raise ValueError(ERROR_KEYS.format(type(key).__name__))
        if not isinstance(value, FEASIBLE_TYPES):
            raise ValueError(ERROR_NESTED.format(type(value).__name__))
        if isinstance(value, dict):
            if _depth_counter >= max_depth:
                raise ValueError(ERROR_LEVEL.format(max_depth))
            substring = dict_to_string(value, max_depth, omit_keys=omit_keys, _depth_counter=_depth_counter + 1)
            dict_string += f"_{_to_string(key)}{substring}"
        elif isinstance(value, list):
            substring = "".join(f"_{_to_string(element)}" for element in value)
            dict_string += f"_{_to_string(key)}{substring}"
        elif isinstance(value, str):
            dict_string += f"_{_to_string(key)}_{_to_string(value)}"
        else:
            dict_string += f"_{_to_string(key)}{_to_string(value)}"
    return dict_string

def _to_string(value):
    """
     get a unique string to a valid input value

    :param value: needs to be int, float, string or bool
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f'{value:e}'
    raise ValueError(ERROR_SCALAR.format(type(value).__name__))
