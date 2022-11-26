from typing import List, Union

from imap_tools import BaseMailBox, MailMessage
from pydantic import Field

from .action import Action, MoveAction
from .common import BaseModel
from .condition import Condition


class Rule(BaseModel):
    condition: Condition
    move_to: Union[str, None]
    keep_evaluating: bool = False
    actions: List[Union[str, Action]] = Field(default_factory=list)

    def apply(self, mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
        if self.condition.eval(message):
            for action in self._actions():
                action.apply(mailbox, message, dry_run)
            return True
        return False

    def _actions(self) -> List[Action]:
        from ..config_state import state

        res = []
        for action in self.actions:
            if isinstance(action, str):
                res.append(state.actions[action])
            else:
                res.append(action)

        if self.move_to is not None:
            res.append(MoveAction(dest=self.move_to))
        return res

    def destinations(self):
        return [action.dest for action in self._actions() if action.action == "move"]


def apply_list(rules: List[Rule], mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
    for rule in rules:
        applied = rule.apply(mailbox, message, dry_run)
        if applied and not rule.keep_evaluating:
            break
