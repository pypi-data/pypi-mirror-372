"""
This module contains the different types of Extraction Plugins.

The types of Extraction Plugins differ in their process functions.
"""
from abc import ABC, abstractmethod
import inspect
from typing import List

from hansken_extraction_plugin.api.data_context import DataContext
from hansken_extraction_plugin.api.extraction_trace import ExtractionTrace, MetaExtractionTrace
from hansken_extraction_plugin.api.plugin_info import PluginInfo
from hansken_extraction_plugin.api.trace_searcher import TraceSearcher
from hansken_extraction_plugin.api.transformer import Transformer
from hansken_extraction_plugin.decorators.transformer import transformer_registry


class BaseExtractionPlugin(ABC):
    """All Extraction Plugins are derived from this class."""

    @abstractmethod
    def plugin_info(self) -> PluginInfo:
        """Return information about this extraction plugin."""

    @property
    def transformers(self) -> List[Transformer]:
        """
        Dynamically retrieves the transformer methods that were decorated with @transform.

        Note: This method will retrieve transformers for superclasses as well.
        """
        # Retrieve all super classes of a plugin so that we can also retrieve transformers of super classes.
        # Note: This also contains the more specific instance this method might be called on as well.
        base_classes = inspect.getmro(self.__class__)

        # Check for each (super) class of the plugin if transformers have been registered.
        transformers = [
            transformer for cl in base_classes
            if cl.__name__ in transformer_registry
            for transformer in transformer_registry[cl.__name__]
        ]

        return transformers


class ExtractionPlugin(BaseExtractionPlugin):
    """Default extraction plugin, that processes a trace and one of its datastreams."""

    @abstractmethod
    def process(self, trace: ExtractionTrace, data_context: DataContext):
        """
        Process a given trace.

        This method is called for every trace that is processed by this tool.

        :param trace: Trace that is being processed
        :param data_context: Data data_context describing the data stream that is being processed
        """


class MetaExtractionPlugin(BaseExtractionPlugin):
    """Extraction Plugin that processes a trace only with its metadata, without processing its data."""

    @abstractmethod
    def process(self, trace: MetaExtractionTrace):
        """
        Process a given trace.

        This method is called for every trace that is processed by this tool.

        :param trace: Trace that is being processed
        """


class DeferredExtractionPlugin(BaseExtractionPlugin):
    """
    Extraction Plugin that can be run at a different extraction stage.

    This type of plugin also allows accessing other traces using the searcher.
    """

    @abstractmethod
    def process(self, trace: ExtractionTrace, data_context: DataContext, searcher: TraceSearcher):
        """
        Process a given trace.

        This method is called for every trace that is processed by this tool.

        :param trace: Trace that is being processed
        :param data_context: Data data_context describing the data stream that is being processed
        :param searcher: TraceSearcher that can be used to obtain more traces
        """


class DeferredMetaExtractionPlugin(BaseExtractionPlugin):
    """
    Extraction Plugin that can be postponed to a later extraction iteration.

    This type of plugin processes a trace only with its metadata,
    without processing its data and accesses traces using the searcher.
    """

    @abstractmethod
    def process(self, trace: MetaExtractionTrace, searcher: TraceSearcher):
        """
        Process a given trace.

        This method is called for every trace that is processed by this tool.

        :param trace: Trace that is being processed
        :param searcher: TraceSearcher that can be used to obtain more traces
        """
