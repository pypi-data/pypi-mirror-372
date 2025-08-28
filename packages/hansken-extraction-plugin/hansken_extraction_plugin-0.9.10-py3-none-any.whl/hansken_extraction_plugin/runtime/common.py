"""Contains utilities that are used both by runner and server implementations."""

from typing import Mapping


def validate_update_arguments(key_or_updates, value):
    """
    Validate the arguments for update(...).

    :param key_or_updates: either a `str` (the metadata property to be
                           updated) or a mapping supplying both keys and values to be updated
    :param value: the value to update metadata property *key* to (used
                  only when *key_or_updates* is a `str`, an exception will be thrown
                  if *key_or_updates* is a mapping)
    :param data: a `dict` mapping data type / stream name to bytes to be
                 added to the trace
    :raises:
        TypeError: if the acutal input is in an incorrect format.
    """
    if not isinstance(key_or_updates, str) and not isinstance(key_or_updates, Mapping):
        raise TypeError('argument `key_or_updates` should be either a str or mapping')

    if isinstance(key_or_updates, str) and value is None:
        raise TypeError('update with key missing value')

    if isinstance(key_or_updates, Mapping) and value is not None:
        raise TypeError('update with Mapping should not have argument value set')
