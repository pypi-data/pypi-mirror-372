"""Contains a cmd entry point to create a plugin docker image with plugin info labels."""
import argparse
import sys
from typing import Optional, Tuple, Union
import uuid

from google.protobuf import empty_pb2

from hansken_extraction_plugin.api.plugin_info import PluginInfo
from hansken_extraction_plugin.buildkit.build_utils import _plugin_info_to_labels
from hansken_extraction_plugin.buildkit.color_log import _log, _log_error, _run, colored_logging
from hansken_extraction_plugin.runtime import unpack
from hansken_extraction_plugin.test_framework.validator import DockerTestPluginRunner

description = ('This is a utility to add labels to an extraction plugin image. Labeling a plugin is required for\n'
               'Hansken to detect extraction plugins in a plugin image registry. To label a plugin, first build the\n'
               'plugin image, for example by using one of the following commands:\n'
               '    docker build . -t my_plugin\n'
               '    docker build . -t my_plugin --build-arg https_proxy=http://your_proxy:8080\n'
               'Next, run this utility to label the build plugin container:\n'
               '    label_plugin my_plugin\n'
               '\n'
               'To label a plugin, this utility will start the extraction plugin container on your host.\n'
               )


def _label_plugin_with_plugininfo(image: str,
                                  plugin_info: PluginInfo,
                                  api_version: str,
                                  target_name: Optional[str] = None,
                                  docker_build_args=[],
                                  build_agent='docker') -> Tuple[str, str]:
    dockerfile = f'FROM {image}'
    labels = _plugin_info_to_labels(plugin_info, api_version)

    name = target_name or f'extraction-plugins/{plugin_info.id}'

    tag_version = f'{name}:{plugin_info.version}'.lower()
    tag_latest = f'{name}:latest'.lower()

    if build_agent == 'buildah':
        # Remove the container that will be created in the process and left behind if '--force-rm' is not provided.
        # '--no-cache' or '--layers' is required when using '--force-rm'
        command = ['buildah', 'bud', '--force-rm', '--layers', '-t', tag_version, '-t', tag_latest]
    elif build_agent == 'docker' or build_agent == 'podman':
        command = [build_agent, 'build', '-t', tag_version, '-t', tag_latest]
    else:
        raise ValueError("build_agent must be 'buildah' or 'docker' or 'podman' but was {}".format(build_agent))

    command.extend(docker_build_args)

    for (label, value) in labels.items():
        command.append('--label')
        command.append(f'{label}={value}')

    command.append('-')  # read dockerfile from stdin (which contains only the FROM-statement)

    _log('Running docker build to add labels to the plugin')
    _run(command, dockerfile)
    return tag_version, tag_latest


def _get_plugin_info(image_name: str, container_name: Optional[str] = None, timeout=30) -> Tuple[PluginInfo, str]:
    container_name = container_name if container_name else f'hansken_label_plugin_{uuid.uuid4()}'
    with DockerTestPluginRunner(image_name, timeout).run_and_connect(container_name=container_name) as grpc_server_stub:
        _log('> Request plugin info from plugin')
        rpc_plugin_info = grpc_server_stub.pluginInfo(empty_pb2.Empty())
        plugin_info, api_version = unpack.plugin_info(rpc_plugin_info)
        _log('> Got plugin info from plugin!')
    return plugin_info, api_version


def label_plugin(image, target_name=None, timeout=None, docker_build_args=[]) -> Union[Tuple[str, str], None]:
    """
    Given a plugin image, label it.

    :param image: the plugin OCI image to label
    :param target_name: optional target image name that will contain the labels
    :param timeout: Optional timeout argument, indicating the time to wait for a plugin to start
    :param docker_build_args: Optional additional argument(s) passed to the `docker build` command
    :return: tag_with_version, tag_with_latest, None if the plugin is not compatible
    """
    plugin_info, api_version = _get_plugin_info(image, timeout=timeout)

    if not plugin_info.id or not plugin_info.id.domain or not plugin_info.id.category or not plugin_info.id.name:
        _log_error('The plugin to label did not return a valid plugin id. '
                   'If the plugin was created before SDK version 0.4.0, please consider upgrading your plugin.')
        return None

    return _label_plugin_with_plugininfo(image, plugin_info, api_version, target_name, docker_build_args)


def log_labels(tag_version, tag_latest):
    """Log the plugin image tags."""
    _log('plugin labeled!')
    _log(f'> plugin image tag: {tag_version}')
    _log(f'> plugin image tag: {tag_latest}')


def _label_plugin(image, target_name=None, timeout=None, docker_build_args=[]):
    # internal use: label plugin, print labels directly to stdout
    tag_version, tag_latest = label_plugin(image, target_name, timeout, docker_build_args)
    log_labels(tag_version, tag_latest)
    print(tag_latest)


def _parse_arguments():
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)

    # required image argument
    parser.add_argument('image', help='The image to add labels to')

    # optional targetimage argument
    parser.add_argument('--target-name',
                        help='Optional target image, the original image will not be updated', required=False)

    parser.add_argument('--timeout', default=30.0, type=float,
                        help='Time (in seconds) the framework has to wait for the Docker container to be ready.')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return None

    return parser.parse_known_args()


def main():
    """Label an extraction plugin Docker image according to provided arguments."""
    arguments, docker_build_args = _parse_arguments()
    if not arguments:
        sys.exit(2)

    try:
        with colored_logging('LABEL_PLUGIN'):
            _label_plugin(arguments.image, arguments.target_name, arguments.timeout, docker_build_args)
        sys.exit(0)
    except Exception:
        sys.exit(1)


if __name__ == '__main__':
    main()
