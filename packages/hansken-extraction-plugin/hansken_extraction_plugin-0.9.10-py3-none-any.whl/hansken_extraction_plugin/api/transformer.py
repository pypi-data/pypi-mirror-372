"""
This module contains the Transformer class that holds the function reference of the transformer.

Instances of this class are constructed by BaseExtractionPlugin when retrieving transformers dynamically.
It also validates whether the method to which @transformer is applied adheres to the requirements of a transformer.
"""

from datetime import datetime
import inspect
from typing import Mapping, Sequence

from hansken.util import GeographicLocation, Vector

from hansken_extraction_plugin.api.plugin_info import TransformerLabel
from hansken_extraction_plugin.utility.type_conversion import get_type_name


class Transformer:
    """
    A transformer is an exposed method of a plugin that can be executed remotely outside extraction-time.

    This allows for on-demand analysis during an investigation.
    """

    """
    This dictionary holds the supported types that transformer methods can as arguments and return types.

    The keys are the supported Python types and the values the generic type names as in the Hansken trace model.
    Note that these types should also be defined in _primitive_matchers in runtime.pack for successful serialization.
    In order to not create circular dependencies and separate the runtime module and the api module this is defined
    separately here.
    """
    supported_primitives = {bytes: 'binary',
                            bool: 'boolean',
                            int: 'integer',
                            float: 'real',
                            str: 'string',
                            datetime: 'date',
                            GeographicLocation: 'latLong',
                            Vector: 'vector',
                            Sequence: 'list',
                            Mapping: 'map'}

    def __init__(self, function):
        """Create a transformer and validate whether the passed function meets the requirements."""
        self.function = function

        # Retrieve the signature so that we can validate whether it complies to the transformer requirements.
        signature = inspect.signature(function)

        # Validate that @transformer was applied to a function/method and not any other type of object (i.e. a class)
        if not function.__class__.__name__ == 'function':
            raise Exception('@transformer was applied to something other than a function/method. '
                            '@transformer may only be applied to methods of classes derived from BaseExtractionPlugin.')

        # Validate that @transformer was applied to a method instead of a function.
        if '.' not in function.__qualname__:
            raise Exception(
                '@transformer was applied to a function instead of a method of a class derived from '
                'BaseExtractionPlugin. '
                '@transformer may only be applied to methods of classes derived from BaseExtractionPlugin.')

        # Extract the method name for ease of use.
        self.method_name = function.__qualname__.split('.')[1]

        # Validate if this function is not a static method.
        # Note: This is not entirely foolproof since the self parameter may officially also be named differently or as
        # a non-first argument.
        if 'self' not in signature.parameters:
            raise Exception('@transformer may not be applied to static methods.')

        # Validate all the parameters and store them.
        self.parameters = {}
        for parameter in signature.parameters.values():

            # Other than validating the self property we don't include it in the parameters field because we do not
            # want to expose it externally.
            # Note: This check is not fool-proof since parameters called self can be defined as non-first parameters.
            if parameter.name == 'self':
                if parameter.annotation is not inspect.Parameter.empty:
                    raise Exception('@transformer methods should have a parameter self without a type annotation.')
                else:
                    continue

            # Validate if annotations are present on each parameter.
            if parameter.annotation is inspect.Parameter.empty:
                raise Exception('The parameters of @transformer methods must have type hints.')

            # Validate that parameters do not have default values.
            if parameter.default is not inspect.Parameter.empty:
                raise Exception('@transformer methods are currently not allowed to have parameters with a '
                                'default value.')

            # Do not allow variable arguments or positional only arguments.
            if parameter.kind in [parameter.POSITIONAL_ONLY, parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD]:
                raise Exception('@transformer methods are currently not allowed to have positional only parameters or '
                                'variable parameters (like *args and **kwargs).')

            # Validate if a parameter is one of the supported serializable types.
            if parameter.annotation not in Transformer.supported_primitives.keys():
                raise Exception(f'The parameters of @transformer methods should be one of '
                                f'{[get_type_name(x) for x in Transformer.supported_primitives]}')

            self.parameters[parameter.name] = parameter.annotation

        # Validate if the return annotation is present and one of the supported serializable types.
        if signature.return_annotation not in Transformer.supported_primitives.keys():
            raise Exception(f'The return type of @transformer methods should be one of '
                            f'{[get_type_name(x) for x in Transformer.supported_primitives.keys()]}')

        self.return_type = signature.return_annotation

    def generate_label(self) -> TransformerLabel:
        """
        Generate a TransformerLabel given the transformer method. TransformerLabels are used in PluginInfo objects.

        Unlike Transformers TransformerLabels can be serialized and sent to a client that wishes to call a transformer.
        The specific Python types are converted to the generic types that are used in the Hansken trace model.
        """
        # Convert the parameters to a generic Hansken parameter names.
        # No checks are needed here because they are already performed upon initialization of a Transformer.
        parameters = {name: self.supported_primitives[param_type] for name, param_type in self.parameters.items()}
        return_type = self.supported_primitives[self.return_type]
        return TransformerLabel(method_name=self.method_name,
                                parameters=parameters,
                                return_type=return_type)
