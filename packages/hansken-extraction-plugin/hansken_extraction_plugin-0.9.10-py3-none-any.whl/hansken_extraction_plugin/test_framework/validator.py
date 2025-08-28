"""Validate extraction plugins by running them against the test framework."""
from abc import ABC, abstractmethod
from contextlib import closing, contextmanager
import glob
import math
import os
from os.path import isdir
import re
import shutil
import socket
import subprocess  # nosec
import sys
from tarfile import TarFile
import threading
from time import sleep
from typing import Any, Dict, Generator, Iterator, Optional, Tuple, Type

import docker  # type: ignore
from docker import DockerClient  # type: ignore
from docker.errors import APIError, ImageNotFound  # type: ignore
from docker.models.containers import Container  # type: ignore
from docker.types import Healthcheck  # type: ignore
import grpc
from logbook import FileHandler, Logger, NestedSetup, StreamHandler  # type: ignore

from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin
from hansken_extraction_plugin.buildkit.color_log import _log_external
from hansken_extraction_plugin.framework.ExtractionPluginService_pb2_grpc import ExtractionPluginServiceStub
from hansken_extraction_plugin.runtime.extraction_plugin_server import serve
from hansken_extraction_plugin.test_framework import FriendlyError

nanos = 1_000_000_000
log = Logger(__name__)


class TestPluginRunner(ABC):
    """Abstract base class to encapsulate plugin runners. Subclasses serve a plugin on localhost."""

    DEFAULT_PORT = 8999

    @contextmanager
    @abstractmethod
    def run(self) -> Generator[Tuple[str, int], None, None]:
        """
        Run the plugin, and yields the hostname and port of the plugin.

        :return: a contextmanager which starts and stops the server, that yields the hostname and port where the
                 plugin is running
        """
        pass


class RemotelyStartedTestPluginRunner(TestPluginRunner):
    """Exposes a running plugin as TestPluginRunner."""

    def __init__(self, hostname: str, port: int):
        """Initialize runner to run using a provided plugin."""
        self._hostname = hostname
        self._port = port

    @contextmanager
    def run(self) -> Generator[Tuple[str, int], None, None]:
        """Run the plugin, and yields the hostname and port of the plugin."""
        yield self._hostname, self._port


class ByClassTestPluginRunner(TestPluginRunner):
    """Run a plugin on localhost using a gRPC Server which runs in its own thread."""

    def __init__(self, plugin_class: Type[BaseExtractionPlugin]):
        """Initialize runner to run using a provided plugin."""
        self._plugin_class = plugin_class

    @contextmanager
    def run(self) -> Generator[Tuple[str, int], None, None]:
        """Run the plugin, and yields the hostname and port of the plugin."""
        host = 'localhost'
        port = find_free_port()
        with serve(self._plugin_class, f'{host}:{port}'):
            yield host, port


class DockerTestPluginRunner(TestPluginRunner):
    """Run a plugin in docker using a provided docker image."""

    def __init__(self, docker_image: str, timeout: float):
        """
        Initialize the plugin runner.

        :param docker_image: the name of the docker image
        """
        self._docker_image = docker_image
        self.timeout = timeout

    def _run_docker(self, port: int, container_name: Optional[str] = None) -> Optional[Container]:
        client = docker.from_env()  # type: ignore

        try:
            client.images.get(self._docker_image)
        except ImageNotFound:
            raise FriendlyError(f'Docker image {self._docker_image} does not exists')

        health_cmd = 'health_check_plugin localhost 8999 || exit 1'
        retries = 10
        interval = math.ceil(self.timeout * nanos / retries)
        container = client.containers.run(self._docker_image,
                                          detach=True,
                                          remove=True,
                                          ports={8999: port},
                                          healthcheck=Healthcheck(test=health_cmd,
                                                                  interval=interval,
                                                                  retries=retries),
                                          environment=['LOG_LEVEL=INFO'],
                                          name=container_name)
        log.info('Starting Docker container: {}', container.id)

        self._log_container_logs(container)

        for retry in range(retries):
            if self._health(client, container)['Status'] == 'healthy':
                log.debug('Started Docker container: {}', container.id)
                return container
            log.debug('Wait until the Docker container is healthy [{}/{}]', retry + 1, retries)
            sleep(interval / nanos)

        for health_log_item in self._health(client, container)['Log']:
            log.debug('[{}] Docker health check failed: {}',
                      health_log_item['Start'],
                      health_log_item['Output'].strip())

        raise FriendlyError(f'Docker container does not start within {self.timeout} seconds')

    @contextmanager
    def run(self, container_name: Optional[str] = None) -> Iterator[Tuple[str, int]]:
        """Run the plugin, and yields the hostname and port of the plugin."""
        container = None
        port = find_free_port()
        try:
            log.debug('Starting Docker container in the background')
            container = self._run_docker(port, container_name)
            log.info('Started Docker container {} in the background', container.id)
            yield 'localhost', port
        finally:
            if container:
                log.debug('Stopping Docker container {}', container.id)
                self._stop_docker(container)

    @contextmanager
    def run_and_connect(self, container_name: Optional[str] = None) -> Iterator[ExtractionPluginServiceStub]:
        """Run the plugin, and yield an ServiceStub which can be used to execute grpc plugin methods."""
        with self.run(container_name) as (hostname, port):
            with grpc.insecure_channel(f'{hostname}:{port}') as channel:
                # wait for ready state of channel
                log.debug('Connecting to Docker container using grpc')
                grpc.channel_ready_future(channel).result()
                yield ExtractionPluginServiceStub(channel)

    @staticmethod
    def _log_container_logs(container: Container) -> None:
        def logging():
            for line in container.logs(stream=True, stdout=True, stderr=True):
                _log_external(line.decode().strip())

        # retrieving streaming container logs returns a generator that returns live logs and blocks until the container
        # stops. Parse these logs in a separate thread to prevent blocking the entire application.
        threading.Thread(target=logging).start()

    @staticmethod
    def _health(client: DockerClient, container: Container) -> Dict[str, Any]:
        try:
            status = client.api.inspect_container(container.id)
            return status['State']['Health']
        except APIError:
            raise FriendlyError(f'Health check failed for Docker container: {container.id}')

    @staticmethod
    def _stop_docker(container: Container):
        try:
            container.stop()
            log.info(f'Stopped Docker container {container.id}')
        except APIError as error:
            log.error('Docker container {} could not be stopped: {}', container.id, error)
            raise FriendlyError(f'Docker container {container.id} could not be stopped')


class TestFramework(ABC):
    """Extraction Plugin tests can be run using a TestFramework."""

    @abstractmethod
    def run(self, host: str, port: int) -> int:
        """
        Run the test framework for a plugin server.

        :param host: the host the plugin server is listening on
        :param port: the port the plugin server is listening on
        :return: return code of the test framework execution
        """
        pass


class _TestFrameworkWrapper:
    """
    Wrapper around the Extraction Plugins SDK test framework (a Java app).

    Note: check that python has sufficient permissions to execute bash and java.
    """

    TEST_RUNNER_DIR = '.runner'
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8999

    def __init__(self):
        if not _TestFrameworkWrapper._test_framework_installed():
            version, _ = _TestFrameworkWrapper._test_framework_distinfo()
            log.info('Unpacking test framework version {}', version)
            _TestFrameworkWrapper._install_test_framework()

    @staticmethod
    def _test_framework_installed() -> bool:
        return os.path.exists(_TestFrameworkWrapper._test_framework_jar())

    @staticmethod
    def _clean_runner_dir() -> None:
        if os.path.exists(_TestFrameworkWrapper.TEST_RUNNER_DIR):
            log.debug('Cleaning test-runner directory: {}', _TestFrameworkWrapper.TEST_RUNNER_DIR)
            shutil.rmtree(_TestFrameworkWrapper.TEST_RUNNER_DIR)

    @staticmethod
    def _test_framework_distinfo() -> Tuple[str, str]:
        here = os.path.dirname(os.path.abspath(__file__))
        tgz_file = glob.glob(f'{here}/_resources/test-framework-*-bin.tar.gz', recursive=False)[0]
        version = tgz_file.split('test-framework-')[1].split('-bin')[0]
        return version, tgz_file

    @staticmethod
    def _install_test_framework() -> None:
        _, tgz_file = _TestFrameworkWrapper._test_framework_distinfo()
        log.debug('installing test-framework from: {}', tgz_file)
        downloaded_tgz_file = TarFile.open(tgz_file, 'r:gz')
        downloaded_tgz_file.extractall(_TestFrameworkWrapper.TEST_RUNNER_DIR)

    @staticmethod
    def _test_framework_dir() -> str:
        version, _ = _TestFrameworkWrapper._test_framework_distinfo()
        return f'{_TestFrameworkWrapper.TEST_RUNNER_DIR}/test-framework-{version}'

    @staticmethod
    def _test_framework_jar() -> str:
        version, _ = _TestFrameworkWrapper._test_framework_distinfo()
        return f'{_TestFrameworkWrapper._test_framework_dir()}/test-framework-{version}.jar'

    @staticmethod
    def run(input_dir: str, result_dir: str,
            host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
            regenerate: bool = False, verbose: bool = False) -> int:
        """
        Run the Extraction Plugin SDK Flits Test Framework against a test plugin server.

        :param input_dir: path to directory with input test data
        :param result_dir: path to directory with result test data
        :param host: the host on which the plugin server is listening
        :param port: the port on which the plugin server is listening
        :param regenerate: do not validate, but *regenerate* (overwrite!) the test results from the input
        :param verbose: enable verbose logging
        :return: return code of returned by the actual test framework
        """
        # sanity check input and result directories
        if not (isdir(input_dir) and isdir(result_dir)):
            raise FriendlyError(f'Both {input_dir} and {result_dir} should be accessible directories.')

        # sanity check host name to protect against code injection through subprocess arguments
        re_hostname = re.compile('([a-zA-Z0-9\\-]*\\.)*[a-zA-Z0-9\\-]*')
        if not re_hostname.match(host):
            raise FriendlyError(f'Unacceptable host name: {host}')

        # build java command (should run with -Xmx350m)
        cmd = ['java', '-Xmx350m', '-jar', _TestFrameworkWrapper._test_framework_jar(),
               '--host', host, '--port', str(port), '--testpath', input_dir, '--resultpath', result_dir]
        if verbose:
            cmd += ['--verbose']
        if regenerate:
            cmd += ['--regenerate']

        log.debug('Running test-framework for plugin at {}:{}: {}', host, port, cmd)
        # run the integration test suite, exit code 1 indicates a test failure
        result = subprocess.run(cmd)  # nosec
        return result.returncode


class FlitsTestRunner(TestFramework):
    """Test Framework which uses the FlitsRunner as backend."""

    def __init__(self, input_dir: str, result_dir: str, regenerate: bool = False, verbose: bool = False):
        """
        Specify a test run.

        :param input_dir: the input directory
        :param result_dir: the result directory to validate the plugin output
        :param regenerate: if the contents of the result dir should be re-generated, based on the input
                           Note: regenerating will overwrite result data!
        :param: verbose: enable verbose logging
        """
        self._input_dir = input_dir
        self._result_dir = result_dir
        self._regenerate = regenerate
        self._verbose = verbose
        self._flits_runner = _TestFrameworkWrapper()

    def run(self, host: str = 'localhost', port: int = _TestFrameworkWrapper.DEFAULT_PORT) -> int:
        """
        Run the test framework for a plugin server.

        :param host: the host the plugin server is listening on
        :param port: the port the plugin server is listening on
        :return: return code of the test framework execution
        """
        return self._flits_runner.run(self._input_dir, self._result_dir, host, port, self._regenerate, self._verbose)


class PluginValidator:
    """Validate plugins using the Flits test-framework."""

    def __init__(self, test_framework: TestFramework, plugin_runner: TestPluginRunner):
        """
        Initialize the plugin validator.

        :param test_framework: framework used for testing a plugin
        :param plugin_runner: runner that runs a plugin
        """
        self._test_framework = test_framework
        self._plugin_runner = plugin_runner

    def validate_plugin(self) -> int:
        """
        Validate a single plugin by starting the plugin, running the test framework, and stopping the plugin.

        :return: return code of the test framework
        """
        with self._plugin_runner.run() as (hostname, port):
            return self._test_framework.run(hostname, port)


def find_free_port() -> int:
    """Find a free tcp/udp port."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@contextmanager
def log_context():
    """
    Contextmanager utility for test log configuration.

    This should be called once from the top level, since it removes the log file each time it is called.
    """
    # setup logging to stdout and .tox/tests.log
    log_file_name = 'tests.log'
    if os.path.exists(log_file_name):
        try:
            os.remove(log_file_name)  # clean log
        except PermissionError:
            log.warn('Could not delete ' + log_file_name)
    log_handler = NestedSetup([
        FileHandler(log_file_name, bubble=False, level='DEBUG', format_string=u'{record.message}'),
        StreamHandler(sys.stdout, bubble=True, level='DEBUG')])

    with log_handler.applicationbound() as context:
        yield context
