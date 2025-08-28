"""Utility methods to use a specific logging style."""
from contextlib import contextmanager
from shlex import join
import signal
import subprocess  # nosec
import sys
from typing import Generator, List, Optional

from logbook import INFO, Logger, StreamHandler  # type: ignore

logger = Logger(__name__)

ANSI_RED = '\033[0;31m'
ANSI_BLUE = '\033[0;34m'
ANSI_CYAN = '\x1b[36;20m'
ANSI_CLEAR = '\033[0;0m'


@contextmanager
def colored_logging(application_name: str) -> Generator[None, None, None]:
    """Prefixes log messages with a colored application preamble."""
    signal.signal(signal.SIGINT, _signal_handler)

    log_handler = StreamHandler(sys.stdout, level=INFO)
    log_handler.format_string = f'{ANSI_BLUE}[{application_name}]{ANSI_CLEAR}'' {record.message}'

    with log_handler.applicationbound():
        try:
            yield
        except Exception as e:
            _log_error(e)
            raise e


def _log(message):
    logger.info(f'{message}')


def _log_error(e):
    logger.error(f'{ANSI_RED}An error occurred{ANSI_CLEAR}: {e}')


def _log_external(message):
    logger.info(f'{ANSI_CYAN}{message}{ANSI_CLEAR}')


def _signal_handler(sig, frame):
    logger.error(f'{ANSI_RED}BUILD PLUGIN WAS INTERRUPTED{ANSI_CLEAR}')
    raise InterruptedError('Build plugin was interrupted')


def _run(command: List[str], stdin: Optional[str] = None):
    _log(f'$ {join(command)}')
    try:
        if stdin:
            subprocess.run(command, check=True, input=stdin, text=True)  # nosec
        else:
            subprocess.run(command, check=True)  # nosec
    finally:
        print('', flush=True)
