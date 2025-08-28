"""
This module contains the transformer decorator that can be used to mark a method as a transformer method.

See the transformer decorator itself for more details on the requirements of a transformer method.
"""
from hansken_extraction_plugin.api.transformer import Transformer

# All transformers will be temporarily stored in the transformer registry because the transformer decorator runs before
# the plugin class, in which the transformer method is defined, is fully declared, making it impossible to store the
# transformers directly in the plugin. The key is a class_name and the value is a list of transformers.
transformer_registry = {}


def transformer(function):
    """
    Register a method of an extraction plugin as a transformer.

    A transformer is an exposed method of a plugin that can be executed remotely outside extraction-time.
    This allows for on-demand analysis during an investigation.

    A transformer should adhere to the following requirements:
    1. It may only be applied on (non-static) methods of an extraction plugin
    (classes derived from BaseExtractionPlugin)
    2. The parameters and return value of the transformer method must be one of the defined types in
    `api.serializable_primitives`.
    3. The parameters of a transformer method must not be variable (`*args` or `**kwargs`) or positional only.
    4. The parameters of a transformer may not have a default value.
    """
    # Retrieve the class name from the whole method name (i.e. MyPlugin.transformer_method)
    class_name = function.__qualname__.split('.')[0]

    # Create and validate if the transformer adheres to the requirements.
    tf = Transformer(function)

    # Store all transformer functions in the registry ordered by class.
    if class_name not in transformer_registry:
        transformer_registry[class_name] = []
    transformer_registry[class_name].append(tf)

    # Just return the unwrapped function after we've registered this function since there is no need to modify
    # run-time behavior.
    return function
