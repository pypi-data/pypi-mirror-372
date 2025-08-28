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

""" module for ScipModel """

from warnings import warn
from ast import literal_eval
from numbers import Real
from pyscipopt.scip import Model  # pylint: disable=no-name-in-module

from .solution import Solution


VAR_PREFIX                 = "var_"
OBJECTIVE_VAR              = "obj"
FILENAME_SUFFIX            = ".cip"
QUADRATIC_OBJECTIVE        = "quadratic_objective"
FROM_CONSTRAINED_OBJECTIVE = "from_constrained_objective"
FROM_OBJECTIVE             = "from_objective"
LIMITS_TIME                = "limits/time"
BINARY                     = "B"
CONTINUOUS                 = "C"
SAVE_ISING                 = "# from_inverted_ising: "

INFEASIBLE = "infeasible"
OPTIMAL    = "optimal"
UNBOUNDED  = "unbounded"
TIMEOUT    = "timelimit"
IS_SOLVED = [INFEASIBLE, OPTIMAL, UNBOUNDED]
HAS_SOLUTION = [OPTIMAL, TIMEOUT]

ERROR_VALUE  = "Cannot get value for variable '{}'"
WARNING_LOAD = "Cannot retrieve value for 'from_inverted_ising', will use 'None'"


class ScipModel(Model):
    """
    A Scip model provides an interface to the classical MIP solver SCIP.
    It automatically builds up the SCIP model from the ConstrainedObjective or the Objective,
    which can be solved with SCIP.
    """

    def __init__(self, name="", from_inverted_ising=None):
        """
        initialize ScipModel object

        :param (str) name: the name of the model
        :param (bool or None) from_inverted_ising: if None, originates from a binary problem,
                                                   if False, originates from a non-inverted (default) Ising model,
                                                   if True, originates from an inverted Ising model
        """
        self.from_inverted_ising = from_inverted_ising
        self.data = {}
        super().__init__(name)
        self.hideOutput()

    @property
    def name(self):
        """ the name of the model """
        return self.getProbName()

    @classmethod
    def get_from_objective(cls, objective):
        """
        get the corresponding ScipModel to an at most quadratic Objective

        :param (Objective) objective: the Objective with the quadratic Ising or binary polynomial
        :return: the corresponding ScipModel
        """
        name = objective.name or FROM_OBJECTIVE
        model = cls(name) if objective.is_binary() else cls(name, objective.is_ising(inverted=True))
        model._init_from_objective(objective)
        return model

    def _init_from_objective(self, objective):
        """ initialize the ScipModel with the data from the Objective """
        self._init_from_binary_poly(objective.to_binary().polynomial)

    def _init_from_binary_poly(self, binary_poly):
        """ initialize the ScipModel with the data from the binary polynomial corresponding to the Objective """
        # initialize binary variables (do not need to be flat)
        variables = {var: self.addVar(VAR_PREFIX + f"{var}", vtype=BINARY) for var in binary_poly.variables}
        # initialize a continuous objective variable serving as a placeholder
        objective = self.addVar(OBJECTIVE_VAR, vtype=CONTINUOUS, lb=-self.infinity())
        # get quadratic scip expression
        objective_scip_expression = binary_poly.evaluate(variables)
        # as scip cannot have quadratic objective functions directly, we set it equal to another continuous variable
        self.addCons(objective_scip_expression == objective, name=QUADRATIC_OBJECTIVE)
        # which we can then optimize as it is linear
        self.setObjective(objective)
        self.setMinimize()
        # container for some data, we store the mapping of the variables
        self.data = variables

    @classmethod
    def get_from_constrained_objective(cls, constrained_objective, name=FROM_CONSTRAINED_OBJECTIVE):
        """
        get the corresponding ScipModel to a ConstrainedObjective with an at most quadratic objective function

        :param (ConstrainedObjective) constrained_objective: the ConstrainedObjective with the quadratic Ising or
                                                             binary objective polynomial
        :param (str) name: the name of the resulting model, by default 'from_constrained_objective'
        :return: the corresponding ScipModel
        """
        model = cls(name)
        model._init_from_constrained_objective(constrained_objective)
        return model

    def _init_from_constrained_objective(self, constrained_objective):
        """ initialize the ScipModel with the data from the ConstrainedObjective """
        # initialize binary variables (do not need to be flat)
        variables = {var: self.addVar(VAR_PREFIX + f"{var}", vtype=BINARY)
                     for var in constrained_objective.get_all_variables()}

        objective_scip_expression = constrained_objective.objective_poly.evaluate(variables)
        if constrained_objective.objective_poly.is_linear():
            # if the objective function is linear we can directly use it in SCIP
            self.setObjective(objective_scip_expression)
        else:
            # otherwise we need to use a placeholder variable as the objective function and add a constraint
            objective = self.addVar(OBJECTIVE_VAR, vtype=CONTINUOUS, lb=-self.infinity())
            self.addCons(objective_scip_expression == objective, name=QUADRATIC_OBJECTIVE)
            self.setObjective(objective)

        # also add the constraints
        for name, constraint in constrained_objective.items():
            # since SCIP does not allow constants in the constraint function, we need to extract it
            shifted_constraint = constraint - constraint.polynomial.offset
            shifted_constraint.polynomial = shifted_constraint.polynomial.remove_zero_coefficients()
            poly_scip_expression = shifted_constraint.polynomial.evaluate(variables)
            # the brackets are necessary for SCIP to have both constraints (left and right side) added at the same time
            self.addCons(float(shifted_constraint.lower_bound) <=
                         (poly_scip_expression <= float(shifted_constraint.upper_bound)), name=name)

        self.setMinimize()
        # store variable mapping in data container
        self.data = variables

    def solve(self, timeout=3600.0, verbose=False, **param_kwargs):
        """
        solve the model using SCIP with the given parameters

        :param (float or int) timeout: the time in seconds until which SCIP tries to find the solution
        :param (bool) verbose: hide or print the output of SCIP
        :param param_kwargs: further parameters which can be given to SCIP,
                             see https://www.scipopt.org/doc-7.0.1/html/PARAMETERS.php
        :return: the optimal solution or best solution at timeout
        """
        self.set_solving_parameters(timeout, verbose, **param_kwargs)
        self.optimize()
        self.hideOutput()
        return self.get_solution()

    def set_solving_parameters(self, timeout=3600.0, verbose=False, **param_kwargs):
        """
        set the solving parameters to the model

        :param (float or int) timeout: the time in seconds until which SCIP tries to find the solution
        :param (bool) verbose: hide or print the output of SCIP
        :param param_kwargs: further parameters which can be given to SCIP,
                             see https://www.scipopt.org/doc-7.0.1/html/PARAMETERS.php
        """
        self.hideOutput(not verbose)
        self.setParam(LIMITS_TIME, timeout)
        for param, value in param_kwargs.items():
            self.setParam(param, value)

    def get_solution(self):
        """
        get the solution from the model, can only be applied once the model is solved,
        the type of the solution corresponds to the type of the original objective
        """
        objective_value, var_assignment = self.get_values()
        solution = Solution(var_assignments=var_assignment,
                            objective_value=objective_value,
                            solving_status=self.getStatus(),
                            solving_success=self.getStatus() in IS_SOLVED,
                            solving_time=self.getSolvingTime(),
                            total_time=self.getTotalTime(),
                            dual_gap=self.getGap(),
                            dual_bound=self.getDualbound(),
                            name=self.name)
        if self.from_inverted_ising is not None:
            solution = solution.to_ising(invert=self.from_inverted_ising)
        return solution

    def get_values(self):
        """ get the objective value and the values for each variable """
        if self.getStatus() in HAS_SOLUTION:
            objective_value = self.getObjVal()
            var_assignment = {var: self.get_value(var) for var in self.data}
            return objective_value, var_assignment
        return None, {}

    def get_value(self, variable, int_precision=1e-9):
        """
        get the assignment of the variable in the solution

        :param (tuple or Integral or str) variable: the original variable
        :param (Real) int_precision: precision value for checking if the value is actually an integer
        :return: the value of the variable in the solution
        """
        try:
            scip_var = self.data[variable]
            value = scip_var if isinstance(scip_var, Real) else self.getVal(scip_var)
        except KeyError as e:
            raise ValueError(ERROR_VALUE.format(variable)) from e
        value = round(value) if abs(value - round(value)) < int_precision else value
        return value

    # io in text files

    def save_cip(self, filename=None):
        """
        save model into a cip file

        :param (str or None) filename: the filename, by default the name of the model,
                                       if it does not have `*.cip` ending, it will be added
        """
        filename = filename or self.name
        filename = filename if filename.endswith(FILENAME_SUFFIX) else filename + FILENAME_SUFFIX

        self.writeProblem(filename)
        with open(filename, mode="a", encoding="utf-8") as txt_file:
            # add the information of the attribute in the last line
            txt_file.writelines(SAVE_ISING + f"{self.from_inverted_ising}")


    @classmethod
    def load_cip(cls, filename):
        """
        load model from a cip file

        :param (str) filename: the filename, if it does not have `*.cip` ending, it will be added
        :return the loaded model
        """
        filename = filename if filename.endswith(FILENAME_SUFFIX) else filename + FILENAME_SUFFIX
        scip_model = cls()

        with open(filename, mode="r", encoding="utf-8") as txt_file:
            last_line = txt_file.readlines()[-1]
            if last_line.startswith(SAVE_ISING):
                # get the value of the attribute in the added line
                from_inverted_ising = literal_eval(last_line[len(SAVE_ISING):])
            else:
                warn(WARNING_LOAD)
                from_inverted_ising = None

        scip_model.readProblem(filename)
        scip_model.from_inverted_ising = from_inverted_ising

        # parse the variables to store them for later usage
        scip_variables = scip_model.getVars()
        scip_variables = [var for var in scip_variables if var.name != OBJECTIVE_VAR]
        original_variables = {literal_eval(var.name.replace(VAR_PREFIX, "")): var for var in scip_variables}
        scip_model.data = original_variables
        return scip_model
