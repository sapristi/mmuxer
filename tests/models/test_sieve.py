import pytest

from mmuxer.models.condition import All, Any, From, Not
from mmuxer.models.sieve import parse_condition, to_condition, to_dnf, to_sieve_conditions

cond1 = From(FROM="1")
cond2 = From(FROM="2")
cond3 = From(FROM="3")


@pytest.mark.parametrize(
    "condition",
    (
        cond1,
        cond2,
        Not(NOT=cond1),
        All(ALL=[cond1, Not(NOT=cond2)]),
        Any(ANY=[cond1, Not(NOT=cond2)]),
        Not(NOT=Any(ANY=[cond1, Not(NOT=cond2)])),
    ),
)
def test_convert_condition(condition):
    expr = parse_condition(condition)
    assert to_condition(expr) == condition


@pytest.mark.parametrize(
    "condition, expected",
    (
        (cond1, cond1),
        (Not(NOT=cond1), Not(NOT=cond1)),
        (Any(ANY=[cond1, cond2]), Any(ANY=[cond1, cond2])),
        (Any(ANY=[cond1, Not(NOT=cond2)]), Any(ANY=[cond1, Not(NOT=cond2)])),
        (All(ALL=[cond1, Not(NOT=cond2)]), All(ALL=[cond1, Not(NOT=cond2)])),
        (Any(ANY=[cond1, All(ALL=[cond2, cond3])]), Any(ANY=[cond1, All(ALL=[cond2, cond3])])),
        (
            All(ALL=[cond1, Any(ANY=[cond2, cond3])]),
            Any(
                ANY=[
                    All(ALL=[cond1, cond2]),
                    All(ALL=[cond1, cond3]),
                ]
            ),
        ),
        (
            Not(NOT=All(ALL=[cond1, Any(ANY=[cond2, cond3])])),
            Any(
                ANY=[
                    Not(NOT=cond1),
                    All(ALL=[Not(NOT=cond2), Not(NOT=cond3)]),
                ]
            ),
        ),
        (
            All(ALL=[cond1, Not(NOT=cond2), All(ALL=[cond3])]),
            All(ALL=[cond1, Not(NOT=cond2), cond3]),
        ),
        (
            All(ALL=[cond1, Not(NOT=cond2), All(ALL=[cond3, cond3])]),
            All(ALL=[cond1, Not(NOT=cond2), cond3]),
        ),
    ),
)
def test_to_dnf(condition, expected):
    dnf = to_dnf(condition)
    assert dnf == expected


@pytest.mark.parametrize(
    "condition",
    (
        (cond1),
        (Not(NOT=cond1)),
        (Any(ANY=[cond1, cond2])),
        (Any(ANY=[cond1, Not(NOT=cond2)])),
        (All(ALL=[cond1, Not(NOT=cond2)])),
        (Any(ANY=[cond1, All(ALL=[cond2, cond3])])),
        (All(ALL=[cond1, Any(ANY=[cond2, cond3])])),
        (Not(NOT=All(ALL=[cond1, Any(ANY=[cond2, cond3])]))),
        (All(ALL=[cond1, Not(NOT=cond2), All(ALL=[cond3])])),
        (All(ALL=[cond1, Not(NOT=cond2), All(ALL=[cond3, cond3])])),
    ),
)
def test_to_sieve_rules(condition):
    to_sieve_conditions(condition)
