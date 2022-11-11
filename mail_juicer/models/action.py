from typing import Literal

from imap_tools import BaseMailBox, MailMessage

from .common import BaseModel
from .enums import Flag


class MoveAction(BaseModel):
    action: Literal["move"] = "move"
    dest: str
    create_if_not_exists: bool = False

    def apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.move(message.uid, self.dest)


class DeleteAction(BaseModel):
    action: Literal["delete"] = "delete"

    def apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.delete([message.uid])


class FlagAction(BaseModel):
    action: Literal["flag"] = "flag"
    flag: Flag

    def apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.flag([message.uid], flag_set={self.flag.imap}, value=True)


class UnflagAction(BaseModel):
    action: Literal["flag"] = "flag"
    flag: Flag

    def apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.flag([message.uid], flag_set={self.flag.imap}, value=False)


Action = MoveAction | DeleteAction | FlagAction | UnflagAction
