"""Contains a cmd entry point to serve a plugin."""
import argparse
import os
import signal
import sys
import threading
import time
from typing import Type

from logbook import Logger, StreamHandler  # type: ignore

from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin
from hansken_extraction_plugin.runtime.extraction_plugin_server import serve_indefinitely
from hansken_extraction_plugin.runtime.reflection_util import get_plugin_class, ReflectionError

log = Logger(__name__)


def hardkill():
    """
    Fully kill the current application.

    This is useful in cases where all other ways to stop the application fails.
    """
    time.sleep(.2)
    log.error('Failed to stop process, taking drastic measures now, goodbye cruel world!')
    try:
        os._exit(1)
    finally:
        os.kill(os.getpid(), signal.SIGKILL)


def serve(extraction_plugin_class: Type[BaseExtractionPlugin], port=8999) -> None:
    """
    Initialize and serve the provided plugin on provided port.

    :param extraction_plugin_class: plugin to be served
    :param port: port plugin can be reached
    """
    log.info(f'Serving plugin on port {port}...')
    serve_indefinitely(extraction_plugin_class, f'[::]:{port}')

    # we are leaving the main thread, start a small thread to kill the entire
    # application if we don't exit gracefully when some other threads are
    # blocking the application to stop
    threading.Thread(target=hardkill, daemon=True).start()


def _determine_log_level(verbose_arg: int) -> str:
    """
    Return the current log level as string.

    If the environment variable LOG_LEVEL is not set, it will use the provided argument as default.
    """
    log_levels = ['WARNING', 'NOTICE', 'INFO', 'DEBUG']
    verbose = min(max(0, verbose_arg), 3)
    log_level = log_levels[verbose]
    env_log_level = os.environ.get('LOG_LEVEL')
    log_level = env_log_level if env_log_level in log_levels else log_level
    return log_level


def main():
    """Run an Extraction Plugin according to provided arguments."""
    parser = argparse.ArgumentParser(prog='serve_plugin',
                                     usage='%(prog)s PLUGIN PORT (Use -h for help)',
                                     description='Run an Extraction Plugin according to provided arguments.')

    parser.add_argument('plugin', metavar='PLUGIN',
                        help='Either the path of the python file or an object reference of the plugin to be served.')
    parser.add_argument('port', metavar='PORT', help='Port where plugin is served on.', type=int)
    parser.add_argument('-v', '--verbose', action='count', required=False, default=0,
                        help='Verbosity level. -v = NOTICE, -vv = INFO, -vvv = DEBUG. Default is WARNING if the '
                             'LOG_LEVEL environment variable is not set.')

    arguments = parser.parse_args()

    # Logs all log messages of severity level log_level and higher to stdout.
    log_level = _determine_log_level(arguments.verbose)
    log_handler = StreamHandler(sys.stdout, bubble=False, level=log_level)

    with log_handler.applicationbound():
        plugin = arguments.plugin
        port = arguments.port

        try:
            plugin_class = get_plugin_class(plugin)
        except ReflectionError as e:
            # print a friendly error
            print(f'Failed to load plugin: {e}')
            sys.exit(1)
        serve(plugin_class, port)


if __name__ == '__main__':
    main()
