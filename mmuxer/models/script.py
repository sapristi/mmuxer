import importlib
from typing import Dict

from imap_tools import MailMessage

from .common import BaseModel
from .condition import Condition


class Script(BaseModel):
    name: str
    condition: Condition
    module: str
    kwargs: Dict[str, str] = {}

    def apply(self, message: MailMessage):
        if self.condition.eval(message):
            print("Executing", self.name)
            module = importlib.import_module(self.module)
            module.script(message, **self.kwargs)
