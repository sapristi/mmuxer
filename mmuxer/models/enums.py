from enum import Enum


class ComparisonOperator(Enum):
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"

    @property
    def sieve(self):
        if self.name == "CONTAINS":
            return ":contains"
        if self.name == "EQUALS":
            return ":is"


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
