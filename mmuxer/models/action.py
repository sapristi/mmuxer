import logging
from abc import abstractmethod
from typing import Literal, Union

from imap_tools import BaseMailBox, MailMessage
from pydantic import RootModel, model_validator

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

        dest = state.settings.sieve.folder_prefix + self.dest.replace(
            "/", state.settings.sieve.folder_separator
        )
        return f'fileinto "{dest}"'

    def __rich_repr__(self):
        yield "destination", self.dest


class DeleteAction(BaseAction):
    action: Literal["delete"] = "delete"

    def _apply(self, mailbox: BaseMailBox, message: MailMessage):
        mailbox.delete([message.uid])

    def format(self, message):
        return f"DELETE {format_message(message)}"

    def to_sieve(self):
        return "discard"

    def __rich_repr__(self):
        pass


class FlagAction(BaseAction):
    action: Literal["flag"] = "flag"
    flag: Flag | None = None
    custom_flag: str | None = None

    @model_validator(mode="after")
    def validate_flag_fields(self):
        """Ensure that either flag or custom_flag is set, but not both."""
        if self.flag is None and self.custom_flag is None:
            raise ValueError("Either 'flag' or 'custom_flag' must be set")
        if self.flag is not None and self.custom_flag is not None:
            raise ValueError("Only one of 'flag' or 'custom_flag' can be set, not both")
        return self

    def _apply(self, mailbox: BaseMailBox, message: MailMessage):
        flag_name = self.flag.imap if self.flag else self.custom_flag
        mailbox.flag([message.uid], flag_set={flag_name}, value=True)

    def format(self, message):
        flag_display = self.flag.name if self.flag else self.custom_flag
        return f"FLAG {format_message(message)} {flag_display}"

    def to_sieve(self):
        flag_name = self.flag.sieve if self.flag else self.custom_flag
        return f'setflag "{flag_name}"'

    def __rich_repr__(self):
        if self.flag:
            yield self.flag
        if self.custom_flag:
            yield self.custom_flag


class UnflagAction(BaseAction):
    action: Literal["unflag"] = "unflag"
    flag: Flag | None = None
    custom_flag: str | None = None

    @model_validator(mode="after")
    def validate_flag_fields(self):
        """Ensure that either flag or custom_flag is set, but not both."""
        if self.flag is None and self.custom_flag is None:
            raise ValueError("Either 'flag' or 'custom_flag' must be set")
        if self.flag is not None and self.custom_flag is not None:
            raise ValueError("Only one of 'flag' or 'custom_flag' can be set, not both")
        return self

    def _apply(self, mailbox: BaseMailBox, message: MailMessage):
        flag_name = self.flag.imap if self.flag else self.custom_flag
        mailbox.flag([message.uid], flag_set={flag_name}, value=False)

    def format(self, message):
        flag_display = self.flag.name if self.flag else self.custom_flag
        return f"UNFLAG {format_message(message)} {flag_display}"

    def to_sieve(self):
        flag_name = self.flag.sieve if self.flag else self.custom_flag
        return f'removeflag "{flag_name}"'

    def __rich_repr__(self):
        if self.flag:
            yield self.flag
        if self.custom_flag:
            yield self.custom_flag


Action = Union[MoveAction, DeleteAction, FlagAction, UnflagAction]
ActionLoader = RootModel[Action]
