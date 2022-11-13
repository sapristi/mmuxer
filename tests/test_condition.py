from mail_juicer.models.condition import All, Any, From, Not, To
from mail_juicer.models.enums import ComparisonOperator


def test_condition_base(mailbox, make_message):
    mailbox.login("u", "p")
    make_message(
        user="u",
        box="INBOX",
        to="to@ok.com",
        from_="from@ok.com",
        subject="subject",
        content="content",
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
