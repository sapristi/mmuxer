from mail_juicer.models.action import DeleteAction, FlagAction, MoveAction, UnflagAction
from mail_juicer.models.enums import Flag


def test_move_action(mailbox, make_message):

    moveAction = MoveAction(target="new_folder")

    mailbox.login("u", "p")
    mailbox.folder.create("new_folder")
    make_message(user="u", box="INBOX")
    messages = list(mailbox.fetch())
    m = messages[0]
    assert len(messages) == 1
    moveAction.apply(mailbox, m)

    messages = list(mailbox.fetch())
    assert len(messages) == 0

    mailbox.folder.set("new_folder")
    messages = list(mailbox.fetch())
    assert len(messages) == 1
    m_moved = messages[0]
    assert m.uid == m_moved.uid


def test_delete_action(mailbox, make_message):

    deleteAction = DeleteAction()

    mailbox.login("u", "p")
    make_message(user="u", box="INBOX")
    messages = list(mailbox.fetch())
    m = messages[0]
    assert len(messages) == 1
    deleteAction.apply(mailbox, m)

    messages = list(mailbox.fetch())
    assert len(messages) == 0


def test_flag_actions(mailbox, make_message):

    flagAction = FlagAction(flag=Flag.FLAGGED)
    unflagAction = UnflagAction(flag=Flag.FLAGGED)

    mailbox.login("u", "p")
    make_message(user="u", box="INBOX")

    messages = list(mailbox.fetch())
    m = messages[0]
    assert len(messages) == 1
    print(m.flags)
    assert Flag.FLAGGED.name not in m.flags
    flagAction.apply(mailbox, m)

    messages = list(mailbox.fetch())
    assert len(messages) == 1
    m_flagged = messages[0]
    assert Flag.FLAGGED.imap in m_flagged.flags

    assert m.uid == m_flagged.uid

    unflagAction.apply(mailbox, m_flagged)
    messages = list(mailbox.fetch())
    assert len(messages) == 1
    m_unflagged = messages[0]
    assert Flag.FLAGGED.imap not in m_unflagged.flags
