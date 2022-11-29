import logging
import os
import ssl
import sys
from pathlib import Path
from typing import List

import certifi
import yaml
from imap_tools import BaseMailBox, MailBox

from mmuxer.models.action import Action, ActionLoader, DeleteAction, FlagAction, MoveAction
from mmuxer.models.enums import Flag
from mmuxer.models.rule import Rule
from mmuxer.models.settings import Settings

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
    __slots__ = ("_settings", "_rules", "_mailbox", "_config_file", "actions")

    def __init__(self):
        self._settings = None
        self._rules = None
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
            logger.exception("Failed loading config file, check that the yaml syntax is valid.")
            raise

        if (
            not isinstance(config_dict, dict)
            or (config_dict.keys() - {"rules", "settings", "actions"}) != set()
            or "rules" not in config_dict
            or "settings" not in config_dict
        ):
            logger.error(
                "The config file should contain a mapping with the keys 'rules', 'settings' and 'actions' (optional)."
            )
            sys.exit(1)

        try:
            self._settings = Settings(**config_dict["settings"])
        except Exception as exc:
            logger.error("Failed parsing the 'settings' section of the configuration:")
            logger.error(exc)
            sys.exit(1)

        parsed_rules = []
        for rule_dict in config_dict["rules"]:
            try:
                parsed_rules.append(Rule.parse_obj(rule_dict))
            except Exception as exc:
                logger.error("Failed parsing the 'rules' section of the configuration:")
                logger.error(rule_dict)
                logger.error(exc)
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
                    self.actions[action_name] = ActionLoader.parse_obj(action_dict).__root__
                except Exception as exc:
                    logger.error("Failed parsing the 'actions' section of the configuration:")
                    logger.error(action_dict)
                    logger.error(exc)
                    sys.exit(1)
            self._rules = parsed_rules

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


state = State()
