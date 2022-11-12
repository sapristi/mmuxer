from typing import Literal

from imap_tools import BaseMailBox, MailMessage

from .action import Action, MoveAction
from .common import BaseModel
from .condition import Condition


class GenericFilter(BaseModel):
    name: str
    type: Literal["generic"] = "generic"
    condition: Condition
    actions: list[Action]
    abort_next: bool = False

    def apply(self, mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
        if self.condition.eval(message):
            for action in self.actions:
                action.apply(mailbox, message, dry_run)
            return True
        return False

    def destinations(self):
        """List destination targets of move actions."""
        return [action.dest for action in self.actions if action.action == "move"]


class BatchMoveItem(BaseModel):
    condition: Condition
    dest: str
    mark_read: bool = False

    def apply(self, mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
        if self.condition.eval(message):
            MoveAction(dest=self.dest).apply(mailbox, message, dry_run)
            return True
        return False


class BatchMoveFilter(BaseModel):
    name: str
    type: Literal["batch_move"] = "batch_move"
    items: list[BatchMoveItem]
    abort_next: bool = False

    def apply(self, mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
        for item in self.items:
            item.apply(mailbox, message, dry_run)

    def destinations(self):
        """List destination targets of move actions."""
        return [item.dest for item in self.items]


Filter = GenericFilter | BatchMoveFilter


def parse_filter(filter_dict: dict):
    class FilterParser(BaseModel):
        __root__: Filter

    return FilterParser.parse_obj(filter_dict).__root__


def apply_list(filters: list[Filter], mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
    for f in filters:
        applied = f.apply(mailbox, message, dry_run)
        if applied and f.abort_next:
            break
