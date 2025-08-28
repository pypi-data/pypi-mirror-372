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

""" module for testing scip_model """

import os
import pytest

from quark import Objective, Polynomial, PolyBinary, PolyIsing, ScipModel, ConstrainedObjective, ConstraintBinary
from quark.scip_model import QUADRATIC_OBJECTIVE, OPTIMAL


X, B, G, R = "x", "blue", "green", "red"

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "scip_model.cip"
FILENAME_FIX = TEST_DIR + "testdata/scip_model.cip"

POLY = Polynomial.read_from_string("- 2 x0 x4 - 3 x0 x5 + x0 x6 + 3 x0 x7 + 4 x1 x4 "
                                   "+ 3 x1 x6 + 4 x0 - 3 x1 - 4 x0 - 5 x2 - 4 x5 + 16")
EXP_VARIABLES = [(X, 1, B), (X, 1, G), (X, 1, R), (X, 2, B), (X, 2, G), (X, 2, R), (X, 3, B), (X, 3, G), (X, 3, R),
                 (X, 4, B), (X, 4, G), (X, 4, R), (X, 5, B), (X, 5, G), (X, 5, R)]

@pytest.fixture(name="scip_model")
def fixture_scip_model(objective):
    """ provide scip model for testing """
    yield ScipModel.get_from_objective(objective)

def test_get_from_objective(scip_model, solutions):
    """ test solution of scip model created from objective """
    constraint = scip_model.getConss()[0]
    assert list(scip_model.data.keys()) == EXP_VARIABLES
    assert constraint.name == QUADRATIC_OBJECTIVE
    assert constraint.isNonlinear()

    solution_solve = scip_model.solve()
    assert scip_model.getObjVal() == 0
    assert scip_model.getVal(scip_model.data[(X, 1, B)]) == 1
    assert scip_model.getVal(scip_model.data[(X, 2, B)]) == 0
    assert dict(solution_solve) in solutions
    assert solution_solve.objective_value == solutions[0].objective_value

def test_get_from_constrained_objective(constrained_objective, solutions):
    """ test solution of scip model created from objective """
    scip_model = ScipModel.get_from_constrained_objective(constrained_objective)
    constraints = scip_model.getConss()
    assert list(scip_model.data.keys()) == EXP_VARIABLES
    assert len(constraints) == 6
    assert constraints[0].name == QUADRATIC_OBJECTIVE
    assert constraints[0].isNonlinear()

    for node in range(1, 6):
        assert constraints[node].name == f"one_color_per_node_{node}"
        assert constraints[node].isLinear()

    solution_solve = scip_model.solve()
    assert scip_model.getObjVal() == 0
    assert dict(solution_solve) in solutions
    assert solution_solve.objective_value == solutions[0].objective_value

def test_get_from_manual_constrained_objective():
    """ test solution of scip model created from objective """
    objective_poly = PolyBinary({(0,): 1, (1,): -1})
    with pytest.warns(UserWarning, match=r"Useless constraint '0 <= \+1 x0 <= 1'"):
        constraint = ConstraintBinary(PolyBinary({(0,): 1}), 0, 1)
    constrained_objective = ConstrainedObjective(objective_poly=objective_poly, constraints={"useless": constraint})
    scip_model = ScipModel.get_from_constrained_objective(constrained_objective)
    solution = scip_model.solve(**{"limits/nodes": 100})
    assert scip_model.getObjVal() == -1
    assert solution.objective_value == -1
    assert solution == {0: 0, 1: 1}

def test_get_from_manual_constrained_objective_infeasible():
    """ test solution of scip model created from objective """
    objective_poly = PolyBinary({(0,): 1, (1,): -1})
    constraint = ConstraintBinary(PolyBinary({(0,): 1}), 2, 3, _check=False)
    constrained_objective = ConstrainedObjective(objective_poly=objective_poly, constraints={"infeasible": constraint})
    scip_model = ScipModel.get_from_constrained_objective(constrained_objective)
    solution = scip_model.solve()
    assert not solution
    assert solution.solving_status == "infeasible"

    with pytest.raises(ValueError, match="Cannot get value for variable '2'"):
        scip_model.get_value(2)
    scip_model.data.update({2: 1})
    assert scip_model.get_value(2) == 1

def test_solve():
    """ test solution of different objectives """
    _assert_solve(Objective(PolyBinary(POLY), "binary"), 1.0, {0: 1, 1: 1, 2: 1, 4: 0, 5: 1, 6: 0, 7: 0})
    _assert_solve(Objective(PolyIsing(POLY),  "ising"), -8.0, {0: 1, 1: 1, 2: 1, 4: -1, 5: 1, 6: -1, 7: -1})
    _assert_solve(Objective(PolyIsing(POLY).invert(), "ising_inverted"), -8.0,
                  {0: -1, 1: -1, 2: -1, 4: 1, 5: -1, 6: 1, 7: 1})

def _assert_solve(objective, exp_objective_value, exp_solution):
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    assert solution.solving_status == OPTIMAL
    assert solution.objective_value == exp_objective_value#
    assert solution == exp_solution

    score_evaluated = objective.polynomial.evaluate(solution)
    assert score_evaluated == exp_objective_value

def test_load_cip(scip_model):
    """ test loading of SCIP model """
    with pytest.warns(UserWarning, match="Cannot retrieve value for 'from_inverted_ising', will use 'None'"):
        loaded = ScipModel.load_cip(FILENAME_FIX)
    scip_model.from_inverted_ising = None
    _check_model(loaded, scip_model)

def test_io_cip(scip_model):
    """ test IO round trip """
    scip_model.save_cip(FILENAME_TMP)
    loaded = scip_model.load_cip(FILENAME_TMP)
    _check_model(loaded, scip_model)
    os.remove(FILENAME_TMP)

def _check_model(loaded, scip_model):
    assert loaded.getProbName() == scip_model.getProbName()
    assert loaded.data.keys() == scip_model.data.keys()
    assert loaded.from_inverted_ising == scip_model.from_inverted_ising

    loaded_constraint = loaded.getConss()[0]
    assert loaded_constraint.isNonlinear()
    assert loaded_constraint.name == QUADRATIC_OBJECTIVE

    loaded_objective = loaded.getObjective()
    objective = scip_model.getObjective()
    loaded_vars = [term[0].name for term in loaded_objective.terms]
    objective_vars = [term[0].name for term in objective.terms]
    assert set(loaded_vars) == set(objective_vars)
