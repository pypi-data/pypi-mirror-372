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

""" module for testing the ObjectiveTerms by inherited example and without """

import pytest

from quark import Polynomial, PolyBinary, PolyIsing, ObjectiveTerms
from quark.testing import ExampleInstance, ExampleObjectiveTerms
from quark.testing.example_objective_terms import X, COLORED_EDGES, ONE_COLOR_PER_NODE
from quark.objective_terms import get_naive_terms_weights


B, G, R = "blue", "green", "red"
REDUCTION = "reduction"

@pytest.fixture(name="objective_terms_different_types")
def fixture_objective_terms_different_types():
    """ provide test objective terms with different types """
    poly_ising = PolyIsing({(0, 1): 2, (2, 3): 4})
    poly_binary = PolyBinary({(0, 1): 2, (2, 3): 4})
    poly_none = Polynomial({(1, 2): 3})
    terms = {"ising": poly_ising, "binary": poly_binary, "none": poly_none}
    yield ExampleObjectiveTerms(objective_terms=terms, constraint_terms_names=["ising", "binary"])


def test_init(objective_terms, exp_objective_terms):
    """ test objective terms creation """
    assert objective_terms == exp_objective_terms

def test_repr(objective_terms):
    """ test string representation """
    exp_str = "ObjectiveTerms({'colored_edges': PolyBinary({(('x', 1, 'blue'), ('x', 2, 'blue')): 1, " \
                                                           "(('x', 1, 'blue'), ('x', 3, 'blue')): 1, " \
                                                           "(('x', 1, 'blue'), ('x', 5, 'blue')): 1, " \
                                                           "(('x', 1, 'green'), ('x', 2, 'green')): 1, " \
                                                           "(('x', 1, 'green'), ('x', 3, 'green')): 1, " \
                                                           "(('x', 1, 'green'), ('x', 5, 'green')): 1, " \
                                                           "(('x', 1, 'red'), ('x', 2, 'red')): 1, " \
                                                           "(('x', 1, 'red'), ('x', 3, 'red')): 1, " \
                                                           "(('x', 1, 'red'), ('x', 5, 'red')): 1, " \
                                                           "(('x', 2, 'blue'), ('x', 3, 'blue')): 1, " \
                                                           "(('x', 2, 'green'), ('x', 3, 'green')): 1, " \
                                                           "(('x', 2, 'red'), ('x', 3, 'red')): 1, " \
                                                           "(('x', 3, 'blue'), ('x', 4, 'blue')): 1, " \
                                                           "(('x', 3, 'blue'), ('x', 5, 'blue')): 1, " \
                                                           "(('x', 3, 'green'), ('x', 4, 'green')): 1, " \
                                                           "(('x', 3, 'green'), ('x', 5, 'green')): 1, " \
                                                           "(('x', 3, 'red'), ('x', 4, 'red')): 1, " \
                                                           "(('x', 3, 'red'), ('x', 5, 'red')): 1, " \
                                                           "(('x', 4, 'blue'), ('x', 5, 'blue')): 1, " \
                                                           "(('x', 4, 'green'), ('x', 5, 'green')): 1, " \
                                                           "(('x', 4, 'red'), ('x', 5, 'red')): 1}), " \
              "'one_color_per_node': PolyBinary({(): 5, " \
                              "(('x', 1, 'blue'),): -1, (('x', 1, 'green'),): -1, (('x', 1, 'red'),): -1, " \
                              "(('x', 2, 'blue'),): -1, (('x', 2, 'green'),): -1, (('x', 2, 'red'),): -1, " \
                              "(('x', 3, 'blue'),): -1, (('x', 3, 'green'),): -1, (('x', 3, 'red'),): -1, " \
                              "(('x', 4, 'blue'),): -1, (('x', 4, 'green'),): -1, (('x', 4, 'red'),): -1, " \
                              "(('x', 5, 'blue'),): -1, (('x', 5, 'green'),): -1, (('x', 5, 'red'),): -1, " \
                              "(('x', 1, 'blue'), ('x', 1, 'green')): 2, (('x', 1, 'blue'), ('x', 1, 'red')): 2, " \
                              "(('x', 1, 'green'), ('x', 1, 'red')): 2, (('x', 2, 'blue'), ('x', 2, 'green')): 2, " \
                              "(('x', 2, 'blue'), ('x', 2, 'red')): 2, (('x', 2, 'green'), ('x', 2, 'red')): 2, " \
                              "(('x', 3, 'blue'), ('x', 3, 'green')): 2, (('x', 3, 'blue'), ('x', 3, 'red')): 2, " \
                              "(('x', 3, 'green'), ('x', 3, 'red')): 2, (('x', 4, 'blue'), ('x', 4, 'green')): 2, " \
                              "(('x', 4, 'blue'), ('x', 4, 'red')): 2, (('x', 4, 'green'), ('x', 4, 'red')): 2, " \
                              "(('x', 5, 'blue'), ('x', 5, 'green')): 2, (('x', 5, 'blue'), ('x', 5, 'red')): 2, " \
                              "(('x', 5, 'green'), ('x', 5, 'red')): 2})}, ['one_color_per_node'], None)"
    assert repr(objective_terms) == exp_str

def test_str(objective_terms):
    """ test string representation """
    exp_str = "min  P_0 * ( +1 x_1_blue x_2_blue +1 x_1_blue x_3_blue +1 x_1_blue x_5_blue +1 x_1_green x_2_green " \
                           "+1 x_1_green x_3_green +1 x_1_green x_5_green +1 x_1_red x_2_red +1 x_1_red x_3_red " \
                           "+1 x_1_red x_5_red +1 x_2_blue x_3_blue +1 x_2_green x_3_green +1 x_2_red x_3_red " \
                           "+1 x_3_blue x_4_blue +1 x_3_blue x_5_blue +1 x_3_green x_4_green +1 x_3_green x_5_green " \
                           "+1 x_3_red x_4_red +1 x_3_red x_5_red +1 x_4_blue x_5_blue +1 x_4_green x_5_green " \
                           "+1 x_4_red x_5_red )\n" \
              "     + P_1 * ( +5 -1 x_1_blue -1 x_1_green -1 x_1_red -1 x_2_blue -1 x_2_green -1 x_2_red -1 x_3_blue " \
                             "-1 x_3_green -1 x_3_red -1 x_4_blue -1 x_4_green -1 x_4_red -1 x_5_blue -1 x_5_green " \
                             "-1 x_5_red +2 x_1_blue x_1_green +2 x_1_blue x_1_red +2 x_1_green x_1_red " \
                             "+2 x_2_blue x_2_green +2 x_2_blue x_2_red +2 x_2_green x_2_red +2 x_3_blue x_3_green " \
                             "+2 x_3_blue x_3_red +2 x_3_green x_3_red +2 x_4_blue x_4_green +2 x_4_blue x_4_red " \
                             "+2 x_4_green x_4_red +2 x_5_blue x_5_green +2 x_5_blue x_5_red +2 x_5_green x_5_red )\n" \
              "s.t. x_*_* in {0, 1}"
    assert str(objective_terms) == exp_str

    objective_terms[ONE_COLOR_PER_NODE] = objective_terms[ONE_COLOR_PER_NODE].to_ising() \
                                          .replace_variables(lambda tup: ("s", *tup[1:]))
                                          # change from "x" to "s" in the variable tuples
    exp_str = "min  P_0 * ( +1 x_1_blue x_2_blue +1 x_1_blue x_3_blue +1 x_1_blue x_5_blue +1 x_1_green x_2_green " \
                           "+1 x_1_green x_3_green +1 x_1_green x_5_green +1 x_1_red x_2_red +1 x_1_red x_3_red " \
                           "+1 x_1_red x_5_red +1 x_2_blue x_3_blue +1 x_2_green x_3_green +1 x_2_red x_3_red " \
                           "+1 x_3_blue x_4_blue +1 x_3_blue x_5_blue +1 x_3_green x_4_green +1 x_3_green x_5_green " \
                           "+1 x_3_red x_4_red +1 x_3_red x_5_red +1 x_4_blue x_5_blue +1 x_4_green x_5_green " \
                           "+1 x_4_red x_5_red )\n" \
              "     + P_1 * ( +5 +0.5 s_1_blue +0.5 s_1_green +0.5 s_1_red +0.5 s_2_blue +0.5 s_2_green +0.5 s_2_red " \
                             "+0.5 s_3_blue +0.5 s_3_green +0.5 s_3_red +0.5 s_4_blue +0.5 s_4_green +0.5 s_4_red " \
                             "+0.5 s_5_blue +0.5 s_5_green +0.5 s_5_red +0.5 s_1_blue s_1_green " \
                             "+0.5 s_1_blue s_1_red +0.5 s_1_green s_1_red +0.5 s_2_blue s_2_green " \
                             "+0.5 s_2_blue s_2_red +0.5 s_2_green s_2_red +0.5 s_3_blue s_3_green " \
                             "+0.5 s_3_blue s_3_red +0.5 s_3_green s_3_red +0.5 s_4_blue s_4_green " \
                             "+0.5 s_4_blue s_4_red +0.5 s_4_green s_4_red +0.5 s_5_blue s_5_green " \
                             "+0.5 s_5_blue s_5_red +0.5 s_5_green s_5_red )\n" \
              "s.t. s_*_* in {-1, 1},\n" \
              "     x_*_* in {0, 1}"
    assert str(objective_terms) == exp_str

def test_get_from_instance(objective_terms_direct_impl, exp_objective_terms, instance):
    """ test different initialization methods """
    # note that at the same time, this also tests two different implementations:
    #     - the fixture objective_terms relies on the implementation of the ExampleConstrainedObjective,
    #       from which we get then automatically generate the corresponding ObjectiveTerms
    #     - objective_terms_get uses the direct implementation of the ExampleObjectiveTerms
    assert objective_terms_direct_impl == exp_objective_terms

    with pytest.warns(DeprecationWarning, match="This way of instantiation is deprecated"):
        objective_terms_depr = ExampleObjectiveTerms(instance=instance)
    assert objective_terms_depr == exp_objective_terms

def test_get_objective(objective_terms, exp_objective):
    """ test objective creation """
    terms_weights = {COLORED_EDGES : 1, ONE_COLOR_PER_NODE : 7}
    poly = objective_terms.get_weighted_sum_polynomial(terms_weights)
    assert isinstance(poly, PolyBinary)
    assert poly == exp_objective.polynomial

    objective = objective_terms.get_objective(terms_weights)
    assert objective == exp_objective

    objective = objective_terms.get_objective(penalty_scale=7)
    assert objective == exp_objective

    with pytest.warns(UserWarning, match="If the terms weights are given, the penalty scale is ignored"):
        objective_terms.get_objective(terms_weights, penalty_scale=7)
    assert objective == exp_objective

    with pytest.raises(ValueError, match="There is a mismatch between given and stored objective_terms names"):
        objective_terms.get_objective({"wrong_pw" : 4})
    with pytest.raises(ValueError, match="Cannot add PolyIsing and PolyBinary"):
        objective_terms.get_weighted_sum_polynomial({COLORED_EDGES : 1.0, ONE_COLOR_PER_NODE : PolyIsing()})

def test_evaluate_terms(objective_terms, solution):
    """ test check solution """
    values = objective_terms.evaluate_terms(solution)
    assert values[COLORED_EDGES] == 0.0
    assert values[ONE_COLOR_PER_NODE] == 0.0

def test_check_validity(objective_terms, solution):
    """ test check solution """
    assert objective_terms.check_validity(solution)

    solution[(X, 2, "green")] = 1
    assert not objective_terms.check_validity(solution)

def test_get_string(objective_terms):
    """ test if unique string is generated correctly """
    terms_weights = {COLORED_EDGES : 1.0, ONE_COLOR_PER_NODE : 2.4}
    exp_str = "colored_edges1.000000e+00_one_color_per_node2.400000e+00"
    assert objective_terms.get_terms_weights_string(terms_weights) == exp_str

def test_objective_terms_creation_no_impl():
    """ test objective terms creation """
    colored_edges = PolyBinary.read_from_string("5 + x0 x1 + x1 x2 + x2 x3 + x0 x3 + x0 x2")
    one_color_per_node = PolyBinary.read_from_string("1 - x0")
    objective_terms_dict = {"colored_edges": colored_edges, "one_color_per_node": one_color_per_node}
    constraint_terms_names = [ONE_COLOR_PER_NODE]
    objective_terms = ObjectiveTerms(objective_terms_dict, constraint_terms_names)
    assert objective_terms.constraint_terms_names == constraint_terms_names
    assert dict(objective_terms) == objective_terms_dict

    # explicitly setting constraint terms names to [] is fine
    objective_terms2 = ObjectiveTerms(objective_terms_dict, [])
    assert objective_terms2.constraint_terms_names == []
    assert dict(objective_terms2) == objective_terms_dict
    assert objective_terms2 != objective_terms

    with pytest.warns(UserWarning, match="There is nothing in this ObjectiveTerms"):
        ObjectiveTerms()

def test_errors(objective_terms):
    """ test the errors """
    # pylint: disable=protected-access
    with pytest.warns(DeprecationWarning, match="This way of instantiation is deprecated"):
        ExampleObjectiveTerms(instance=ExampleInstance([(0, 1)], 1))
    objective_terms_dict = dict(objective_terms)
    with pytest.raises(NotImplementedError, match="Provide 'objective_terms' on initialization or "):
        ObjectiveTerms._get_objective_terms(None)
    with pytest.raises(NotImplementedError, match="Provide 'constraint_terms_names' on initialization or "):
        ObjectiveTerms._get_constraint_terms_names()
    with pytest.raises(ValueError, match="All constraint terms names should also be a key of the objective terms"):
        ObjectiveTerms(objective_terms_dict, ["wrong_constraint_name"])

def test_all_to_binary(objective_terms_different_types):
    """ test transformation of all terms to binary polynomials """
    objective_terms_binary = objective_terms_different_types.all_to_binary()
    exp_transformed_ising = PolyBinary({(): 6, (0,): -4, (0, 1): 8, (1,): -4, (2,): -8, (2, 3): 16, (3,): -8})
    assert isinstance(objective_terms_binary, ExampleObjectiveTerms)
    assert all(isinstance(poly, PolyBinary) for poly in objective_terms_binary.values())
    assert objective_terms_binary["binary"] == objective_terms_different_types["binary"]
    assert objective_terms_binary["none"] == objective_terms_different_types["none"]
    assert objective_terms_binary["ising"] == exp_transformed_ising

def test_all_to_ising(objective_terms_different_types):
    """ test conversion of all terms to Ising polynomials """
    # without inversion of ising
    objective_terms_ising = objective_terms_different_types.all_to_ising()
    assert isinstance(objective_terms_ising, ExampleObjectiveTerms)
    assert all(isinstance(poly, PolyIsing) for poly in objective_terms_ising.values())
    assert all(not poly.is_inverted() for poly in objective_terms_ising.values())

    # with inversion of ising
    objective_terms_ising = objective_terms_different_types.all_to_ising(inverted=True)
    assert isinstance(objective_terms_ising, ExampleObjectiveTerms)
    assert all(isinstance(poly, PolyIsing) for poly in objective_terms_ising.values())
    assert all(poly.is_inverted() for poly in objective_terms_ising.values())

def test_get_default_terms_weights(objective_terms):
    """ test the default weights """
    exp_weights = {"colored_edges": 1, "one_color_per_node": 1}
    assert objective_terms.get_default_terms_weights() == exp_weights

    exp_weights = {"colored_edges": 1, "one_color_per_node": 3}
    assert objective_terms.get_default_terms_weights(penalty_scale=3) == exp_weights

    exp_weights = {"colored_edges": 1, "one_color_per_node": 22}
    assert objective_terms.get_default_terms_weights(use_naive_bounds=True) == exp_weights

    exp_weights = {"colored_edges": 1, "one_color_per_node": 2}
    assert objective_terms.get_default_terms_weights(use_naive_bounds=True, penalty_scale=1/11) == exp_weights

def test_get_naive_terms_weights(objective_terms):
    """ test the naive weights """
    with pytest.raises(ValueError, match="Either provide ObjectiveTerms objects or the constraint terms names"):
        get_naive_terms_weights(dict(objective_terms))

    exp_naive_terms_weights = {"colored_edges": 1, "one_color_per_node": 22}
    assert get_naive_terms_weights(objective_terms) == exp_naive_terms_weights

    # check constraint for non-integer coefficients with factor 0.3
    constraint_poly = PolyBinary({((X, 1), (X, 2)): 1, ((X, 2),): -1.4, ((X, 1),): 5, ((X, 3),): 3})
    objective_terms["float_constraint"] = constraint_poly

    # the name of the constraint is not added to the constraint terms names, yet,
    # therefore is considered as objective and raises the error
    with pytest.raises(ValueError, match="Currently only one objective function is supported"):
        get_naive_terms_weights(objective_terms)
    objective_terms.constraint_terms_names.append("float_constraint")

    exp_naive_terms_weights = {"colored_edges": 1, "one_color_per_node": 22, "float_constraint":  55}
    assert get_naive_terms_weights(objective_terms) == exp_naive_terms_weights

    # remove objective function
    del objective_terms["colored_edges"]
    exp_naive_terms_weights = {"one_color_per_node": 1, "float_constraint": 1}
    assert get_naive_terms_weights(objective_terms) == exp_naive_terms_weights

def test_get_all_variables(objective_terms):
    """ test all variables """
    exp_variables = [(X, 1, B), (X, 1, G), (X, 1, R),
                     (X, 2, B), (X, 2, G), (X, 2, R),
                     (X, 3, B), (X, 3, G), (X, 3, R),
                     (X, 4, B), (X, 4, G), (X, 4, R),
                     (X, 5, B), (X, 5, G), (X, 5, R)]
    variables = objective_terms.get_all_variables()
    assert variables == exp_variables

def test_reduce():
    """ test reduction """
    term1 = PolyBinary({((X, 1), (X, 2), (X, 3)): 1, ((X, 1),) : -1})
    term2 = PolyBinary({((X, 2), (X, 3)): 2})
    objective_terms = ObjectiveTerms({"term1": term1, "term2": term2}, ["term1"])

    # has already only qubic polynomials
    reduced = objective_terms.reduce(3)
    assert reduced == objective_terms

    # only first term is reduced
    exp_reduction_term1 = PolyBinary({((REDUCTION, X, 1, X, 2),): 3,
                                      ((REDUCTION, X, 1, X, 2), (X, 1)): -2,
                                      ((REDUCTION, X, 1, X, 2), (X, 2)): -2,
                                      ((X, 1), (X, 2)): 1})
    exp_reduced_term1 = PolyBinary({((REDUCTION, X, 1, X, 2), (X, 3)): 1, ((X, 1),) : -1})
    exp_reduced = ObjectiveTerms({"term1": exp_reduced_term1, "term2": term2, "reduction_x_1_x_2": exp_reduction_term1},
                                 ["term1", "reduction_x_1_x_2"])
    reduced = objective_terms.reduce(single_penalty_term=False)
    assert reduced == exp_reduced

    # in the first step term1 is reduced, this is applied to term2, and afterwards term2 is further reduced
    term2 = PolyBinary({((X, 0), (X, 1), (X, 2), (X, 3)): 2})
    objective_terms = ObjectiveTerms({"term1": term1, "term2": term2}, ["term1"])

    exp_reduced_term2 = PolyBinary({((REDUCTION, REDUCTION, X, 1, X, 2, X, 0), (X, 3)): 2})
    exp_reduction_term2 = PolyBinary({((REDUCTION, REDUCTION, X, 1, X, 2, X, 0),): 3,
                                      ((REDUCTION, REDUCTION, X, 1, X, 2, X, 0), (X, 0)): -2,
                                      ((REDUCTION, REDUCTION, X, 1, X, 2, X, 0), (REDUCTION, X, 1, X, 2)): -2,
                                      ((REDUCTION, X, 1, X, 2), (X, 0)): 1})
    exp_reduction = exp_reduction_term1 + exp_reduction_term2
    exp_reduced = ObjectiveTerms({"term1": exp_reduced_term1, "term2": exp_reduced_term2, REDUCTION: exp_reduction},
                                 ["term1", REDUCTION])
    reduced = objective_terms.reduce()
    assert reduced == exp_reduced

    # check errors
    with pytest.raises(ValueError, match="Can only reduce to at least quadratic"):
        ObjectiveTerms({"term1": term1}, []).reduce(1)
    with pytest.raises(ValueError, match="Reduction is currently only implemented for binary polynomials"):
        ObjectiveTerms({"term1": PolyIsing()}, []).reduce()
