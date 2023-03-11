import importlib
import importlib.util
import logging
import sys
from typing import Any, Dict

from imap_tools import MailMessage
from pydantic import PrivateAttr

from mmuxer.utils import format_message

from .common import BaseModel
from .condition import Condition

logger = logging.getLogger(__name__)


# https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
class PythonScript(BaseModel):
    name: str
    script_path: str
    entrypoint: str
    condition: Condition
    kwargs: Dict[str, Any] = {}
    _callable: Any = PrivateAttr()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._callable = self._load_callable()
        except Exception:
            logger.exception(f"Failed loading code for script {self.name}")
            sys.exit(1)

    def apply(self, message: MailMessage, dry_run):
        if self.condition.eval(message):
            log_message = f"Executing script {self.name} for {format_message(message)}"
            if dry_run:
                logger.info("%s [DRY_RUN]", log_message)
            else:
                logger.info(log_message)
                try:
                    self._callable(message, **self.kwargs, logger=logger)
                except Exception:
                    logger.exception(f"Script {self.name} execution failed.")

    def _load_callable(self):
        spec = importlib.util.spec_from_file_location(self.name, self.script_path)
        if spec is None:
            raise Exception(f"Could not find python module to load at '{self.script_path}")

        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)

        entrypoint = getattr(script_module, self.entrypoint, None)
        if entrypoint is None:
            raise Exception(
                f"Could not find a function '{self.entrypoint}' in '{self.script_path}'."
            )
        return entrypoint
