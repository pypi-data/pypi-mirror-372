"""
This module contains a script that outputs the plugin info of an extraction plugin to either a file or to the console.

It is used during the build and label process in combination with the build_plugin_ci utility to generate a
plugin-info.json file inside the extraction plugin image. This file can then later be extracted from the image to label
the plugin without having to start the plugin making it easier to build and label it in CI pipelines.
"""
import argparse
from dataclasses import asdict
import json
import sys

from hansken_extraction_plugin.framework import GRPC_API_VERSION
from hansken_extraction_plugin.runtime.reflection_util import get_plugin_class, ReflectionError


def main():
    """Output the plugin info of an extraction plugin to a file or the console in JSON format."""
    parser = argparse.ArgumentParser(prog='plugin_info',
                                     usage='%(prog)s PLUGIN (Use -h for help)',
                                     description='Output the plugin info of a plugin to a file in JSON format')
    parser.add_argument('--output', '-o',
                        help='Output the plugin info to the specified file.',
                        default='plugin-info.json',
                        required=False)
    parser.add_argument('--console', '-c',
                        help='Print the plugin info to STDOUT instead of outputting it to a file.',
                        action='store_true')
    parser.add_argument('plugin',
                        metavar='PLUGIN',
                        help='Either the path of the python file or an object reference of the plugin to be served.')
    arguments = parser.parse_args()

    try:
        # Load the plugin module/class dynamically so that we can extract the plugin information.
        plugin_class = get_plugin_class(arguments.plugin)
    except ReflectionError as e:
        print(f'Failed to load plugin: {e}')
        sys.exit(1)

    # Instantiate the plugin in order to retrieve the plugin information.
    plugin = plugin_class()
    plugin_info = plugin.plugin_info()

    # Dynamically generate the transformers of this plugin.
    plugin_info.transformers = [(t.generate_label()) for t in plugin.transformers]

    # Create a dictionary that holds the plugin information and the (grpc) API version of the plugin.
    plugin_info_dict = {
        'api-version': GRPC_API_VERSION,
        'plugin-info': asdict(plugin_info)
    }

    # Pretty print the plugin info to the console as JSON or output it to a file.
    output = json.dumps(plugin_info_dict, indent=4, default=str)
    if arguments.console:
        print(output, file=sys.stdout)
    else:
        with open(arguments.output, 'w') as file:
            file.write(output)


if __name__ == '__main__':
    main()
