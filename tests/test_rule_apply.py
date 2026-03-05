from unittest.mock import MagicMock

from mmuxer.models.action import FlagAction, MoveAction
from mmuxer.models.condition import From
from mmuxer.models.enums import ComparisonOperator, Flag
from mmuxer.models.rule import Rule, RuleSet


def test_rule_matches_and_applies(mailbox, make_message):
    # GIVEN a message from "from@ok.com" and a rule matching that sender
    mailbox.login("u", "p")
    mailbox.folder.create("dest")
    make_message(content_text="hello")
    messages = list(mailbox.fetch())
    m = messages[0]

    rule = Rule(
        condition=From(FROM="from@ok.com", operator=ComparisonOperator.EQUALS),
        move_to="dest",
    )

    # WHEN the rule is applied
    result = rule.apply(mailbox, m, dry_run=False)

    # THEN it matches and moves the message to dest
    assert result is True
    mailbox.folder.set("INBOX")
    assert len(list(mailbox.fetch())) == 0
    mailbox.folder.set("dest")
    assert len(list(mailbox.fetch())) == 1


def test_rule_no_match(mailbox, make_message):
    # GIVEN a message from "from@ok.com" and a rule matching a different sender
    mailbox.login("u", "p")
    make_message(content_text="hello")
    messages = list(mailbox.fetch())
    m = messages[0]

    rule = Rule(
        condition=From(FROM="nobody@example.com", operator=ComparisonOperator.EQUALS),
        move_to="dest",
    )

    # WHEN the rule is applied
    result = rule.apply(mailbox, m, dry_run=False)

    # THEN it does not match and the message stays in INBOX
    assert result is False
    assert len(list(mailbox.fetch())) == 1


def test_ruleset_stops_after_first_match(mailbox, make_message):
    # GIVEN two matching rules where the first has keep_evaluating=False
    mailbox.login("u", "p")
    mailbox.folder.create("dest1")
    mailbox.folder.create("dest2")
    make_message(content_text="hello")
    messages = list(mailbox.fetch())
    m = messages[0]

    rule1 = Rule(
        condition=From(FROM="from@ok.com", operator=ComparisonOperator.EQUALS),
        actions=[FlagAction(flag=Flag.FLAGGED)],
        keep_evaluating=False,
    )
    rule2 = Rule(
        condition=From(FROM="from@ok.com", operator=ComparisonOperator.EQUALS),
        move_to="dest2",
    )
    ruleset = RuleSet(root=[rule1, rule2])

    # WHEN the ruleset is applied
    ruleset.apply(mailbox, m, dry_run=False)

    # THEN only the first rule's action is applied (flagged but not moved)
    messages = list(mailbox.fetch())
    assert len(messages) == 1
    assert Flag.FLAGGED.imap in messages[0].flags


def test_ruleset_continues_with_keep_evaluating(mailbox, make_message):
    # GIVEN two matching rules where the first has keep_evaluating=True
    mailbox.login("u", "p")
    mailbox.folder.create("dest")
    make_message(content_text="hello")
    messages = list(mailbox.fetch())
    m = messages[0]

    rule1 = Rule(
        condition=From(FROM="from@ok.com", operator=ComparisonOperator.EQUALS),
        actions=[FlagAction(flag=Flag.FLAGGED)],
        keep_evaluating=True,
    )
    rule2 = Rule(
        condition=From(FROM="from@ok.com", operator=ComparisonOperator.EQUALS),
        move_to="dest",
    )
    ruleset = RuleSet(root=[rule1, rule2])

    # WHEN the ruleset is applied
    ruleset.apply(mailbox, m, dry_run=False)

    # THEN both rules' actions are applied (flagged and moved)
    mailbox.folder.set("INBOX")
    assert len(list(mailbox.fetch())) == 0
    mailbox.folder.set("dest")
    messages = list(mailbox.fetch())
    assert len(messages) == 1
    assert Flag.FLAGGED.imap in messages[0].flags
