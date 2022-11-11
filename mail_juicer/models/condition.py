from typing import ForwardRef, Union

from imap_tools import MailMessage

from .common import BaseModel
from .enums import ComparisonOperator, MessageField


class BaseCondition(BaseModel):
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


AndCondition = ForwardRef("AndCondition")  # type: ignore
OrCondition = ForwardRef("OrCondition")  # type: ignore
NotCondition = ForwardRef("NotCondition")  # type: ignore


class AndCondition(BaseModel):
    AND: list[Union[BaseCondition, AndCondition, OrCondition, NotCondition]]

    def eval(self, message: MailMessage):
        return all(operand.eval(message) for operand in self.AND)


class OrCondition(BaseModel):
    OR: list[Union[BaseCondition, AndCondition, OrCondition, NotCondition]]

    def eval(self, message: MailMessage):
        return any(operand.eval(message) for operand in self.OR)


class NotCondition(BaseModel):
    NOT: Union[BaseCondition, AndCondition, OrCondition, NotCondition]

    def eval(self, message: MailMessage):
        return not self.NOT.eval(message)


AndCondition.update_forward_refs()
OrCondition.update_forward_refs()
NotCondition.update_forward_refs()

Condition = Union[BaseCondition, AndCondition, OrCondition, NotCondition]
