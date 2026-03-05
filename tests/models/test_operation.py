from datetime import date, timedelta
from unittest.mock import patch

from imap_tools.query import AND as imap_AND
from imap_tools.query import NOT as imap_NOT
from imap_tools.query import OR as imap_OR
from imap_tools.query import H as imap_HEADER

from mmuxer.models.enums import Flag
from mmuxer.models.operation import (
    All,
    Any,
    HasCustomFlag,
    HasFlag,
    Header,
    Not,
    OlderThan,
    YoungerThan,
)


def test_has_flag():
    # GIVEN a HasFlag criterion for FLAGGED
    crit = HasFlag(flag=Flag.FLAGGED)

    # WHEN converted to search condition
    # THEN it produces the correct dict
    assert crit.to_search_condition() == {Flag.FLAGGED.value.lower(): True}


def test_has_custom_flag():
    # GIVEN a HasCustomFlag criterion
    crit = HasCustomFlag(custom_flag="my_flag")

    # WHEN converted to search condition
    # THEN it produces a keyword dict
    assert crit.to_search_condition() == {"keyword": "my_flag"}


@patch("mmuxer.models.operation.date")
def test_older_than(mock_date):
    # GIVEN today is 2026-03-06 and an OlderThan criterion of 10 days
    mock_date.today.return_value = date(2026, 3, 6)
    mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
    crit = OlderThan(older_than_days=10)

    # WHEN converted to search condition
    result = crit.to_search_condition()

    # THEN it produces a date_lt 10 days before today
    assert result == {"date_lt": date(2026, 2, 24)}


@patch("mmuxer.models.operation.date")
def test_younger_than(mock_date):
    # GIVEN today is 2026-03-06 and a YoungerThan criterion of 5 days
    mock_date.today.return_value = date(2026, 3, 6)
    mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
    crit = YoungerThan(younger_than_days=5)

    # WHEN converted to search condition
    result = crit.to_search_condition()

    # THEN it produces a date_gte 5 days before today
    assert result == {"date_gte": date(2026, 3, 1)}


def test_header():
    # GIVEN a Header criterion
    crit = Header(name="X-Custom", value="test")

    # WHEN converted to search condition
    result = crit.to_search_condition()

    # THEN it produces a header query with quoted name and value
    assert "header" in result
    header = result["header"]
    assert header.name == '"X-Custom"'
    assert header.value == '"test"'


def test_all_operator():
    # GIVEN an All operator combining two criteria
    crit = All(
        ALL=[
            HasFlag(flag=Flag.FLAGGED),
            HasCustomFlag(custom_flag="test"),
        ]
    )

    # WHEN converted to search condition
    result = crit.to_search_condition()

    # THEN it produces an AND query
    expected = imap_AND(**{Flag.FLAGGED.value.lower(): True}, keyword="test")
    assert str(result) == str(expected)


def test_not_operator():
    # GIVEN a Not operator wrapping a HasFlag criterion
    crit = Not(NOT=HasFlag(flag=Flag.FLAGGED))

    # WHEN converted to search condition
    result = crit.to_search_condition()

    # THEN it produces a NOT query
    expected = imap_NOT(**{Flag.FLAGGED.value.lower(): True})
    assert str(result) == str(expected)


def test_any_operator():
    # GIVEN an Any operator combining two criteria
    crit = Any(
        ANY=[
            HasFlag(flag=Flag.FLAGGED),
            HasCustomFlag(custom_flag="test"),
        ]
    )

    # WHEN converted to search condition
    result = crit.to_search_condition()

    # THEN it produces an OR query
    expected = imap_OR(**{Flag.FLAGGED.value.lower(): True}, keyword="test")
    assert str(result) == str(expected)
