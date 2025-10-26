import itertools

import more_itertools
from rich import print
from rich.pretty import Pretty

from mmuxer.config_state import state
from mmuxer.models.operation import All, Operation, SearchCriteria


def debug_iter(f):
    def inner(*args, **kwargs):
        res = list(f(*args, **kwargs))
        print(res)
        yield from res

    return inner


def _get_messages(query, folder: str):
    box = state.mailbox
    box.folder.set(folder)
    yield from box.fetch(
        query,
        mark_seen=False,
        headers_only=True,
        bulk=50,
    )


def get_messages(operation):
    query = operation.query
    if query is not None:
        if isinstance(query, SearchCriteria):
            query = All(ALL=[query])
        search_query = query.to_search_condition()
    else:
        search_query = "ALL"

    yield from itertools.chain.from_iterable(
        _get_messages(search_query, folder) for folder in operation.folders
    )


def apply_operation(
    operation: Operation,
    ask_confirmation: bool,
):
    for messages in more_itertools.chunked(get_messages(operation), n=operation.batch_size):
        if ask_confirmation:
            for message in messages:
                print(message)

            print(f"Will apply the following actions to {len(messages)} messages, continue ?")
            for action in operation.actions:
                print(" - ", end="")
                print(Pretty(action))
