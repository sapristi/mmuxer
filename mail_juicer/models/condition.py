from typing import ForwardRef, Union

from imap_tools import MailMessage

from .common import BaseModel
from .enums import ComparisonOperator, ConditionOperator, MessageField


class ConditionBase(BaseModel):
    field: MessageField
    operator: ComparisonOperator
    operand: str

    def eval(self, message: MailMessage):
        value = getattr(message, self.field.name.lower())
        match self.operator:
            case ComparisonOperator.CONTAINS:
                return self.operand in value
            case ComparisonOperator.EQUALS:
                return self.operand == value


ConditionComposed = ForwardRef("ConditionComposed")  # type: ignore


class ConditionComposed(BaseModel):
    operator: ConditionOperator
    operands: list[Union[ConditionComposed, ConditionBase]]

    def eval(self, message: MailMessage):
        match self.operator:
            case ConditionOperator.OR:
                return any(operand.eval(message) for operand in self.operands)
            case ConditionOperator.AND:
                return all(operand.eval(message) for operand in self.operands)
            case ConditionOperator.NOT:
                return not (self.operands[0].eval(message))


ConditionComposed.update_forward_refs()

Condition = ConditionBase | ConditionComposed
