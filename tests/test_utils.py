from pydantic import BaseModel, ValidationError

from mmuxer.models.condition import Condition
from mmuxer.utils import ParseException, find_likely_error_location_and_message


def test_find_likely_error_location_single_error():
    class M(BaseModel):
        a: str
        b: int

    data = {"a": "ok"}
    try:
        M.parse_obj(data)
    except ValidationError as exc:
        location, message = find_likely_error_location_and_message(exc)
        assert location == ("b",)
        assert message == "field required"


def test_find_likely_error_location_multiple_errors():
    class M(BaseModel):
        a: str
        b: int

    data = {}
    try:
        M.parse_obj(data)
    except ValidationError as exc:
        location, message = find_likely_error_location_and_message(exc)
        assert location == ("b",) or location == ("a",)
        assert message == "field required"


def test_find_likely_error_location_unions():
    data = {
        "condition": {
            "ALL": [
                {"FROM": "ok"},
                {"SUBECT": "ok"},
            ]
        }
    }

    class M(BaseModel):
        condition: Condition

    try:
        M.parse_obj(data)
    except ValidationError as exc:
        location, message = find_likely_error_location_and_message(exc)
        assert location == ("condition", "ALL", 1, "SUBECT")
        assert message == "could not parse"
        parse_exception = ParseException.from_validation_error(exc, data)
        assert parse_exception.bad_content == {"SUBECT": "ok"}


def test_find_likely_error_location_unions_multiple_errors():
    data = {"condition": {"ALL": [{"SUBECT": "ok"}, {"SENDER": "ok"}, {"ANY": ["test", "okok"]}]}}

    class M(BaseModel):
        condition: Condition

    try:
        M.parse_obj(data)
    except ValidationError as exc:
        location, message = find_likely_error_location_and_message(exc)
        assert location == ("condition", "ALL", 2, "ANY", 0)
        assert message == "could not parse"
        parse_exception = ParseException.from_validation_error(exc, data)
        assert parse_exception.bad_content == "test"


def test_find_likely_error_location_unions_multiple_errors_bis():
    data = {"condition": {"ALL": [{"SUBECT": "ok"}, {"SENDER": "ok"}, {"ANY": [{}, "okok"]}]}}

    class M(BaseModel):
        condition: Condition

    try:
        M.parse_obj(data)
    except ValidationError as exc:
        location, message = find_likely_error_location_and_message(exc)
        assert message == "could not parse"
        assert location == ("condition", "ALL", 2, "ANY", 0)
        parse_exception = ParseException.from_validation_error(exc, data)
        assert parse_exception.bad_content == {}
