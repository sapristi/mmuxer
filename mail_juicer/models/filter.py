from imap_tools import BaseMailBox, MailMessage

from .action import Action
from .common import BaseModel
from .condition import Condition


class Filter(BaseModel):
    name: str
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

    @staticmethod
    def apply_list(filters: list["Filter"], mailbox: BaseMailBox, message: MailMessage):
        for f in filters:
            applied = f.apply(mailbox, message)
            if applied and f.abort_next:
                break
