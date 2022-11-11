from mail_juicer.models.condition import AndCondition, BaseCondition, NotCondition, OrCondition
from mail_juicer.models.enums import ComparisonOperator, MessageField


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

    cond_ok = BaseCondition(
        field=MessageField.FROM_, operator=ComparisonOperator.EQUALS, operand="from@ok.com"
    )
    assert cond_ok.eval(m) is True

    comp_cond_not = NotCondition(NOT=cond_ok)
    assert comp_cond_not.eval(m) is False

    cond_ko = BaseCondition(
        field=MessageField.TO, operator=ComparisonOperator.CONTAINS, operand="something else"
    )
    assert cond_ko.eval(m) is False

    comp_cond_or = OrCondition(OR=[cond_ok, cond_ko])
    assert comp_cond_or.eval(m) is True

    comp_cond_and = AndCondition(AND=[cond_ok, cond_ko])
    assert comp_cond_and.eval(m) is False
