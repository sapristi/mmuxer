import pytest
from pydantic import BaseModel, ValidationError

from mmuxer.models.condition import Condition
from mmuxer.utils import ParseException, find_likely_error_location_and_message


def test_find_likely_error_location_single_error():
    class M(BaseModel):
        a: str
        b: int

    data = {"a": "ok"}
    with pytest.raises(ValidationError) as exc_info:
        M.model_validate(data)
    location, message = find_likely_error_location_and_message(exc_info.value)
    assert location == ("b",)
    assert message == "Field required"


def test_find_likely_error_location_multiple_errors():
    class M(BaseModel):
        a: str
        b: int

    data = {}
    with pytest.raises(ValidationError) as exc_info:
        M.model_validate(data)
    location, message = find_likely_error_location_and_message(exc_info.value)
    assert location == ("b",) or location == ("a",)
    assert message == "Field required"


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

    with pytest.raises(ValidationError) as exc_info:
        M.model_validate(data)

    location, message = find_likely_error_location_and_message(exc_info.value)
    assert location == ("condition", "All", "ALL", 1, "From")
    assert message == "could not parse"

    parse_exception = ParseException.from_validation_error(exc_info.value, data)
    assert parse_exception.bad_content == {"From": "Missing field"}


def test_find_likely_error_location_unions_multiple_errors():
    data = {"condition": {"ALL": [{"SUBECT": "ok"}, {"SENDER": "ok"}, {"ANY": ["test", "okok"]}]}}

    class M(BaseModel):
        condition: Condition

    with pytest.raises(ValidationError) as exc_info:
        M.model_validate(data)

    location, message = find_likely_error_location_and_message(exc_info.value)
    assert location == ("condition", "All", "ALL", 2, "Any", "ANY", 0)
    assert message == "could not parse"
    parse_exception = ParseException.from_validation_error(exc_info.value, data)
    assert parse_exception.bad_content == "Missing field"


def test_find_likely_error_location_unions_multiple_errors_bis():
    data = {"condition": {"ALL": [{"SUBECT": "ok"}, {"SENDER": "ok"}, {"ANY": [{}, "okok"]}]}}

    class M(BaseModel):
        condition: Condition

    with pytest.raises(ValidationError) as exc_info:
        M.model_validate(data)

    location, message = find_likely_error_location_and_message(exc_info.value)
    assert message == "could not parse"
    assert location == ("condition", "All", "ALL", 2, "Any", "ANY", 0)
    parse_exception = ParseException.from_validation_error(exc_info.value, data)
    assert parse_exception.bad_content == "Missing field"
