import importlib
import logging
from typing import Dict, Literal

from imap_tools import MailMessage

from .common import BaseModel
from .condition import Condition

logger = logging.getLogger(__name__)


class PythonScript(BaseModel):
    type: Literal["python"] = "python"
    module_path: str
    module: str
    condition: Condition
    kwargs: Dict[str, str] = {}

    def apply(self, message: MailMessage, dry_run):
        if self.condition.eval(message):
            log_message = f"Executing {self.module_path}: {self.module}({self.kwargs})"
            if dry_run:
                logger.info("%s [DRY_RUN]", log_message)
            else:
                logger.info(log_message)
                module = importlib.import_module(self.module)
                module.script(message, **self.kwargs)
