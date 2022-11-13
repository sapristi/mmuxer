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


class From(IBaseCondition):
    FROM: str

    def get_value(self, message: MailMessage):
        return message.from_

    def get_operand(self) -> str:
        return self.FROM

    def __rich_repr__(self):
        yield self.operator.name, self.FROM


class To(IBaseCondition):
    TO: str

    def get_value(self, message: MailMessage):
        return message.to

    def get_operand(self) -> str:
        return self.TO

    def __rich_repr__(self):
        yield self.operator.name, self.TO


class Subject(IBaseCondition):
    SUBJECT: str

    def get_value(self, message: MailMessage):
        return message.subject

    def get_operand(self) -> str:
        return self.SUBJECT

    def __rich_repr__(self):
        yield self.operator.name, self.SUBJECT


BaseCondition = From | To | Subject

All = ForwardRef("All")  # type: ignore
Any = ForwardRef("Any")  # type: ignore
Not = ForwardRef("Not")  # type: ignore


class All(BaseModel):
    ALL: list[Union[BaseCondition, All, Any, Not]]

    def eval(self, message: MailMessage):
        return all(operand.eval(message) for operand in self.ALL)

    def __rich_repr__(self):
        for item in self.ALL:
            yield item


class Any(BaseModel):
    ANY: list[Union[BaseCondition, All, Any, Not]]

    def eval(self, message: MailMessage):
        return any(operand.eval(message) for operand in self.ANY)

    def __rich_repr__(self):
        for item in self.ANY:
            yield item


class Not(BaseModel):
    NOT: Union[BaseCondition, All, Any, Not]

    def eval(self, message: MailMessage):
        return not self.NOT.eval(message)


All.update_forward_refs()
Any.update_forward_refs()
Not.update_forward_refs()

Condition = Union[BaseCondition, All, Any, Not]
