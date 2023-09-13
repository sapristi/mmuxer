from enum import Enum


class ComparisonOperator(Enum):
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"

    @property
    def sieve(self):
        if self == ComparisonOperator.CONTAINS:
            return ":contains"
        if self == ComparisonOperator.EQUALS:
            return ":is"
        raise Exception(f"Unhandled operator {self}")

    def eval(self, operand: str, value: str) -> bool:
        if self == ComparisonOperator.CONTAINS:
            return operand.lower() in value.lower()
        if self == ComparisonOperator.EQUALS:
            return operand.lower() == value.lower()
        raise Exception(f"Unhandled operator {self}")


class Flag(Enum):
    SEEN = "SEEN"
    ANSWERED = "ANSWERED"
    FLAGGED = "FLAGGED"
    DELETED = "DELETED"
    DRAFT = "DRAFT"

    @property
    def imap(self):
        return "\\" + self.name.capitalize()

    @property
    def sieve(self):
        return "\\\\" + self.name.capitalize()
