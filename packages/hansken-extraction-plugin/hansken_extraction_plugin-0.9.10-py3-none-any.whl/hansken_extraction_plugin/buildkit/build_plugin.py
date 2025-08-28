"""Contains a cmd entry point to create a plugin docker image with plugin info labels."""
import argparse
from random import randint
import sys

from hansken_extraction_plugin.buildkit.color_log import _log, _run, colored_logging
from hansken_extraction_plugin.buildkit.label_plugin import label_plugin, log_labels

description = ('This script builds and labels an Extraction Plugin docker image. The image is \n'
               ' started to retrieve the information required to label the image. \n\n'
               'It is possible to provide additional command line arguments. These arguments \n '
               'are passed to the docker build command. \n\n'
               'Example: build_plugin --target-name image_name . --build-arg https_proxy="$https_proxy"')


def _build(containerfile_path, build_agent_args=None, tmp_plugin_image=None, build_agent='docker') -> str:
    tmp_plugin_image = tmp_plugin_image or f'build_extraction_plugin:{randint(0, 999999)}'  # nosec
    if build_agent == 'buildah':
        command = ['buildah', 'bud', '-t', tmp_plugin_image]

        # When using buildah --build-arg may only be specified before the container filepath.
        command.extend(build_agent_args)
        command.append(containerfile_path)
    elif build_agent == 'docker' or build_agent == 'podman':
        command = [build_agent, 'build', containerfile_path, '-t', tmp_plugin_image]
        command.extend(build_agent_args)
    else:
        raise ValueError("build_agent must be 'buildah' or 'docker' or 'podman' but was {}".format(build_agent))

    _log('Building a Hansken extraction plugin image')
    _run(command)
    return tmp_plugin_image


def _build_and_label(docker_file_path, target_image_name=None, docker_build_args=None, timeout=None):
    tmp_plugin_image = _build(docker_file_path, docker_build_args)
    _log('The plugin image was built successfully! Now the required plugin LABELS will be added to the image.')
    try:
        result = label_plugin(tmp_plugin_image, target_name=target_image_name, timeout=timeout)
    finally:
        _log('Removing temporary build image')
        _run(['docker', 'image', 'rm', tmp_plugin_image])

    if not result:
        return
    tag_version, tag_latest = result
    log_labels(tag_version, tag_latest)  # logging *AFTER* removing temporary build image for user readability
    print(tag_latest)


def _parse_args(args):
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', help='path to the directory containing the Dockerfile of the plugin')
    parser.add_argument('--timeout', default=30.0, type=float,
                        help='time (in seconds) the framework will wait for the Docker container to be ready before '
                             'labeling the plugin', required=False)
    parser.add_argument('--target-name', required=False,
                        help='name of the target docker image without tag. Note that docker image names cannot start '
                             'with a period or dash')

    parsed, docker_build_args = parser.parse_known_args(args)
    docker_file_path = parsed.path
    timeout = parsed.timeout
    image_name = parsed.target_name
    return docker_file_path, timeout, image_name, docker_build_args


def main():
    """Build and label an extraction plugin Docker image according to provided arguments."""
    parsed = _parse_args(sys.argv[1:])

    docker_file_path, timeout, target_image_name, docker_build_args = parsed
    try:
        with colored_logging('BUILD_PLUGIN'):
            _build_and_label(docker_file_path, target_image_name, docker_build_args, timeout)
        sys.exit(0)
    except Exception:
        sys.exit(1)


if __name__ == '__main__':
    main()
