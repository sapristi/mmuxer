from abc import abstractmethod
from typing import ForwardRef, Union

from imap_tools import MailMessage

from .common import BaseModel
from .enums import ComparisonOperator


class IBaseCondition(BaseModel):
    operator: ComparisonOperator = ComparisonOperator.CONTAINS

    @abstractmethod
    def get_value(self, message: MailMessage) -> str:
        pass

    @abstractmethod
    def get_operand(self) -> str:
        pass

    def eval(self, message: MailMessage):
        value = self.get_value(message)
        match self.operator:
            case ComparisonOperator.CONTAINS:
                return self.get_operand() in value
            case ComparisonOperator.EQUALS:
                return self.get_operand() == value


class FromBaseCondition(IBaseCondition):
    FROM: str

    def get_value(self, message: MailMessage):
        return message.from_

    def get_operand(self) -> str:
        return self.FROM


class ToBaseCondition(IBaseCondition):
    TO: str

    def get_value(self, message: MailMessage):
        return message.to

    def get_operand(self) -> str:
        return self.TO


class SubjectBaseCondition(IBaseCondition):
    SUBJECT: str

    def get_value(self, message: MailMessage):
        return message.subject

    def get_operand(self) -> str:
        return self.SUBJECT


BaseCondition = FromBaseCondition | ToBaseCondition | SubjectBaseCondition

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
