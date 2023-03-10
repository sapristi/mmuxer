import imaplib
import logging
import time
from threading import Event, Thread

from imap_tools import AND
from watchfiles import watch

from .config_state import state
from .models.rule import apply_list

logger = logging.getLogger(__name__)

flag = Event()


class MonitorWorker(Thread):
    def __init__(self, dry_run, folder):
        self.dry_run = dry_run
        self.folder = folder
        super().__init__()

    def run(self):
        logger.debug("Starting IMAP monitor thread.")
        box = state.mailbox
        while True:
            if flag.isSet():
                logger.info("Config change detected, reloading")
                state.reload_config_file()
                flag.clear()
            try:
                responses = box.idle.wait(timeout=state.settings.imap_wait_timeout)
                if responses:
                    for msg in box.fetch(AND(seen=False), mark_seen=False):
                        msg.associated_folder = self.folder
                        logger.info(
                            f"Found message [{{{msg.uid}}} {msg.from_} -> {msg.to} '{msg.subject}']"
                        )
                        apply_list(state.rules, box, msg, self.dry_run)
                        for script in state.scripts:
                            script.apply(msg, dry_run=self.dry_run)
            except imaplib.IMAP4.abort:
                logger.warning("IMAP connection aborted, reconnecting ")
                state.create_mailbox()
                box = state.mailbox
            except Exception:
                logger.exception("An error occured, reconnecting...")
                state.create_mailbox()
                box = state.mailbox

            time.sleep(0.1)


class WatcherWorker(Thread):
    def run(self):
        logger.debug("Starting file watcher thread, monitoring %s.", state.config_file)
        # force polling because of a bug with vim.
        # The other solution would be to watch the whole folder
        for _change in watch(
            state.config_file,
            force_polling=True,
            poll_delay_ms=1000,
        ):
            flag.set()
