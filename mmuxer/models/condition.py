import logging
from abc import abstractmethod
from typing import ForwardRef, List, Union

from imap_tools import MailMessage

from .common import BaseModel
from .enums import ComparisonOperator


class IBaseCondition(BaseModel):
    class Config:
        frozen = True

    operator: ComparisonOperator = ComparisonOperator.CONTAINS

    @abstractmethod
    def get_value(self, message: MailMessage) -> str:
        """Extract value from the message, used as value to which the rule is applied to."""
        pass

    @abstractmethod
    def get_operand(self) -> str:
        """Used to have a common function returning the operand of the rule across subclasses."""
        pass

    def eval(self, message: MailMessage) -> bool:
        """Evaluate the rule"""
        value = self.get_value(message)
        logging.debug("Eval %s <%s> %s", self.get_operand(), self.operator, value)
        if self.operator == ComparisonOperator.CONTAINS:
            return self.get_operand().lower() in value.lower()
        if self.operator == ComparisonOperator.EQUALS:
            return self.get_operand().lower() == value.lower()
        raise Exception(f"Unhandled operator {self.operator}")

    def to_sieve(self) -> str:
        """Used to render sieve files
        We include here the one used for header conditions
        """
        return f'header {self.operator.sieve} "{self.__class__.__name__}" "{self.get_operand()}'

    def __lt__(self, other):
        """Comparison: used for using with boolean.py"""
        return repr(self).__lt__(repr(other))


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
        return " ".join(message.to)

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


class Body(IBaseCondition):
    BODY: str

    def get_value(self, message: MailMessage):
        return message.text + message.html

    def get_operand(self) -> str:
        return self.BODY

    def __rich_repr__(self):
        yield self.operator.name, self.BODY

    def to_sieve(self) -> str:
        """Used to render sieve files"""
        return f'body :text {self.operator.sieve} "{self.get_operand()}'


BaseCondition = Union[From, To, Subject]


def is_base_condition(obj):
    """Useful for isinstance tests with python < 3.10"""
    return isinstance(obj, From) or isinstance(obj, To) or isinstance(obj, Subject)


All = ForwardRef("All")  # type: ignore
Any = ForwardRef("Any")  # type: ignore
Not = ForwardRef("Not")  # type: ignore


class All(BaseModel):
    ALL: List[Union[BaseCondition, All, Any, Not]]

    def eval(self, message: MailMessage):
        return all(operand.eval(message) for operand in self.ALL)

    def __rich_repr__(self):
        for item in self.ALL:
            yield item


class Any(BaseModel):
    ANY: List[Union[BaseCondition, All, Any, Not]]

    def eval(self, message: MailMessage):
        return any(operand.eval(message) for operand in self.ANY)

    def __rich_repr__(self):
        for item in self.ANY:
            yield item


class Not(BaseModel):
    NOT: Union[BaseCondition, All, Any, Not]

    def eval(self, message: MailMessage):
        return not self.NOT.eval(message)

    def to_sieve(self) -> str:
        """Used to render sieve files"""
        return f"not {self.NOT.to_sieve()}"


All.update_forward_refs()
Any.update_forward_refs()
Not.update_forward_refs()

Condition = Union[BaseCondition, All, Any, Not]
