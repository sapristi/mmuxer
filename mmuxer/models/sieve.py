from typing import List, Literal, Union

import boolean

from mmuxer.models.common import BaseModel
from mmuxer.models.condition import All, Any, BaseCondition, Condition, Not, is_base_condition

algebra = boolean.BooleanAlgebra()
Clause = Union[algebra.Symbol, algebra.NOT, algebra.OR, algebra.AND]


def remove_singleton_conditions(condition: Condition) -> Condition:
    if is_base_condition(condition):
        return condition
    elif isinstance(condition, Not):
        return Not(NOT=remove_singleton_conditions(condition.NOT))
    elif isinstance(condition, Any):
        if len(condition.ANY) == 1:
            return remove_singleton_conditions(condition.ANY[0])
        else:
            return Any(ANY=[remove_singleton_conditions(cond) for cond in condition.ANY])
    elif isinstance(condition, All):
        if len(condition.ALL) == 1:
            return remove_singleton_conditions(condition.ALL[0])
        else:
            return All(ALL=[remove_singleton_conditions(cond) for cond in condition.ALL])


def parse_condition(condition: Condition) -> Clause:
    if is_base_condition(condition):
        return algebra.Symbol(condition)
    elif isinstance(condition, Not):
        return algebra.NOT(parse_condition(condition.NOT))
    elif isinstance(condition, Any):
        return algebra.OR(*(parse_condition(cond) for cond in condition.ANY))
    elif isinstance(condition, All):
        return algebra.AND(*(parse_condition(cond) for cond in condition.ALL))


def to_condition(expression: Clause) -> Condition:
    if isinstance(expression, algebra.Symbol):
        return expression.obj
    if isinstance(expression, algebra.NOT):
        return Not(NOT=to_condition(expression.args[0]))
    elif isinstance(expression, algebra.AND):
        return All(ALL=[to_condition(e) for e in expression.args])
    elif isinstance(expression, algebra.OR):
        return Any(ANY=[to_condition(e) for e in expression.args])
    else:
        raise Exception(f"Unexpected expression {expression}")


def to_dnf(condition: Condition):
    normalized_condition = remove_singleton_conditions(condition)
    clause = parse_condition(normalized_condition)
    dnf_clause = algebra.normalize(clause, algebra.OR)
    return to_condition(dnf_clause)


#
def depth(condition: Condition) -> int:
    """We expect the condition to be in normal form, with Not only
    applied to BaseConditions"""
    if is_base_condition(condition) or isinstance(condition, Not):
        return 0
    elif isinstance(condition, Any):
        return 1 + max(depth(cond) for cond in condition.ANY)
    elif isinstance(condition, All):
        return 1 + max(depth(cond) for cond in condition.ALL)


class SieveCondition(BaseModel):
    type: Union[Literal["allof"], Literal["anyof"]]
    conditions: List[Union[BaseCondition, Not]]

    def dump(self):
        conditions_to_sieve = ", ".join(condition.to_sieve() for condition in self.conditions)
        return f"if {self.type} ({conditions_to_sieve})"


def to_sieve_conditions_flat(condition: Condition) -> List[SieveCondition]:
    condition_dnf = to_dnf(condition)
    if is_base_condition(condition_dnf) or isinstance(condition_dnf, Not):
        return [SieveCondition(type="anyof", conditions=[condition_dnf])]
    elif isinstance(condition_dnf, All):
        return [SieveCondition(type="allof", conditions=condition_dnf.ALL)]
    elif isinstance(condition_dnf, Any):
        first_level_conds = [cond for cond in condition_dnf.ANY if depth(cond) == 0]
        second_level_conds = [cond for cond in condition_dnf.ANY if depth(cond) == 1]
        # When in dnf, conditions of level 1 are All conditions
        assert all(isinstance(all_conds, All) for all_conds in second_level_conds)

        res = []
        if first_level_conds:
            res.append(SieveCondition(type="anyof", conditions=first_level_conds))
        if second_level_conds:
            res.extend(
                SieveCondition(type="allof", conditions=all_conds.ALL)
                for i, all_conds in enumerate(second_level_conds)
            )
        return res
    else:
        raise Exception(f"Unexpected condition {condition_dnf}")


def to_sieve_condition_rec(condition: Condition, indent_n: int) -> str:
    indent = "  " * indent_n
    if isinstance(condition, Not):
        inner = to_sieve_condition_rec(condition.NOT, indent_n)
        return f"not {inner}"
    if isinstance(condition, All):
        inner_conds = (to_sieve_condition_rec(cond, indent_n + 1) for cond in condition.ALL)
        inner = f",\n".join(inner_conds)
        return f"{indent}allof (\n{inner}\n{indent})"
    if isinstance(condition, Any):
        inner_conds = (to_sieve_condition_rec(cond, indent_n + 1) for cond in condition.ANY)
        inner = f",\n".join(inner_conds)
        return f"{indent}anyof (\n{inner}\n{indent})"

    return f"{indent}{condition.to_sieve()}"


def to_sieve_conditions(condition: Condition) -> str:
    return "if " + to_sieve_condition_rec(condition, 0)
