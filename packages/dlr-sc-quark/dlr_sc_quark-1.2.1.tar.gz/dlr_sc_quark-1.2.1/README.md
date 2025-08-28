# quark - QUantum Application Reformulation Kernel

[![pipeline status](https://gitlab.com/quantum-computing-software/quark//badges/development/pipeline.svg)](https://gitlab.com/quantum-computing-software/quark/-/commits/development)

This is a software package to support the mapping of combinatorial optimization problems to quantum computing interfaces via QUBO and Ising problems.

## Documentation

The full documentation can be found [here](https://quantum-computing-software.gitlab.io/quark/).

## Description of the Basic Ideas

The combinatorial optimization problem is rewritten as a single (quadratic unconstrained binary) objective function.
The usual way to build it up is to use the following structure:
In the **`Instance`** we describe the problem defining parameters.
From the instance, we construct the **`ObjectiveTerms`**,
containing the different contributions to the objective function,
in particular the ones derived from problem constraints.
The objective terms can be implemented directly or derived from a **`ConstrainedObjective`**,
which contains the objective function and multiple constraints, implemented as **`ConstraintBinary`**.
The objective terms can now be used to create the **`Objective`**
by summing up the single terms weighted with a certain so-called penalty weight.

All objective objects contain **`Polynomials`** representing the functions.
There are special polynomials, **`PolyBinary`** and **`PolyIsing`**,
which take advantage of the restriction to either binary (0 or 1) or spin (-1 or 1) variables.

The **`ScipModel`** is an interface to the classical MILP solver [SCIP](https://scip.zib.de/),
which can solve a **`ConstrainedObjective`** or a (small enough) **`Objective`** for comparison.
In **`Solution`**, we store not only the optimal variable assignment but also further information,
like runtime etc., which are obtained during the solving process.

Furthermore, we have the **`HardwareAdjacency`** and the **`Embedding`**,
which are useful when dealing with actual hardware.

All mentioned objects also provide methods to store and load their information in and from hdf5 files.

## License

This project is [Apache-2.0](https://gitlab.com/quantum-computing-software/quark/-/blob/development/LICENSE) licensed.

Copyright © 2025 German Aerospace Center (DLR) - Institute of Software Technology (SC). 

Please find the individual contributors [here](https://gitlab.com/quantum-computing-software/quark/-/blob/development/CONTRIBUTORS) 
and information for citing this package [here](https://gitlab.com/quantum-computing-software/quark/-/blob/development/CITATION.cff).
