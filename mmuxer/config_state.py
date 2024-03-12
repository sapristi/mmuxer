import logging
import os
import ssl
import sys
from pathlib import Path
from typing import List

import certifi
import yaml
from imap_tools.mailbox import BaseMailBox

from mmuxer.mailbox import MailBox
from mmuxer.models.action import Action, ActionLoader, DeleteAction, FlagAction, MoveAction
from mmuxer.models.enums import Flag
from mmuxer.models.rule import Rule
from mmuxer.models.script import PythonScript
from mmuxer.models.settings import Settings
from mmuxer.utils import ParseException

logger = logging.getLogger(__name__)


def make_ssl_context(ssl_ciphers):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if ssl_ciphers is not None:
        context.set_ciphers(ssl_ciphers)
    context.load_verify_locations(
        cafile=os.path.relpath(certifi.where()), capath=None, cadata=None
    )
    return context


default_actions = {
    "delete": DeleteAction(),
    "trash": MoveAction(dest="Trash"),
    "mark_read": FlagAction(flag=Flag.SEEN),
}


class State:
    __slots__ = ("_settings", "_rules", "_scripts", "_mailbox", "_config_file", "actions")

    def __init__(self):
        self._settings = None
        self._rules = None
        self._scripts = None
        self._mailbox = None
        self._config_file = None
        self.actions: dict[str, Action] = default_actions

    def load_config_file(self, config_file: Path):
        logger.info("Loading config from %s", config_file)
        self._config_file = config_file
        self._parse_config_file()

    def reload_config_file(self):
        current_state = {key: getattr(self, key) for key in self.__slots__}
        try:
            self._parse_config_file()
        except Exception:
            logger.error("Failed loading new configuration, reverting to previous configuration.")
            for key, value in current_state.items():
                setattr(self, key, value)
            return
        logger.info("Succesfuly parsed new configuration.")

    def create_mailbox(self):
        logger.debug(f"Connecting to {self.settings.server} with {self.settings.username}")
        ssl_context = make_ssl_context(self.settings.ssl_ciphers)
        self._mailbox = MailBox(self.settings.server, ssl_context=ssl_context).login(
            self.settings.username, self.settings.password
        )
        logger.info(f"Connected to {self.settings.server} with {self.settings.username}")

    def _parse_config_file(self):
        config_raw = self.config_file.read_text()
        try:
            config_dict = yaml.safe_load(config_raw)
        except Exception:
            logger.error("The config file is not valid yaml, check that the yaml syntax is valid.")
            exit(1)

        if not isinstance(config_dict, dict) or not "settings" in config_dict:
            logger.error("The config should be mapping. 'settings' is a required key")
            exit(1)

        all_keys = {"rules", "actions", "scripts", "settings"}
        extra_keys = config_dict.keys() - all_keys
        if extra_keys:
            logger.warning(f"The following keys in the config are not recognized: {extra_keys}")

        try:
            self._settings = Settings.parse_data(config_dict["settings"])
        except ParseException as exc:
            logger.error(exc.format("the 'settings' section of the configuration"))

            sys.exit(1)

        parsed_rules = []
        for rule_dict in config_dict["rules"]:
            try:
                parsed_rules.append(Rule.parse_data(rule_dict))
            except ParseException as exc:
                logger.error(exc.format("the following rules entry"))
                sys.exit(1)
        self._rules = parsed_rules

        if "actions" in config_dict:
            if not isinstance(config_dict["actions"], dict):
                logger.error(f"'actions' value is not a mapping: {config_dict['actions']}")
                sys.exit(1)
            for action_name, action_dict in config_dict["actions"].items():
                if action_name in self.actions:
                    logger.warning(f"Overriding default action f{action_name}")
                try:
                    self.actions[action_name] = ActionLoader.parse_data(action_dict).__root__
                except ParseException as exc:
                    logger.error(exc.format("the following action entry"))
                    sys.exit(1)
            self._rules = parsed_rules

        self._scripts = []
        for script_data in config_dict.get("scripts", []):
            try:
                self._scripts.append(PythonScript.parse_data(script_data))
            except ParseException as exc:
                logger.error(exc.format("the following script entry"))
                exit(1)

    @property
    def config_file(self) -> Path:
        if self._config_file is None:
            raise Exception("Uninitialized config_file")
        return self._config_file

    @property
    def settings(self) -> Settings:
        if self._settings is None:
            raise Exception("Uninitialized settings")
        return self._settings

    @property
    def rules(self) -> List[Rule]:
        if self._rules is None:
            raise Exception("Uninitialized rules")
        return self._rules

    @property
    def mailbox(self) -> BaseMailBox:
        if self._mailbox is None:
            raise Exception("Uninitialized mailbox")
        return self._mailbox

    @property
    def scripts(self) -> List[PythonScript]:
        if self._scripts is None:
            raise Exception("Uninitialized rules")
        return self._scripts


state = State()
