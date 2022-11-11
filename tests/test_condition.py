from mail_juicer.models.condition import ConditionBase, ConditionComposed
from mail_juicer.models.enums import ComparisonOperator, ConditionOperator, MessageField


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

    cond_ok = ConditionBase(
        field=MessageField.FROM_, operator=ComparisonOperator.EQUALS, operand="from@ok.com"
    )
    assert cond_ok.eval(m) is True

    comp_cond_not = ConditionComposed(operator=ConditionOperator.NOT, operands=[cond_ok])
    assert comp_cond_not.eval(m) is False

    cond_ko = ConditionBase(
        field=MessageField.TO, operator=ComparisonOperator.CONTAINS, operand="something else"
    )
    assert cond_ko.eval(m) is False

    comp_cond_or = ConditionComposed(operator=ConditionOperator.OR, operands=[cond_ok, cond_ko])
    assert comp_cond_or.eval(m) is True

    comp_cond_and = ConditionComposed(operator=ConditionOperator.AND, operands=[cond_ok, cond_ko])
    assert comp_cond_and.eval(m) is False
