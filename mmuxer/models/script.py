import importlib
import logging
from typing import Dict

from imap_tools import MailMessage

from .common import BaseModel
from .condition import Condition

logger = logging.getLogger(__name__)


class Script(BaseModel):
    name: str
    condition: Condition
    module: str
    kwargs: Dict[str, str] = {}

    def apply(self, message: MailMessage, dry_run):
        if self.condition.eval(message):
            message = f"Executing {self.name}: {self.module}({self.kwargs})"
            if dry_run:
                logger.info("%s [DRY_RUN]", message)
            else:
                module = importlib.import_module(self.module)
                module.script(message, **self.kwargs)
