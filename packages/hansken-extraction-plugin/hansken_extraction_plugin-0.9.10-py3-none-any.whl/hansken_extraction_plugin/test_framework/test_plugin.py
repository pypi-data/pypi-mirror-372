"""Test an extraction plugin using the provided test framework."""
import argparse
import shutil
import subprocess  # nosec
import sys
from typing import Type

from hansken_extraction_plugin.runtime.reflection_util import get_plugin_class, ReflectionError
from hansken_extraction_plugin.test_framework import FriendlyError
from hansken_extraction_plugin.test_framework.validator import ByClassTestPluginRunner, DockerTestPluginRunner, \
    FlitsTestRunner, log_context, PluginValidator, RemotelyStartedTestPluginRunner

MIN_JAVA_VERSION = 11


def _test_validate_standalone(plugin_class: Type, input_path, result_path, regenerate, verbose) -> int:
    with log_context():
        # setup test
        test_runner = FlitsTestRunner(input_path, result_path, regenerate, verbose)
        standalone_runner = ByClassTestPluginRunner(plugin_class)
        validator = PluginValidator(test_runner, standalone_runner)
        return validator.validate_plugin()


def _test_validate_manual(hostname, port, input_path, result_path, regenerate, verbose) -> int:
    with log_context():
        test_runner = FlitsTestRunner(input_path, result_path, regenerate, verbose)
        manual_runner = RemotelyStartedTestPluginRunner(hostname, port)
        validator = PluginValidator(test_runner, manual_runner)
        return validator.validate_plugin()


def _test_validate_docker(docker_repository, input_path, result_path, regenerate, verbose, timeout) -> int:
    with log_context():
        test_runner = FlitsTestRunner(input_path, result_path, regenerate, verbose)
        standalone_runner = DockerTestPluginRunner(docker_repository, timeout)
        validator = PluginValidator(test_runner, standalone_runner)
        return validator.validate_plugin()


def _ensure_docker():
    if not shutil.which('docker'):
        raise FriendlyError('The test runner requires `docker` to be installed.\n'
                            'Please install Docker and try again.')


def _ensure_java(test_java_version=True):
    if not shutil.which('java'):
        raise FriendlyError('The test runner requires `java` to be installed.\n'
                            'Please install Java and try again.')

    if not test_java_version:
        return

    try:
        java_version = subprocess.run(['java', '-version'], capture_output=True).stderr.decode('utf-8')  # nosec
        if not java_version:
            raise FriendlyError('`java -version` did not return version info')
        try:
            version_number = java_version.splitlines()[0].split('"')[1]
            major, minor, _ = version_number.split('.')
            int(major)
        except Exception:
            raise FriendlyError('could not parse Java version from `java -version` output (was: '
                                f'{java_version.splitlines()[0]})')
        if int(major) < MIN_JAVA_VERSION:
            raise FriendlyError(f'Java version should be at least version {MIN_JAVA_VERSION}, '
                                f'please upgrade Java (got: {version_number})\n'
                                'If you think this is incorrect, please re-run with the `--skip-java-version-check` '
                                'flag enabled.')
    except FriendlyError as e:
        raise e
    except Exception as e:
        raise FriendlyError(f'Unable to determine Java version: {e}')


def _main():
    """Run tests for a provided extraction plugin."""
    parser = argparse.ArgumentParser(prog='test_plugin',
                                     usage='%(prog)s [options]',
                                     description='A script to run three types of tests on your plugin.')

    run_mode_parser = parser.add_mutually_exclusive_group(required=True)
    run_mode_parser.add_argument('-s', '--standalone', metavar='PLUGIN',
                                 help='Run the FLITS test against the plugin served locally.')
    run_mode_parser.add_argument('-m', '--manual', nargs=2, metavar=('SERVER', 'PORT'),
                                 help='Run the FLITS test against the plugin running on the server SERVER with port '
                                      'PORT. The plugin is expected to be already running (use command serve_plugin).')
    run_mode_parser.add_argument('-d', '--docker', metavar='DOCKER_IMAGE',
                                 help='Run the FLITS test against the plugin running in a docker container.')

    parser.add_argument('-i', '--input', default='testdata/input', help='PATH to the input files.')
    parser.add_argument('-r', '--result', default='testdata/result', help='PATH to the result files.')
    parser.add_argument('-reg', '--regenerate', action='store_true', help='Regenerate test results.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    parser.add_argument('-t', '--timeout', default=30.0, type=float,
                        help='Time (in seconds) the test framework has to wait for the Docker container to be ready.')
    parser.add_argument('--skip-java-version-check', action='store_true', help=argparse.SUPPRESS)

    args = parser.parse_args()

    test_standalone = args.standalone
    test_manual = args.manual
    test_docker = args.docker

    input_path = args.input
    result_path = args.result
    regenerate = args.regenerate
    verbose = args.verbose

    _ensure_java(not args.skip_java_version_check)

    if test_standalone:
        plugin_class = get_plugin_class(test_standalone)
        sys.exit(_test_validate_standalone(plugin_class, input_path, result_path, regenerate, verbose))
    if test_docker:
        _ensure_docker()
        sys.exit(_test_validate_docker(test_docker, input_path, result_path, regenerate, verbose, args.timeout))
    if test_manual:
        sys.exit(_test_validate_manual(test_manual[0], test_manual[1], input_path, result_path, regenerate, verbose))


def main():
    """Run tests for a provided extraction plugin."""
    try:
        _main()
    except ReflectionError as e:
        print(f'Failed to load the plugin: {e}')
        sys.exit(1)
    except FriendlyError as e:
        print(f'ERROR: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
