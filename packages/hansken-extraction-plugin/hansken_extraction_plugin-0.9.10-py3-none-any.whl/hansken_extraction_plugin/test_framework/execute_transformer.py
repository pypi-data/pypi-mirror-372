#!/usr/bin/python3
"""Execute a transformer function of a running extraction plugin."""
import argparse
from typing import Any, Dict, List
import uuid

from google.protobuf.empty_pb2 import Empty
from hansken.util import Vector
from more_itertools import first

from hansken_extraction_plugin.api.plugin_info import TransformerLabel
from hansken_extraction_plugin.buildkit.color_log import _log, colored_logging
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcTransformerRequest
from hansken_extraction_plugin.framework.ExtractionPluginService_pb2_grpc import ExtractionPluginServiceStub
from hansken_extraction_plugin.runtime import pack, unpack
from hansken_extraction_plugin.runtime.extraction_plugin_server import validate_transformer_arguments
from hansken_extraction_plugin.test_framework.validator import DockerTestPluginRunner
from hansken_extraction_plugin.utility.terminal_arg_parser import arg_to_python


def _transform(running_plugin: ExtractionPluginServiceStub, request: RpcTransformerRequest) -> Vector:
    """Connect and execute grpc request to transform function of a running extraction plugin."""
    _log('Executing transformer')
    transformer_response = running_plugin.transform(request)
    return unpack.transformer_response(transformer_response)


def _named_arguments_dict(named_arguments: List[str]) -> Dict[str, str]:
    """
    Convert a list of parameter argument pairs to a dictionary of named arguments.

    For example: [a, b, c, '5'] -> {'a': 'b', 'c': '5'}
    """
    if len(named_arguments) < 2:
        raise ValueError('At least one pair of arguments is required.')
    if len(named_arguments) % 2 != 0:
        raise ValueError('Uneven number of arguments, arguments should come in pairs.')

    parameters = named_arguments[0::2]
    arguments = named_arguments[1::2]
    return dict(zip(parameters, arguments))


def _retrieve_transformers(running_plugin: ExtractionPluginServiceStub) -> List[TransformerLabel]:
    plugin_info, _ = unpack.plugin_info(running_plugin.pluginInfo(request=Empty()))
    transformers = plugin_info.transformers
    _log(f'Available transformers: {transformers}')
    return transformers


def _expected_signature(available_transformers: List[TransformerLabel], method_name: str) -> TransformerLabel:
    transformer = first(
        (transformer for transformer in available_transformers
         if transformer.method_name == method_name),
        default=None
    )

    if transformer is None:
        available_transformer_names = [transformer.method_name for transformer in available_transformers]
        raise ValueError(f'Transformer {method_name} is not available in this plugin. The following transformers are '
                         f'available: {", ".join(available_transformer_names)}')
    return transformer


def _transform_request(expected_args: Dict[str, str], provided_args: Dict[str, str], method_name: str) \
        -> RpcTransformerRequest:
    validate_transformer_arguments(
        set(expected_args.keys()),
        set(provided_args.keys()),
        method_name
    )

    return pack.transformer_request(
        method_name=method_name,
        arguments=_args_to_python(expected_args, provided_args)
    )


def _args_to_python(expected_args: Dict[str, str], provided_args: Dict[str, str]) -> Dict[str, Any]:
    return {
        name: arg_to_python(expected_args[name], argument)
        for name, argument in provided_args.items()
    }


def main():
    """Execute transformer function of an extraction plugin."""
    with colored_logging('Executor'):
        parser = argparse.ArgumentParser(prog='execute_transformer',
                                         usage='%(prog)s [options]',
                                         description='A script to execute a transformer of a running plugin.')
        parser.add_argument('docker_image', help='Docker image containing the plugin.')
        parser.add_argument('method_name', type=str, help='Method name of the transformer to execute.')
        parser.add_argument('arguments', type=str, nargs='+',
                            help='Pairs of named arguments to provide to the transformer function; e.g. weight 15.')
        parser.add_argument('-t', '--timeout', default=30.0, type=float,
                            help='Time (in seconds) the framework has to wait for the Docker container to be ready.')

        args = parser.parse_args()

        method_name = args.method_name
        named_arguments = _named_arguments_dict(args.arguments)

        plugin_runner = DockerTestPluginRunner(args.docker_image, args.timeout)
        # Start the plugin as Docker container and invoke a transformer with the provided arguments.
        container = f'executing_transformer_{uuid.uuid4()}'
        with plugin_runner.run_and_connect(container_name=container) as plugin_service_stub:
            available_transformers = _retrieve_transformers(plugin_service_stub)
            transformer_signature = _expected_signature(available_transformers, method_name)
            request = _transform_request(transformer_signature.parameters, named_arguments, method_name)
            result = _transform(plugin_service_stub, request)
        print(f'Result of transform function: \n\n{result}')


if __name__ == '__main__':
    main()
