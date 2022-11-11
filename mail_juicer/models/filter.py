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

    def apply(self, mailbox: BaseMailBox, message: MailMessage):
        if self.condition.eval(message):
            for action in self.actions:
                print(
                    message.date, message.subject, len(message.text or message.html), "->", action
                )
                action.apply(mailbox, message)
            return True
        return False


class BatchMoveItem(BaseModel):
    condition: Condition
    dest: str
    mark_read: bool = False

    def apply(self, mailbox: BaseMailBox, message: MailMessage):
        if self.condition.eval(message):
            MoveAction(dest=self.dest).apply(mailbox, message)
            return True
        return False


class BatchMoveFilter(BaseModel):
    name: str
    type: Literal["batch_move"] = "batch_move"
    items: list[BatchMoveItem]
    abort_next: bool = False

    def apply(self, mailbox: BaseMailBox, message: MailMessage):
        for item in self.items:
            item.apply(mailbox, message)


class Filter(BaseModel):
    __root__: GenericFilter | BatchMoveFilter

    @staticmethod
    def apply_list(filters: list["Filter"], mailbox: BaseMailBox, message: MailMessage):
        for f in filters:
            applied = f.__root__.apply(mailbox, message)
            if applied and f.__root__.abort_next:
                break
