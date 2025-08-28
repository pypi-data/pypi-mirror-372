"""A utility to create a plugin docker image with plugin info labels. Optimized for usage within CI pipelines."""
import argparse
import json
import os
import shutil
import sys
import tarfile
from typing import Tuple

from hansken_extraction_plugin.api.plugin_info import PluginInfo
from hansken_extraction_plugin.buildkit.build_plugin import _build
from hansken_extraction_plugin.buildkit.color_log import _log, _log_error, _run, colored_logging
from hansken_extraction_plugin.buildkit.label_plugin import _label_plugin_with_plugininfo, log_labels


def get_plugin_info_from_docker_image(image_name: str, build_agent='docker') -> Tuple[PluginInfo, str]:
    """
    Retrieve the plugin info from the given image name.

    Retrieve the plugin information by saving the image to disk as a .tar file and then retrieving the plugin-info.json
    file from this tar file. This way we don't have to start the plugin in order to retrieve the plugin information.
    Only the last (most recent) image layer is extracted from the image in order to extract the plugin-info.json.

    :param image_name: The image from which we should extract the plugin-info
    :param build_agent: The build agent used to build the image. Supported: "docker", "podman" and "buildah".
    :return: The plugin info in this image and the (gRPC) API version of the plugin in this image.
    """
    # Create a temporary directory to store .tar archive and extracted files in.
    extraction_directory = os.path.join(os.getcwd(), 'tmp')
    tar_image_name = 'image.tar'
    os.makedirs(extraction_directory, exist_ok=True)

    # Save the image that we want to retrieve the plugin information from to disk.
    filepath = os.path.join(extraction_directory, tar_image_name)
    if build_agent == 'buildah':
        _run(['buildah', 'push', image_name, 'docker-archive:' + filepath])
    elif build_agent == 'docker' or build_agent == 'podman':
        _run([build_agent, 'save', '-o', filepath, image_name])
    else:
        raise ValueError("build_agent must be 'buildah' or 'docker' or 'podman' but was {}".format(build_agent))

    try:
        # Get the plugin information from the tar archive.
        return get_plugin_info_from_image_tar(extraction_directory, tar_image_name)
    finally:
        # Remove the temporary directory as we now have the plugin info and do not need to use these files anymore.
        shutil.rmtree(os.path.join(extraction_directory))


def get_plugin_info_from_image_tar(extraction_directory, tar_file) -> Tuple[PluginInfo, str]:
    """
    Retrieve the plugin information from the given tar file (which is an exported Docker image).

    This way we don't have to start the plugin in order to retrieve the plugin information.
    Only the last (most recent) image layer is extracted from the image in order to extract the plugin-info.json.

    :param extraction_directory: The directory in which temporary results should be stored.
    :param tar_file: The name of the tar file in the extraction directory that is an exported Docker image.
    :return: The plugin info in this image and the (gRPC) API version of the plugin in this image.
    """
    # Extract the manifest.json file from the image.tar. The manifest.json file contains information about the last
    # layer that our docker image consists of. We want to retrieve the plugin-info.json from the last layer.
    # Temporarily store these contents in the tmp folder so we can easily delete it later.
    # More information: https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers/
    image_tar = tarfile.open(os.path.join(extraction_directory, tar_file), 'r')
    image_tar.extract(member='manifest.json', path=extraction_directory)

    # Parse and load the manifest.json file.
    manifest_path = os.path.join(extraction_directory, 'manifest.json')
    with open(manifest_path, 'r') as manifest_file:
        manifest = json.load(manifest_file)

    # Get the last layer of our docker image from which we want to obtain the plugin information.
    # This last layer is stored as a .tar file inside the image.tar and contains the actual files that we're interested
    # in. Example value: 330514fd53f8c431f6abb689dacd9c60e2a076fa0f46a07d13c7883d4d0e7060/layer.tar
    last_layer = manifest[0]['Layers'][-1]

    # Only extract the last (most recent) layer from the image.tar since we are not interested in the other layers.
    image_tar.extract(member=last_layer, path=extraction_directory)
    image_tar.close()

    # Extract the layer.tar file that holds the plugin-info.json.
    with tarfile.open(os.path.join(extraction_directory, last_layer), 'r') as last_layer_tar:
        last_layer_tar.extract(member='plugin-info.json', path=extraction_directory)

    # Check if plugin-info is successfully extracted.
    plugin_info_file_path = os.path.join(extraction_directory, 'plugin-info.json')

    # Read the plugin information and (gRPC) API version from the JSON file and construct a PluginInfo object.
    with open(plugin_info_file_path, 'r') as file:
        content = file.read()
        data = json.loads(content)
        plugin_info: PluginInfo = PluginInfo.from_dict(data['plugin-info'])
        return plugin_info, str(data['api-version'])


description = ('This script builds and labels an Extraction Plugin docker image in a way that is specialized to be '
               'more reliable in CI pipelines due to the fact that a container does not have to be started as is the '
               'case with build_plugin. The image is saved to disk to retrieve the information required to label the '
               'image. It is important that the plugin-info.json is written within the image using the plugin_info '
               'utility in order for this tool to work. See the documentation on build_plugin_ci on how to do this.'
               '\n\n'
               'It is possible to provide additional command line arguments. These arguments are passed to the docker '
               'build command.'
               '\n\n'
               'Example: build_plugin --target-name image_name . --build-arg https_proxy="$https_proxy"')


def main():
    """Build and label an extraction plugin Docker image in a CI pipeline according to provided arguments."""
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', help='path to the directory containing the Dockerfile of the plugin')
    parser.add_argument('--target-name', required=False,
                        help='name of the target docker image without tag. Note that docker image names cannot start '
                             'with a period or dash')
    parser.add_argument('--build-agent', required=False, default='docker',
                        help='The name of the build agent that we want to use. Currently only "docker", "podman" and '
                             '"buildah" are supported.')

    args, agent_build_args = parser.parse_known_args(sys.argv[1:])

    if args.build_agent not in ['docker', 'podman', 'buildah']:
        _log_error(f"--build_agent must be 'buildah' or 'docker' or 'podman' but was {args.build_agent}")
        sys.exit(1)

    with colored_logging('BUILD_PLUGIN'):
        try:
            # Build the plugin so that the plugin-info.json gets written within the resulting image.
            # This plugin info can then be retrieved from the image and used in the labeling process.
            tmp_plugin_image = _build(containerfile_path=args.path,
                                      build_agent_args=agent_build_args,
                                      build_agent=args.build_agent)
        except Exception as e:
            _log_error('Could not build plugin due: ' + str(e))
            sys.exit(1)

        _log('The plugin image was built successfully! Now the required plugin LABELS will be added to the image.')

        try:
            try:
                # Save the image to disk and extract the plugin information from it.
                plugin_info, api_version = get_plugin_info_from_docker_image(tmp_plugin_image,
                                                                             build_agent=args.build_agent)
            except Exception as e:
                _log_error('Could not extract plugin info from Docker image due: ' + str(e))
                sys.exit(1)

            if (not plugin_info.id
                    or not plugin_info.id.domain
                    or not plugin_info.id.category
                    or not plugin_info.id.name):
                _log_error('The plugin to label did not return a valid plugin id. '
                           'If the plugin was created before SDK version 0.4.0, '
                           'please consider upgrading your plugin.')
                sys.exit(1)

            try:
                # Label the image using the plugin info that we have previously retrieved from the image saved to disk
                tag_version, tag_latest = _label_plugin_with_plugininfo(tmp_plugin_image,
                                                                        plugin_info,
                                                                        api_version,
                                                                        args.target_name,
                                                                        agent_build_args,
                                                                        build_agent=args.build_agent)
            except Exception as e:
                _log_error('Could not label plugin due: ' + str(e))
                sys.exit(1)

            log_labels(tag_version, tag_latest)
            print(tag_latest)
        finally:
            _log('Removing temporary build image')
            if args.build_agent == 'buildah':
                _run(['buildah', 'rmi', tmp_plugin_image])
            elif args.build_agent == 'docker' or args.build_agent == 'podman':
                _run([args.build_agent, 'image', 'rm', tmp_plugin_image])
            else:
                _log_error(f"build_agent has mutated and is not 'buildah', 'docker' or 'podman' "
                           f'but was {args.build_agent}')
                sys.exit(1)


if __name__ == '__main__':
    main()
