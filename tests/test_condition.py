import pytest

from mmuxer.models.condition import All, Any, Body, From, Not, To
from mmuxer.models.enums import ComparisonOperator


def test_condition_base(mailbox, make_message):
    mailbox.login("u", "p")
    make_message(
        content_text="content",
    )
    messages = list(mailbox.fetch())
    m = messages[0]

    cond_ok = From(
        FROM="from@ok.com",
        operator=ComparisonOperator.EQUALS,
    )
    assert cond_ok.eval(m) is True

    comp_cond_not = Not(NOT=cond_ok)
    assert comp_cond_not.eval(m) is False

    cond_ko = To(TO="something else", operator=ComparisonOperator.CONTAINS)
    assert cond_ko.eval(m) is False

    comp_cond_or = Any(ANY=[cond_ok, cond_ko])
    assert comp_cond_or.eval(m) is True

    comp_cond_and = All(ALL=[cond_ok, cond_ko])
    assert comp_cond_and.eval(m) is False


@pytest.mark.parametrize(
    ("content_text", "content_html"),
    (
        ("content", None),
        (None, "<div>content</div>"),
        ("content", "<div>content</div>"),
    ),
)
def test_condition_body(mailbox, make_message, content_text, content_html):
    mailbox.login("u", "p")
    make_message(content_text=content_text, content_html=content_html)
    messages = list(mailbox.fetch())
    m = messages[0]

    cond_ok = Body(BODY="cont")
    assert cond_ok.eval(m) is True

    cond_ko = Body(BODY="contcont")
    assert cond_ko.eval(m) is False
