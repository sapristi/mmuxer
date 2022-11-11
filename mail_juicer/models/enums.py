from enum import Enum


class ComparisonOperator(Enum):
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"


class MessageField(Enum):
    FROM_ = "FROM"
    TO = "TO"
    SUBJET = "SUBJECT"
    BODY = "TEXT"


class ConditionOperator(Enum):
    OR = "OR"
    AND = "AND"
    NOT = "NOT"


class Flag(Enum):
    SEEN = "SEEN"
    ANSWERED = "ANSWERED"
    FLAGGED = "FLAGGED"
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    RECENT = "RECENT"

    @property
    def imap(self):
        return "\\" + self.name.capitalize()
