import logging
from collections import Counter
from pathlib import Path

import typer
import yaml
from imap_tools import MailMessage
from pydantic import ValidationError

config_file_typer_option = typer.Option(
    Path("config.yaml"), exists=True, dir_okay=False, readable=True, resolve_path=True
)
logger = logging.getLogger(__name__)


def find_likely_error_location_and_message(exc: ValidationError):
    locations = [error["loc"] for error in exc.errors()]

    prefixes = [location[0 : i + 1] for location in locations for i in range(len(location))]
    longest_prefix = sorted((prefix for prefix in set(prefixes)), key=len)[-1]
    most_common_prefixes = Counter(prefixes).most_common()
    if most_common_prefixes[0][1] == 1:
        longest_prefix = longest_prefix

    else:
        longest_prefix = ()
        for prefix, count in Counter(prefixes).most_common():
            if count == 1:
                break
            if len(prefix) > len(longest_prefix):
                longest_prefix = prefix

    errors_with_loc = [error for error in exc.errors() if error["loc"] == longest_prefix]
    if len(errors_with_loc) == 1:
        message = errors_with_loc[0]["msg"]
    else:
        message = "could not parse"
    return longest_prefix, message


def get_from_keys_tuple(data, keys):
    if len(keys) == 0:
        return data
    key, *remaining_keys = keys
    if isinstance(data, dict) and not key in data:
        return "Missing field"
    return get_from_keys_tuple(data[key], remaining_keys)


def format_data(data):
    data_str = yaml.dump(data)
    return "╭\n" + "\n".join("│ " + line for line in data_str.splitlines()) + "\n╰"


class ParseException(Exception):
    def __init__(self, error_loc, bad_content, full_content, validation_error, message):
        self.error_loc = error_loc
        self.bad_content = bad_content
        self.full_content = full_content
        self.validation_error = validation_error
        self.message = message

    def format(self, desc_str):
        return (
            f"Failed parsing {desc_str}:\n"
            + format_data(self.full_content)
            + f"\nThe malformed configuration may come from '{self.message}' in\n"
            + format_data(self.bad_content)
        )

    @classmethod
    def from_validation_error(cls, exc: ValidationError, full_content):
        error_loc, message = find_likely_error_location_and_message(exc)
        if len(error_loc) == 0:
            bad_content = full_content
        elif isinstance(error_loc[-1], str):
            bad_content = {error_loc[-1]: get_from_keys_tuple(full_content, error_loc)}
        else:
            bad_content = get_from_keys_tuple(full_content, error_loc)

        return ParseException(
            error_loc=error_loc,
            bad_content=bad_content,
            full_content=full_content,
            validation_error=exc,
            message=message,
        )

    def __str__(self):
        return str(
            (
                self.error_loc,
                self.bad_content,
                self.full_content,
                self.validation_error,
                self.message,
            )
        )


def format_message(msg: MailMessage):
    return f"[{{{msg.uid}}} {msg.from_} -> {msg.to} '{msg.subject}']"
