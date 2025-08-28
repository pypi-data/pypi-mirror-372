""" setup for project quark """

from setuptools import setup, find_packages


setup(name = 'quark',
      version = '1.2',
      url = 'https://gitlab.com/quantum-computing-software/quark/',
      author = 'DLR-SC',
      author_email = 'qc-software@dlr.de',
      python_requires = '>=3.11',
      description = 'This is a software package to support the mapping of combinatorial optimization problems to quantum computing interfaces via QUBO and Ising problems.',
      packages = find_packages(include=['quark', 'quark.io', 'quark.testing', 'quark.utils']),
      zip_safe = False)
