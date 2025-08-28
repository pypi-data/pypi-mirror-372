"""Contains utility functions to parse strings provided by command line to their python counterparts."""
from datetime import datetime
import json
from json import JSONDecodeError
from typing import Any, Dict, List

from hansken.trace import CONVERTERS
from hansken.util import INVALID_DATE

from hansken_extraction_plugin.api.transformer import Transformer

deserializers = {
    # use same deserializer as hansken.py
    'binary': CONVERTERS['binary'].deserialize,
    # convert any capitalization of true to True, else False
    'boolean': lambda value: value.lower() == 'true',
    'integer': lambda value: int(value),
    'real': lambda value: float(value),
    'string': lambda value: value,
    # use same deserializer as hansken.py
    'date': lambda value: _datetime_to_python(value),
    # use same deserializer as hansken.py
    'latLong': lambda value: CONVERTERS['latLong'].deserialize(value),
    # use same deserializer as hansken.py
    'vector': lambda value: CONVERTERS['vector'].deserialize(value),
    'list': lambda value: _list_to_python(value),
    'map': lambda value: _map_to_python(value),
}


def arg_to_python(expected_type: str, argument: str) -> Any:
    """Convert a string argument into a Transformer compatible Python object."""
    primitives = Transformer.supported_primitives.values()
    if expected_type not in primitives:
        raise ValueError(f'Type {expected_type} is not supported.')

    return deserializers[expected_type](argument)


def _datetime_to_python(argument: str) -> datetime:
    converter = CONVERTERS.get('date')
    deserialized = converter.deserialize(argument)
    if deserialized is INVALID_DATE:
        raise ValueError(f'Invalid iso8601 date {argument}.')
    return deserialized


def _list_to_python(argument: str) -> List[str]:
    # use the json library to parse lists. this method does not vereify t.
    try:
        return json.loads(argument)
    except JSONDecodeError:
        raise ValueError(f'Invalid argument {argument}. Make sure the provided list consists of double quoted '
                         f'strings; e.g. ["ex1", "ex2"].')


def _map_to_python(argument: str) -> Dict[str, str]:
    # use the json library to parse lists. If the result is not a list of strings, this should be catched later.
    try:
        return json.loads(argument)
    except JSONDecodeError:
        raise ValueError(f'Invalid argument {argument}. Make sure the provided map consists of double quoted key, '
                         f'value pairs; eg. {"key", "value"}.')
