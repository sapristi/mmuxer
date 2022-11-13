from enum import Enum


class ComparisonOperator(Enum):
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"


class Flag(Enum):
    SEEN = "SEEN"
    ANSWERED = "ANSWERED"
    FLAGGED = "FLAGGED"
    DELETED = "DELETED"
    DRAFT = "DRAFT"

    @property
    def imap(self):
        return "\\" + self.name.capitalize()
