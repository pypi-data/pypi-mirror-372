# Copyright 2025 DLR-SC
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

""" module for namedtuple variables """

from collections import namedtuple

from .poly_binary import PolyBinary
from .poly_ising import PolyIsing


def var_binary_namedtuple(name, *field_names):
    """
    get a new subclass of tuple representing binary variables with the same tuple structure

    with `x = var_binary_namedtuple("x", "node", "index")` you can get the constructor and then
    use it for a specific variable with `x("a", 1)`, which gives you the namedtuple `Bin(var='x', node='a', index=1)`

    note that the addition, multiplication, etc. of these namedtuple variables is rather to get familiar with our
    polynomials and variable tuples, it is not optimized for performance,
    thus we do not recommend the usage on large scale
    """

    class Bin(namedtuple("Bin", ("var",) + field_names)):
        """ workaround to define the namedtuple in a certain way """

        def __new__(cls, *args, **kwargs):
            # the name is inserted for this variable by default
            return super(Bin, cls).__new__(cls, name, *args, **kwargs)

        def __add__(self, other):

            if isinstance(other, Bin):
                other = PolyBinary({(other,) : 1})
            return PolyBinary({(self,) : 1}) + other

        def __radd__(self, other):
            return PolyBinary({(self,) : 1}) + other

        def __sub__(self, other):
            if isinstance(other, Bin):
                other = PolyBinary({(other,) : 1})
            return PolyBinary({(self,) : 1}) - other

        def __rsub__(self, other):
            return other - PolyBinary({(self,) : 1})

        def __mul__(self, other):
            if isinstance(other, Bin):
                other = PolyBinary({(other,) : 1})
            return other * PolyBinary({(self,) : 1})

        def __rmul__(self, other):
            return other * PolyBinary({(self,) : 1})

        def __truediv__(self, other):
            return PolyBinary({(self,) : 1}) / other

        def __pow__(self, exponent):
            return PolyBinary({(self,) : 1}) ** exponent

    return Bin


def var_ising_namedtuple(name, *field_names):
    """
    get a new subclass of tuple representing Ising variables with the same tuple structure

    with `s = var_binary_namedtuple("s", "node", "index")` you can get the constructor and then
    use it for a specific variable with `s("a", 1)`, which gives you the namedtuple `Ising(var='s', node='a', index=1)`

    note that the addition, multiplication, etc. of these namedtuple variables is rather to get familiar with our
    polynomials and variable tuples, it is not optimized for performance,
    thus we do not recommend the usage on large scale
    """

    class Ising(namedtuple("Ising", ("var",) + field_names)):
        """ workaround to define the namedtuple in a certain way """

        def __new__(cls, *args, **kwargs):
            # the name is inserted for this variable by default
            return super(Ising, cls).__new__(cls, name, *args, **kwargs)

        def __add__(self, other):
            if isinstance(other, Ising):
                other = PolyIsing({(other,) : 1})
            return PolyIsing({(self,) : 1}) + other

        def __radd__(self, other):
            return PolyIsing({(self,) : 1}) + other

        def __sub__(self, other):
            if isinstance(other, Ising):
                other = PolyIsing({(other,) : 1})
            return PolyIsing({(self,) : 1}) - other

        def __rsub__(self, other):
            return other - PolyIsing({(self,) : 1})

        def __mul__(self, other):
            if isinstance(other, Ising):
                other = PolyIsing({(other,) : 1})
            return other * PolyIsing({(self,) : 1})

        def __rmul__(self, other):
            return other * PolyIsing({(self,) : 1})

        def __truediv__(self, other):
            return PolyIsing({(self,) : 1}) / other

        def __pow__(self, exponent):
            return PolyIsing({(self,) : 1}) ** exponent

    return Ising
