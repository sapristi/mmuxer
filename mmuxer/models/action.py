import logging
from abc import abstractmethod
from typing import Literal, Union

from imap_tools import BaseMailBox, MailMessage
from pydantic import RootModel

from mmuxer.utils import format_message

from .common import BaseModel
from .enums import Flag

logger = logging.getLogger(__name__)


class BaseAction(BaseModel):
    @abstractmethod
    def _apply(self, mailbox: BaseMailBox, message: MailMessage) -> None:
        """Implementation of the action"""
        pass

    @abstractmethod
    def format(self, message) -> str:
        """Used to print information in terminal"""
        pass

    def skip(self, message) -> bool:
        """Custom function to skip action in certain conditions"""
        return False

    def apply(self, mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
        if self.skip(message):
            logger.debug("SKIP %s", self.format(message))
            return
        if dry_run:
            logger.info("%s [DRY_RUN]", self.format(message))
        else:
            logger.info(self.format(message))
            self._apply(mailbox, message)

    @abstractmethod
    def to_sieve(self) -> str:
        """Used to render sieve files"""


class MoveAction(BaseAction):
    action: Literal["move"] = "move"
    dest: str

    def skip(self, message):
        return getattr(message, "associated_folder", None) == self.dest

    def _apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.move(message.uid, self.dest)

    def format(self, message):
        return f"MOVE {format_message(message)} --> {self.dest}"

    def to_sieve(self):
        from mmuxer.config_state import state

        dest = state.settings.sieve_folder_prefix + self.dest.replace(
            "/", state.settings.sieve_folder_separator
        )
        return f'fileinto "{dest}"'


class DeleteAction(BaseAction):
    action: Literal["delete"] = "delete"

    def _apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.delete([message.uid])

    def format(self, message):
        return f"DELETE {format_message(message)}"

    def to_sieve(self):
        return "discard"


class FlagAction(BaseAction):
    action: Literal["flag"] = "flag"
    flag: Flag

    def _apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.flag([message.uid], flag_set={self.flag.imap}, value=True)

    def format(self, message):
        return f"FLAG {format_message(message)} {self.flag.name}"

    def to_sieve(self):
        return f'setflag "{self.flag.sieve}"'


class UnflagAction(BaseAction):
    action: Literal["flag"] = "flag"
    flag: Flag

    def _apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.flag([message.uid], flag_set={self.flag.imap}, value=False)

    def format(self, message):
        return f"UNFLAG {format_message(message)} {self.flag.name}"

    def to_sieve(self):
        return f'removeflag "{self.flag.sieve}"'


Action = Union[MoveAction, DeleteAction, FlagAction, UnflagAction]
ActionLoader = RootModel[Action]
