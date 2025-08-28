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

""" module for ExampleConfig """

from quark.utils import Config


class ExampleConfig(Config):
    """ example implementation of a configuration for testing """

    def __init__(self,
                 float_option=None,
                 int_option=None,
                 str_option=None,
                 list_option=None,
                 dict_option=None,
                 set_defaults=False):
        """
        initialize ExampleConfig object

        :param float_option: option with float
        :param int_option: option with int
        :param str_option: option with str
        :param list_option: option with list
        :param dict_option: option with dict
        :param set_defaults: if True, set options which are not given explicitly to the default values
        """
        super().__init__(set_defaults,
                         float_option=float_option,
                         int_option=int_option,
                         list_option=list_option,
                         str_option=str_option,
                         dict_option=dict_option)

    @staticmethod
    def get_options_dict():
        """ get the dictionary of all possible options and additional information such as their default values """
        return {"float_option" : {"type": float, "default": 20.0,           "help": 'Just a float for testing'},
                "int_option"   : {"type": int,   "default": 10,             "help": 'Just an int for testing'},
                "str_option"   : {"type": str,   "default": "some_string",  "help": 'Just a str for testing'},
                "list_option"  : {"type": list,  "default": None,           "help": 'Just a list for testing'},
                "dict_option"  : {"type": dict,  "default": {"default": 0}, "help": 'Just a dict for testing'}}
