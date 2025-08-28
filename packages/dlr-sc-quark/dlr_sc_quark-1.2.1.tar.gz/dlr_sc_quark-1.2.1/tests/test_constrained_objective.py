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

""" module for testing the ConstrainedObjective by inherited example and without """

import itertools
import pytest

from quark import VariableMapping, PolyBinary, ConstraintBinary, ConstrainedObjective
from quark.constraint_binary import get_reduction_constraints
from quark.testing import ExampleConstrainedObjective
from quark.testing.example_objective_terms import X, ONE_COLOR_PER_NODE, COLORED_EDGES


OBJECTIVE_POLY_FLAT_STR = "+1 x0 x3 +1 x0 x6 +1 x0 x12 +1 x1 x4 +1 x1 x7 +1 x1 x13 +1 x2 x5 " \
                          "+1 x2 x8 +1 x2 x14 +1 x3 x6 +1 x4 x7 +1 x5 x8 +1 x6 x9 +1 x6 x12 " \
                          "+1 x7 x10 +1 x7 x13 +1 x8 x11 +1 x8 x14 +1 x9 x12 +1 x10 x13 +1 x11 x14"

Y, R = "y", "reduction"


def test_init(constrained_objective, exp_constrained_objective):
    """ test constrained objective initialization """
    assert constrained_objective == exp_constrained_objective

def test_repr(constrained_objective):
    """ test string representation """
    constrained_objective.name = "test"
    exp_str = "ExampleConstrainedObjective(" + repr(constrained_objective.objective_poly) + ", " \
              "{'one_color_per_node_1': " + repr(constrained_objective['one_color_per_node_1']) + ", " \
               "'one_color_per_node_2': " + repr(constrained_objective['one_color_per_node_2']) + ", " \
               "'one_color_per_node_3': " + repr(constrained_objective['one_color_per_node_3']) + ", " \
               "'one_color_per_node_4': " + repr(constrained_objective['one_color_per_node_4']) + ", " \
               "'one_color_per_node_5': " + repr(constrained_objective['one_color_per_node_5']) + "}, " \
              "'test')"
    assert repr(constrained_objective) == exp_str

def test_str(constrained_objective):
    """ test string representation """
    exp_str = "min  +1 x_1_blue x_2_blue +1 x_1_blue x_3_blue +1 x_1_blue x_5_blue " \
                   "+1 x_1_green x_2_green +1 x_1_green x_3_green +1 x_1_green x_5_green " \
                   "+1 x_1_red x_2_red +1 x_1_red x_3_red +1 x_1_red x_5_red " \
                   "+1 x_2_blue x_3_blue +1 x_2_green x_3_green +1 x_2_red x_3_red " \
                   "+1 x_3_blue x_4_blue +1 x_3_blue x_5_blue +1 x_3_green x_4_green " \
                   "+1 x_3_green x_5_green +1 x_3_red x_4_red +1 x_3_red x_5_red " \
                   "+1 x_4_blue x_5_blue +1 x_4_green x_5_green +1 x_4_red x_5_red\n" \
              "s.t. 1 == +1 x_1_blue +1 x_1_green +1 x_1_red,\n" \
              "     1 == +1 x_2_blue +1 x_2_green +1 x_2_red,\n" \
              "     1 == +1 x_3_blue +1 x_3_green +1 x_3_red,\n" \
              "     1 == +1 x_4_blue +1 x_4_green +1 x_4_red,\n" \
              "     1 == +1 x_5_blue +1 x_5_green +1 x_5_red,\n" \
              "     x_*_* in {0, 1}"
    assert str(constrained_objective) == exp_str

    # make an inequality
    constrained_objective[ONE_COLOR_PER_NODE + "_2"].lower_bound = -1
    exp_str = "min  +1 x_1_blue x_2_blue +1 x_1_blue x_3_blue +1 x_1_blue x_5_blue " \
                   "+1 x_1_green x_2_green +1 x_1_green x_3_green +1 x_1_green x_5_green " \
                   "+1 x_1_red x_2_red +1 x_1_red x_3_red +1 x_1_red x_5_red " \
                   "+1 x_2_blue x_3_blue +1 x_2_green x_3_green +1 x_2_red x_3_red " \
                   "+1 x_3_blue x_4_blue +1 x_3_blue x_5_blue +1 x_3_green x_4_green " \
                   "+1 x_3_green x_5_green +1 x_3_red x_4_red +1 x_3_red x_5_red " \
                   "+1 x_4_blue x_5_blue +1 x_4_green x_5_green +1 x_4_red x_5_red\n" \
              "s.t.  1 == +1 x_1_blue +1 x_1_green +1 x_1_red,\n" \
              "      1 == +1 x_3_blue +1 x_3_green +1 x_3_red,\n" \
              "      1 == +1 x_4_blue +1 x_4_green +1 x_4_red,\n" \
              "      1 == +1 x_5_blue +1 x_5_green +1 x_5_red,\n" \
              "     -1 <= +1 x_2_blue +1 x_2_green +1 x_2_red <= 1,\n" \
              "     x_*_* in {0, 1}"
    assert str(constrained_objective) == exp_str

    # flat polynomial, only one equality
    flat_poly = PolyBinary.read_from_string(OBJECTIVE_POLY_FLAT_STR)
    flat_constraint = ConstraintBinary(PolyBinary({(1,2) : 1}), 0, 0)
    constrained_objective = ConstrainedObjective(flat_poly, {"flat": flat_constraint})
    exp_str = "min  +1 x0 x3 +1 x0 x6 +1 x0 x12 +1 x1 x4 +1 x1 x7 +1 x1 x13 +1 x2 x5 +1 x2 x8 +1 x2 x14 +1 x3 x6 " \
                   "+1 x4 x7 +1 x5 x8 +1 x6 x9 +1 x6 x12 +1 x7 x10 +1 x7 x13 +1 x8 x11 +1 x8 x14 +1 x9 x12 " \
                   "+1 x10 x13 +1 x11 x14\n" \
              "s.t. 0 == +1 x1 x2,\n" \
              "     x* in {0, 1}"
    assert str(constrained_objective) == exp_str

    # polynomial with string variables, only inequalities
    str_poly = PolyBinary({('a', 'b'): 1, ('b', 'c'): 1})
    flat_constraint1 = ConstraintBinary(PolyBinary({('a',): 1, ('c',): 1}), 0, 1)
    flat_constraint2 = ConstraintBinary(PolyBinary({('a',): -1, ('c',): 1}), -1, 0)
    constrained_objective = ConstrainedObjective(str_poly, {"flat1": flat_constraint1, "flat2": flat_constraint2})
    exp_str = "min  +1 a b +1 b c\n" \
              "s.t.  0 <= +1 a +1 c <= 1,\n" \
              "     -1 <= -1 a +1 c <= 0,\n" \
              "     a in {0, 1},\n" \
              "     b in {0, 1},\n" \
              "     c in {0, 1}"
    assert str(constrained_objective) == exp_str

    # polynomial, no constraints
    poly = PolyBinary({((X, 1, 2), (Y, 0)): 1, ((X, 1, 2), (Y, 1)): 1})
    constrained_objective = ConstrainedObjective(poly)
    exp_str = "min  +1 x_1_2 y_0 +1 x_1_2 y_1\n" \
              "s.t. x_*_* in {0, 1},\n" \
              "     y_* in {0, 1}"
    assert str(constrained_objective) == exp_str

def test_get_from_instance(instance, constrained_objective):
    """ test different initialization methods """
    constrained_objective_get = ExampleConstrainedObjective.get_from_instance(instance)
    assert constrained_objective_get == constrained_objective

    with pytest.warns(DeprecationWarning, match="This way of instantiation is deprecated"):
        constrained_objective_depr = ExampleConstrainedObjective(instance=instance)
    assert constrained_objective_depr == constrained_objective

def test_get_all_variables(constrained_objective):
    """ test getting all variables """
    exp_variables = [(X, 1, "blue"), (X, 1, "green"), (X, 1, "red"), (X, 2, "blue"), (X, 2, "green"), (X, 2, "red"),
                     (X, 3, "blue"), (X, 3, "green"), (X, 3, "red"), (X, 4, "blue"), (X, 4, "green"), (X, 4, "red"),
                     (X, 5, "blue"), (X, 5, "green"), (X, 5, "red")]
    assert constrained_objective.get_all_variables() == exp_variables

    # introduce constraint with wrong variables manually
    constrained_objective["wrong"] = ConstraintBinary(PolyBinary({("x",): 1, ("y",): 1}), 0, 1)
    with pytest.raises(TypeError, match="Objective polynomial's and constraints' variable types do not match"):
        constrained_objective.get_all_variables()

    constrained_objective["wrong"] = ConstraintBinary(PolyBinary({((X, "a"),): 1, ((X, "b"),): 1}), 0, 1)
    with pytest.raises(ValueError, match="Sorting failed"):
        constrained_objective.get_all_variables()

    constrained_objective = ConstrainedObjective(PolyBinary({(4, 5): 1}),
                                                 {"constraint": ConstraintBinary(PolyBinary({(1, 2): 1}), 0, 0)})
    assert constrained_objective.get_all_variables() == [1, 2, 4, 5]

def test_get_redundant_constraints():
    """ test getting the name of the redundant constraints """
    objective_poly = PolyBinary({(0,): 7, (1, 0): 2, (): -1})
    quadratic_poly = PolyBinary({(0,): 7, (1, 0): 2, (): -3})
    quadratic_constraint = ConstraintBinary(quadratic_poly, 5, 6)
    constraints = {"quadratic": quadratic_constraint,
                   "again": ConstraintBinary(quadratic_poly, 5, 6),
                   "scaled": quadratic_constraint * 2,
                   "shifted": quadratic_constraint + 1,
                   "scaled_shifted": quadratic_constraint * 2 + 1}

    # if redundancy checks are omitted, no warnings are thrown
    constrained_objective = ConstrainedObjective(objective_poly=objective_poly, constraints=constraints,
                                                 check_redundant_constraints=False)
    # without flag, we have warnings
    with pytest.warns(UserWarning, match=r"The ConstrainedObjective contains 4 redundant constraint\(s\)"):
        constrained_objective = ConstrainedObjective(objective_poly=objective_poly, constraints=constraints)
    exp_constraints = {"again", "scaled", "shifted", "scaled_shifted"}
    assert constrained_objective.get_redundant_constraints() == exp_constraints

    # the ordering is important: the first will be marked as non-redundant while the following are redundant
    constraints = {"scaled_shifted": quadratic_constraint * 2 + 1, "quadratic": quadratic_constraint}
    with pytest.warns(UserWarning, match=r"The ConstrainedObjective contains 1 redundant constraint\(s\)"):
        constrained_objective = ConstrainedObjective(objective_poly=objective_poly, constraints=constraints)
    exp_constraints = {"quadratic"}
    assert constrained_objective.get_redundant_constraints() == exp_constraints

def test_remove_redundant_constraints(constrained_objective):
    """ test redundant constraints methods """
    # Case 0: Removing constraints from a ConstraintObjective without redundant constraints
    assert constrained_objective.remove_redundant_constraints() == constrained_objective

    # Case 1: Linear constraints
    poly1 = PolyBinary({((X, 1, "red"),): 1, ((X, 1, "green"),): 1, ((X, 1, "blue"),): 1})
    poly2 = PolyBinary({((X, 2, "red"),): 2, ((X, 2, "green"),): 2, ((X, 2, "blue"),): 2})
    poly3 = PolyBinary({((X, 3, "red"),): 1, ((X, 3, "green"),): 1, ((X, 3, "blue"),): 1, (): 1})
    poly4 = PolyBinary({((X, 4, "red"),): 2, ((X, 4, "green"),): 2, ((X, 4, "blue"),): 2, (): 2})
    redundant_cons = {"again_1": ConstraintBinary(poly1, 1, 1),
                      "scaled_2": ConstraintBinary(poly2, 2, 2),
                      "shifted_3": ConstraintBinary(poly3, 2, 2),
                      "scaled_shifted_4": ConstraintBinary(poly4, 4, 4)}
    with pytest.warns(UserWarning, match=r"The ConstrainedObjective contains 4 redundant constraint\(s\)"):
        red_constrained_objective = ConstrainedObjective(objective_poly=constrained_objective.objective_poly,
                                                         constraints=constrained_objective|redundant_cons)
    assert red_constrained_objective.remove_redundant_constraints() == constrained_objective

    # Case 2: Quadratic constraints
    objective_poly = PolyBinary({(0,): 7, (1, 0): 2, (): -1})
    quadratic_poly = PolyBinary({(0,): 7, (1, 0): 2, (): -3})
    quadratic_constraint = ConstraintBinary(quadratic_poly, 5, 6)
    constraints = {"quadratic": quadratic_constraint}
    redundant_constraints = {"again": ConstraintBinary(quadratic_poly, 5, 6),
                             "scaled": quadratic_constraint * 2,
                             "shifted": quadratic_constraint + 1,
                             "scaled_shifted": quadratic_constraint * 2 + 1}

    exp_constrained_objective = ConstrainedObjective(objective_poly=objective_poly, constraints=constraints)
    with pytest.warns(UserWarning, match=r"The ConstrainedObjective contains 4 redundant constraint\(s\)"):
        red_constrained_objective = ConstrainedObjective(objective_poly=objective_poly,
                                                         constraints=constraints|redundant_constraints)
    assert red_constrained_objective.remove_redundant_constraints() == exp_constrained_objective

def test_get_broken_constraints(constrained_objective, solution):
    """ test broken constraints """
    assert constrained_objective.get_broken_constraints(solution) == []
    solution[(X, 2, "green")] = 1
    assert constrained_objective.get_broken_constraints(solution) == [ONE_COLOR_PER_NODE + "_2"]

def test_check_validity(constrained_objective, solution):
    """ test validity of solution """
    assert constrained_objective.check_validity(solution)

    solution[(X, 2, "green")] = 1
    assert not constrained_objective.check_validity(solution)

def test_get_original_problem_solution(constrained_objective, solution):
    """ test solution extraction """
    exp_original_solution = {1: 'blue', 2: 'red', 3: 'green', 4: 'blue', 5: 'red'}
    assert constrained_objective.get_original_problem_solution(solution) == exp_original_solution

def test_init__check_consistency(instance):
    """ test the errors """
    # pylint: disable=protected-access
    with pytest.warns(DeprecationWarning, match="This way of instantiation is deprecated"):
        ExampleConstrainedObjective(instance=instance)
    with pytest.raises(NotImplementedError, match="Provide 'objective_poly' on initialization or "):
        ConstrainedObjective._get_objective_poly(None)
    with pytest.raises(NotImplementedError, match="Provide 'constraints' on initialization or "):
        ConstrainedObjective._get_constraints(None)
    with pytest.raises(ValueError, match="Currently only binary objective functions are supported for the"):
        ConstrainedObjective(PolyBinary({"x0" : 1}).to_ising(), {})
    # Variable Types
    with pytest.raises(TypeError, match="Objective polynomial's and constraints' variable types do not match"):
        ConstrainedObjective(PolyBinary({(("x", 1),): 1}),
                             {"constraint": ConstraintBinary(PolyBinary({(0,): 1, (1,): 2}), 0, 1)})
    with pytest.raises(TypeError, match="Objective polynomial's and constraints' variable types do not match"):
        ConstrainedObjective(PolyBinary({(("x", 1),): 1}),
                             {"constraint": ConstraintBinary(PolyBinary({("x",): 1, ("y",): 2}), 0, 2)})
    with pytest.raises(TypeError, match="Objective polynomial's and constraints' variable types do not match"):
        ConstrainedObjective(PolyBinary({(0, 1): 1}),
                             {"constraint": ConstraintBinary(PolyBinary({("x",): 1, ("y",): 2}), 0, 2)})
    with pytest.raises(ValueError, match="Sorting failed"):
        ConstrainedObjective(PolyBinary({(("x", 0), ("x", 1)): 1}),
                             {"constraint": ConstraintBinary(PolyBinary({(("x", "0"),): 1, (("x", "1"),): 2}), 0, 2)})

def test_is_compact(constrained_objective):
    """ test check for compact constrained objectives """
    assert not constrained_objective.is_compact()

    compact, _ = constrained_objective.compact()
    assert compact.is_compact()

    objective_poly = PolyBinary({(1, 2, 3): 1, (1,) : -1})
    constraint = ConstraintBinary(PolyBinary({(1, 2): 1, (2,): -1}), 0, 1)
    constrained_objective = ConstrainedObjective(objective_poly, {"constraint": constraint})
    assert not constrained_objective.is_compact()

    constrained_objective["additional_constraint"] = ConstraintBinary(PolyBinary({(0,): 1, (1,): 1}), 0, 1)
    assert constrained_objective.is_compact()

def test_compact(constrained_objective):
    """ test making the polynomials compact """
    exp_compact_poly = PolyBinary({(0, 3): 1, (0, 6): 1, (0, 12): 1, (1, 4): 1, (1, 7): 1, (1, 13): 1, (2, 5): 1,
                                   (2, 8): 1, (2, 14): 1, (3, 6): 1, (4, 7): 1, (5, 8): 1, (6, 9): 1, (6, 12): 1,
                                  (7, 10): 1, (7, 13): 1, (8, 11): 1, (8, 14): 1, (9, 12): 1, (10, 13): 1, (11, 14): 1})
    exp_compact_constraints = {'one_color_per_node_1': ConstraintBinary(PolyBinary({(0,): 1, (1,): 1, (2,): 1}), 1, 1),
                               'one_color_per_node_2': ConstraintBinary(PolyBinary({(3,): 1, (4,): 1, (5,): 1}), 1, 1),
                               'one_color_per_node_3': ConstraintBinary(PolyBinary({(6,): 1, (7,): 1, (8,): 1}), 1, 1),
                               'one_color_per_node_4': ConstraintBinary(PolyBinary({(9,): 1, (10,): 1, (11,): 1}), 1,1),
                               'one_color_per_node_5': ConstraintBinary(PolyBinary({(12,): 1, (13,): 1, (14,): 1}),1,1)}
    exp_var_mapping = VariableMapping({0: ('x', 1, 'blue'), 1: ('x', 1, 'green'), 2: ('x', 1, 'red'),
                                       3: ('x', 2, 'blue'), 4: ('x', 2, 'green'), 5: ('x', 2, 'red'),
                                       6: ('x', 3, 'blue'), 7: ('x', 3, 'green'), 8: ('x', 3, 'red'),
                                       9: ('x', 4, 'blue'), 10: ('x', 4, 'green'), 11: ('x', 4, 'red'),
                                       12: ('x', 5, 'blue'), 13: ('x', 5, 'green'), 14: ('x', 5, 'red')})
    compact, var_mapping = constrained_objective.compact()
    assert not compact.name
    assert compact.objective_poly == exp_compact_poly
    assert dict(compact) == exp_compact_constraints
    assert var_mapping == exp_var_mapping

    # nothing happens when applying again
    assert compact.compact() == (compact, None)

    # more variables in the constraints than in the objective_poly
    objective_poly = PolyBinary({(('x', 3, "blue"), ('x', 4, "blue")): 1, (('x', 3, "red"), ('x', 4, "red")): 1})
    constrained_objective = ConstrainedObjective(objective_poly, constraints=dict(constrained_objective))
    exp_compact_poly = PolyBinary({(6, 9): 1, (8, 11): 1})
    compact, var_mapping = constrained_objective.compact("new_name")
    assert compact.name == "new_name"
    assert compact.objective_poly == exp_compact_poly
    assert dict(compact) == exp_compact_constraints
    assert var_mapping == exp_var_mapping

def test_get_objective_terms__two_paths(constrained_objective, objective_terms):
    """ test objective terms creation by comparing it to constrained_objective """
    objective_terms_from_co = constrained_objective.get_objective_terms(COLORED_EDGES, combine_prefixes=())
    one_color_per_node_polys = dict(itertools.islice(objective_terms_from_co.items(), 5))
    one_color_per_node_sum_poly = sum(one_color_per_node_polys.values())
    assert objective_terms_from_co[COLORED_EDGES] == objective_terms[COLORED_EDGES]
    assert one_color_per_node_sum_poly == objective_terms[ONE_COLOR_PER_NODE]

    ots_from_co_combined = constrained_objective.get_objective_terms(COLORED_EDGES, combine_prefixes=ONE_COLOR_PER_NODE)
    assert ots_from_co_combined != objective_terms_from_co
    assert ots_from_co_combined == objective_terms

def test_constrained_objective_creation_no_impl():
    """ test constrained objective creation with constraint initialization """
    objective_poly = PolyBinary.read_from_string(OBJECTIVE_POLY_FLAT_STR)
    constraint = ConstraintBinary(PolyBinary.read_from_string("x0 + x1 + x2"), 1, 1)
    constraints = {ONE_COLOR_PER_NODE : constraint}
    constrained_objective = ConstrainedObjective(objective_poly, constraints)
    assert constrained_objective.objective_poly == objective_poly
    assert dict(constrained_objective) == constraints
    assert constrained_objective != ConstrainedObjective(PolyBinary({(0,): 1}), constraints)
    assert constrained_objective != constraints

    with pytest.warns(UserWarning, match="There is nothing in this ConstrainedObjective"):
        ConstrainedObjective(PolyBinary())

def test_reduce():
    """ test the reduction of the constrained objective """
    objective_poly = PolyBinary({((X, 1, 1), (Y, 0)): 1, ((X, 1, 1), (Y, 1)): 3, ((X, 1, 2), (Y, 2),): 2})
    constraints = {"max_one_x": ConstraintBinary(PolyBinary({((X, 1, 1),): 1, ((X, 1, 2),): 1}), 0, 1),
                   "exactly_one_y": ConstraintBinary(PolyBinary({((Y, 0),): 1, ((Y, 1),): 1, ((Y, 2),): 1}), 1, 1)}
    constrained_objective = ConstrainedObjective(objective_poly, constraints)

    # nothing happens
    reduced_obj_poly, reduced_constraints, reductions = constrained_objective.get_reductions()
    assert reduced_obj_poly == objective_poly
    assert reduced_constraints == constraints
    assert reductions == []

    # apply prepared reductions
    exp_objective_poly = PolyBinary({((R, X, 1, 1, Y, 0),): 1,
                                     ((R, X, 1, 1, Y, 1),): 3,
                                     ((R, X, 1, 2, Y, 2),): 2})
    reduced_constrained_objective = constrained_objective.reduce(use=[((R, X, 1, 1, Y, 0), (X, 1, 1), (Y, 0)),
                                                                      ((R, X, 1, 1, Y, 1), (X, 1, 1), (Y, 1)),
                                                                      ((R, X, 1, 2, Y, 2), (X, 1, 2), (Y, 2))])
    assert reduced_constrained_objective.objective_poly == exp_objective_poly
    assert dict(reduced_constrained_objective) == constraints

    # force the reduction
    exp_constraint_x_reduced = ConstraintBinary(PolyBinary({((X, 1, 1),): 1, ((X, 1, 2),): 1}), 0, 1)
    exp_constraint_y_reduced = ConstraintBinary(PolyBinary({((Y, 0),): 1, ((Y, 1),): 1, ((Y, 2),): 1}), 1, 1)
    exp_constraints = {'max_one_x': exp_constraint_x_reduced,
                       'exactly_one_y': exp_constraint_y_reduced}

    reduced_obj_poly, reduced_constraints, reductions = constrained_objective.get_reductions(force=True)
    assert reduced_obj_poly == exp_objective_poly
    assert reduced_constraints == exp_constraints
    assert reductions == [((R, X, 1, 1, Y, 0), (X, 1, 1), (Y, 0)),
                          ((R, X, 1, 1, Y, 1), (X, 1, 1), (Y, 1)),
                          ((R, X, 1, 2, Y, 2), (X, 1, 2), (Y, 2))]

    # get all reduction constraints
    exp_poly_dicts = [{(): 1, ((R, X, 1, 1, Y, 0),): 1, ((X, 1, 1),): -1},
                      {(): 1, ((R, X, 1, 1, Y, 0),): 1, ((Y, 0),): -1},
                      {(): 1, ((R, X, 1, 1, Y, 0),): 1, ((X, 1, 1),): -1, ((Y, 0),): -1},
                      {(): 1, ((R, X, 1, 1, Y, 1),): 1, ((X, 1, 1),): -1},
                      {(): 1, ((R, X, 1, 1, Y, 1),): 1, ((Y, 1),): -1},
                      {(): 1, ((R, X, 1, 1, Y, 1),): 1, ((X, 1, 1),): -1, ((Y, 1),): -1},
                      {(): 1, ((R, X, 1, 2, Y, 2),): 1, ((X, 1, 2),): -1},
                      {(): 1, ((R, X, 1, 2, Y, 2),): 1, ((Y, 2),): -1},
                      {(): 1, ((R, X, 1, 2, Y, 2),): 1, ((X, 1, 2),): -1, ((Y, 2),): -1}]
    exp_names = ['reduction_x_1_1_y_0_0', 'reduction_x_1_1_y_0_1', 'reduction_x_1_1_y_0_2', 'reduction_x_1_1_y_1_0',
                 'reduction_x_1_1_y_1_1', 'reduction_x_1_1_y_1_2', 'reduction_x_1_2_y_2_0', 'reduction_x_1_2_y_2_1',
                 'reduction_x_1_2_y_2_2']
    exp_constraints.update(dict(zip(exp_names, [ConstraintBinary(PolyBinary(d), 0, 1) for d in exp_poly_dicts])))
    exp_constrained_objective = ConstrainedObjective(exp_objective_poly, exp_constraints)
    reduced_constrained_objective = constrained_objective.reduce(force=True)
    assert reduced_constrained_objective == exp_constrained_objective

def test_reduce__two_steps():
    """ test reduction in two steps """
    # first step
    objective_poly = PolyBinary({((X, 1), (X, 2), (X, 3)): 1})
    constraint_x = ConstraintBinary(PolyBinary({((X, 2),): 1, ((X, 3),): 1}), 0, 1)
    constraints = {"max_one_x": constraint_x}
    constrained_objective = ConstrainedObjective(objective_poly, constraints)

    exp_objective_poly = PolyBinary({((R, X, 1, X, 2), (X, 3)): 1})
    exp_constraint_red = ConstraintBinary(PolyBinary({((R, X, 1, X, 2),): 1, ((X, 1), (X, 2)): -1}), 0, 0)
    exp_constraints = {"max_one_x": constraint_x, "reduction_x_1_x_2": exp_constraint_red}
    exp_constrained_objective = ConstrainedObjective(exp_objective_poly, exp_constraints)

    reduced_constrained_objective = constrained_objective.reduce(max_degree=2)
    assert reduced_constrained_objective == exp_constrained_objective

    # reduce further, without force
    exp_objective_poly = PolyBinary({((R, X, 1, X, 2), (X, 3)): 1})
    exp_constraints = {"max_one_x": constraint_x}
    exp_constraints.update(get_reduction_constraints((R, X, 1, X, 2), (X, 1), (X, 2)))
    exp_constrained_objective = ConstrainedObjective(exp_objective_poly, exp_constraints)

    reduced_constrained_objective2 = reduced_constrained_objective.reduce(1)
    assert reduced_constrained_objective2 == exp_constrained_objective

    # reduce further, with force
    exp_objective_poly = PolyBinary({((R, R, X, 1, X, 2, X, 3),): 1})
    exp_constraints = {"max_one_x": ConstraintBinary(PolyBinary({((X, 2),): 1, ((X, 3),): 1}), 0, 1)}
    exp_constraints.update(get_reduction_constraints((R, X, 1, X, 2), (X, 1), (X, 2)))
    exp_constraints.update(get_reduction_constraints((R, R, X, 1, X, 2, X, 3), (R, X, 1, X, 2), (X, 3)))
    exp_constrained_objective = ConstrainedObjective(exp_objective_poly, exp_constraints)

    reduced_constrained_objective3 = reduced_constrained_objective2.reduce(1, force=True)
    assert reduced_constrained_objective3 == exp_constrained_objective

    reduced_constrained_objective2_direct_force = reduced_constrained_objective.reduce(1, force=True)
    assert reduced_constrained_objective2_direct_force == exp_constrained_objective

def test_reduce__big_example(constrained_objective, exp_constrained_objective, instance):
    """ test the automatic reduction of the objective function and the constraint polynomials """
    # nothing happens
    reduced_constrained_objective = constrained_objective.reduce()
    assert reduced_constrained_objective == exp_constrained_objective

    # several reductions are applied
    exp_constraints = dict(exp_constrained_objective)
    exp_objective_poly = PolyBinary({((R, X, n1, c, X, n2, c),): 1
                                     for n1, n2 in instance.edges for c in instance.colors})
    exp_reductions = {((R, X, n1, c, X, n2, c), (X, n1, c), (X, n2, c))
                      for n1, n2 in instance.edges for c in instance.colors}
    reduced_obj_poly, reduced_constraints, reductions = constrained_objective.get_reductions(force=True)
    assert reduced_obj_poly == exp_objective_poly
    assert reduced_constraints == exp_constraints
    assert set(reductions) == exp_reductions

    for n1, n2 in instance.edges:
        for c in instance.colors:
            names = [f"reduction_x_{n1}_{c}_x_{n2}_{c}_0",
                     f"reduction_x_{n1}_{c}_x_{n2}_{c}_1",
                     f"reduction_x_{n1}_{c}_x_{n2}_{c}_2"]
            polys = [PolyBinary({((R, X, n1, c, X, n2, c),): 1, ((X, n1, c),): -1, (): 1}),
                     PolyBinary({((R, X, n1, c, X, n2, c),): 1, ((X, n2, c),): -1, (): 1}),
                     PolyBinary({((R, X, n1, c, X, n2, c),): 1, ((X, n1, c),): -1, ((X, n2, c),): -1, (): 1})]
            exp_constraints.update(dict(zip(names, [ConstraintBinary(p, 0, 1) for p in polys])))
    exp_constrained_objective = ExampleConstrainedObjective(exp_objective_poly, exp_constraints)
    reduced_constrained_objective = constrained_objective.reduce(force=True)
    assert reduced_constrained_objective == exp_constrained_objective

def test_get_objective_terms(constrained_objective, exp_objective_terms):
    """ test objective terms creation """
    objective_terms = constrained_objective.get_objective_terms(COLORED_EDGES)
    assert objective_terms == exp_objective_terms

    # without explicit objective polynomial
    constrained_objective.objective_poly = PolyBinary()
    objective_terms = constrained_objective.get_objective_terms(COLORED_EDGES)
    assert not COLORED_EDGES in objective_terms

def test_get_objective_terms__reduction():
    """ test objective terms creation with automatic reduction """
    objective_poly = PolyBinary({(("x", 1), ("x", 2), ("x", 3)): 1, (("x", 1),) : -1})
    constraint = ConstraintBinary(PolyBinary({(("x", 1), ("x", 2)): 1, (("x", 2),): -1}), 0, 1)
    constrained_objective = ConstrainedObjective(objective_poly, {"constraint": constraint})

    # without checking for special constraints everything is reduced
    objective_terms = constrained_objective.get_objective_terms(check_special_constraints=False)
    exp_objective_poly = PolyBinary({((X, 1),): -1, ((R, X, 1, X, 2), (X, 3)): 1})
    exp_reduction_poly = PolyBinary({((R, X, 1, X, 2),): 3,
                                     ((R, X, 1, X, 2), (X, 1)): -2,
                                     ((R, X, 1, X, 2), (X, 2)): -2,
                                     ((X, 1), (X, 2)): 1})
    exp_constraint_poly = PolyBinary({(): 0,
                                      (('constraint_slack', 0),): 1,
                                      (('constraint_slack', 0), (R, X, 1, X, 2)): -2,
                                      (('constraint_slack', 0), (X, 2)): 2,
                                      ((R, X, 1, X, 2),): 1,
                                      ((R, X, 1, X, 2), (X, 2)): -2,
                                      ((X, 2),): 1})
    assert len(objective_terms) == 3
    assert objective_terms["objective"] == exp_objective_poly
    assert objective_terms["reduction"] == exp_reduction_poly
    assert objective_terms["constraint"] == exp_constraint_poly

    # with checking no slack variables are introduced
    objective_terms = constrained_objective.get_objective_terms()
    exp_constraint_poly = PolyBinary({((X, 2),): 1, ((R, X, 1, X, 2), (X, 2)): -1})
    assert len(objective_terms) == 3
    assert objective_terms["objective"] == exp_objective_poly
    assert objective_terms["reduction"] == exp_reduction_poly
    assert objective_terms["constraint"] == exp_constraint_poly

    # even if we reduce beforehand, the objective terms remain the same
    constrained_objective_reduced = constrained_objective.reduce()
    assert len(constrained_objective_reduced) == 4  # 1 original constraint and 3 reductions constraints
    objective_terms_reduced = constrained_objective_reduced.get_objective_terms()
    assert objective_terms_reduced == objective_terms
    # TODO: add more tests here!
