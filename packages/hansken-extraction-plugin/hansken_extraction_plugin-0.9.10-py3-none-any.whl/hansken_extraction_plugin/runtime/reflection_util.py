"""Helper methods to find out more about the class of a plugin."""
import importlib.util
import inspect
import os
import sys
from types import ModuleType
from typing import Any, Type

from logbook import Logger  # type: ignore

from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin

log = Logger(__name__)


class ReflectionError(Exception):
    """A reflection error raised with a user-friendly error message."""

    def __init__(self, message):
        """
        Create a ReflectionError.

        Args:
            message: the message shown to the user
        """
        super().__init__(message)


def is_abstract(cls: Type) -> bool:
    """
    Verify if provided class is abstract.

    An abstract class has a __abstractmethods__ property containing a set of
    abstract method names. See https://www.python.org/dev/peps/pep-3119/.

    :param cls: class that may be abstract
    :returns: true if class is abstract
    """
    if hasattr(cls, '__abstractmethods__'):
        return len(cls.__abstractmethods__) > 0
    return False


def _get_plugin_class_from_module(module: ModuleType) -> Type:
    # Loop over all classes found in the pluginFile. The first class that is a subclass of ExtractionPlugin
    # or MetaExtractionPlugin will be the pluginClass that is served.
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if issubclass(cls, BaseExtractionPlugin) and not is_abstract(cls):
            log.info(f'Plugin class found: {cls}')
            return cls

    raise ReflectionError(f'No Extraction Plugin class found in module {module.__name__}')


def _get_plugin_class_from_reference(reference: str) -> Type:
    # Reference to object adapted from https://packaging.python.org/en/latest/specifications/entry-points/#data-model
    modname, qualname_separator, qualname = reference.partition(':')
    module = importlib.import_module(modname)
    if qualname_separator:
        # There's a separator, resolve the latter part to a value / type
        obj: Any = module
        for attr in qualname.split('.'):
            obj = getattr(obj, attr)

        return obj
    else:
        # No separator, reference to a module, resolve that in the same was as if it were loaded from file
        return _get_plugin_class_from_module(module)


def _get_plugin_class_from_file(plugin_file: str) -> Type:
    log.info(f'Looking for a plugin in {plugin_file}')
    if not os.path.isfile(plugin_file):
        raise ReflectionError(f'File not found or path is directory: {plugin_file}')

    if not plugin_file.endswith('.py'):
        raise ReflectionError(f'Not a python file: {plugin_file}')

    # Import the plugin_file into code
    spec = importlib.util.spec_from_file_location('plugin_module', plugin_file)
    if not spec:
        raise ReflectionError(f'No Extraction Plugin class found in {plugin_file} (spec could not loaded)')

    module = importlib.util.module_from_spec(spec)
    if not module or not module.__file__:
        raise ReflectionError(f'No Extraction Plugin class found in {plugin_file} (module could not loaded)')

    # add the plugin path to sys.path, to let 'relative' imports in a plugin work
    sys.path.append(os.path.dirname(os.path.abspath(module.__file__)))

    sys.modules['plugin_module'] = module
    spec.loader.exec_module(module)  # type: ignore
    return _get_plugin_class_from_module(module)


def get_plugin_class(file_or_reference: str) -> Type:
    """
    Retrieve the parent class of a plugin contained in the provided file.

    :param file_or_reference: either the path of the python source file that should contain a Extraction Plugin class
           definition or an object reference to be resolved into an Extraction Plugin class
    :returns: the first class that is found in file_or_reference that is a subclass of ExtractionPlugin or
              MetaExtractionPlugin.
    """
    try:
        return _get_plugin_class_from_file(file_or_reference)
    except (ReflectionError, ImportError) as e_file:
        log.debug(
            f'Loading Plugin from {file_or_reference} as file failed, retrying as object reference',
            exc_info=e_file
        )

    try:
        return _get_plugin_class_from_reference(file_or_reference)
    except (ReflectionError, ImportError, AttributeError) as e_reference:
        log.debug(
            f'Loading Plugin from {file_or_reference} as object reference failed',
            exc_info=e_reference
        )

    # When required Python language level reaches 3.11+, this could be made into an ExceptionGroup referencing both
    # e_file and e_reference
    raise ReflectionError(f'No Extraction Plugin class found in either file or reference {file_or_reference}')
