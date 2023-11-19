from typing import List, Optional, Union

from imap_tools import BaseMailBox, MailMessage
from pydantic import Field

from .action import Action, MoveAction
from .common import BaseModel
from .condition import Condition
from .sieve import to_sieve_conditions


class Rule(BaseModel):
    name: Optional[str] = None
    condition: Condition
    move_to: Union[str, None] = None
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

    def to_sieve(self):
        if self.name:
            name = self.name
        elif self.move_to:
            name = self.move_to
        else:
            raise Exception("A rule must have a name to be converted to sieve rules")
        sieve_conditions = to_sieve_conditions(self.condition)
        sieve_actions = [action.to_sieve() for action in self._actions()]
        if not self.keep_evaluating:
            sieve_actions.append("stop")
        sieve_actions_str = "\n".join(f"  {action};" for action in sieve_actions)
        return [
            f"""
# rule:[{name}]
{sieve_conditions}
{{
{sieve_actions_str}
}}"""
        ]
        return [
            f"""
# rule:[{name}_{i}]
{sieve_condition}
{{
{sieve_actions_str}
}}"""
            for i, sieve_condition in enumerate(sieve_conditions)
        ]


def apply_list(rules: List[Rule], mailbox: BaseMailBox, message: MailMessage, dry_run: bool):
    for rule in rules:
        applied = rule.apply(mailbox, message, dry_run)
        if applied and not rule.keep_evaluating:
            break
