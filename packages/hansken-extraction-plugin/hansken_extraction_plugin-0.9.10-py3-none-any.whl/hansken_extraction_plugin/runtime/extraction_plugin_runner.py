"""
Implementation of the api using ``Hansken.py``.

All api calls are translated to ``Hansken.py`` calls.
"""
from io import BufferedReader, BufferedWriter, TextIOBase
import re
from re import Match
from typing import Any, Callable, cast, Dict, List, Literal, Mapping, Optional, Tuple, Union

from hansken.abstract_trace import AbstractTrace
from hansken.query import And, HQLHuman, Term
from hansken.remote import ProjectContext
from hansken.tool import run
from hansken.trace import image_from_trace, Trace, TraceBuilder
from logbook import Logger  # type: ignore

from hansken_extraction_plugin.api.data_context import DataContext
from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin, DeferredExtractionPlugin, \
    DeferredMetaExtractionPlugin, ExtractionPlugin, MetaExtractionPlugin
from hansken_extraction_plugin.api.extraction_trace import ExtractionTrace, ExtractionTraceBuilder, SearchTrace, \
    Tracelet
from hansken_extraction_plugin.api.search_result import SearchResult
from hansken_extraction_plugin.api.search_sort_option import SearchSortOption
from hansken_extraction_plugin.api.trace_searcher import SearchScope, TraceSearcher
from hansken_extraction_plugin.api.transformation import Transformation
from hansken_extraction_plugin.runtime.common import validate_update_arguments

log = Logger(__name__)

# \s* optional spaces
# (\w+)? optional logical operator
# \s* optional spaces
# \$data\.(\w+) data property
# (["\'][^"\']+["\']|[^\s]+) -> data value (value or value within quotes)
data_matcher_pattern = re.compile(r'\s*(\w+)?\s*\$data\.(\w+)\s*=\s*(["\'][^"\']+["\']|[^\s]+)', re.IGNORECASE)


class HanskenPyExtractionTraceBuilder(ExtractionTraceBuilder):
    """
    Helper class that wraps a trace from ``Hansken.py`` in a ExtractionTraceBuilder.

    Delegates all calls to the wrapped hansken py trace builder.
    """

    def __init__(self, builder: TraceBuilder):
        """
        Initialize a TraceBuilder.

        :param builder: hansken.py tracebuilder. All calls are delegated to this object.
        """
        self._hanskenpy_trace_builder = builder
        self._tracelet_properties: List[Tracelet] = []
        self._transformations: Dict[str, List[Transformation]] = {}

    def update(self, key_or_updates=None, value=None, data=None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTrace.get`."""
        if data is not None:
            for stream_name in data:
                self._hanskenpy_trace_builder.add_data(stream=stream_name, data=data[stream_name])

        if key_or_updates is not None or value is not None:
            validate_update_arguments(key_or_updates, value)
            self._hanskenpy_trace_builder.update(key_or_updates, value)

        return self

    def add_tracelet(self,
                     tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> 'ExtractionTraceBuilder':
        """
        Override :meth: `ExtractionTraceBuilder.add_tracelet`.

        Log an error because ``Hansken.py`` does not yet support adding tracelets.
        """
        # TODO HANSKEN-15372 Extraction plugin tracelet support FVT via REST API
        if isinstance(tracelet, Tracelet) and not value:
            self._tracelet_properties.append(tracelet)
        elif isinstance(tracelet, str) and value:
            self._tracelet_properties.append(Tracelet(tracelet, value))
        else:
            raise TypeError('invalid arguments for adding tracelet, '
                            'need either tracelet type and value or Tracelet object')

        log.error("PluginRunner doesn't support add_tracelet over REST API, Tracelet {} will be dropped",
                  tracelet.name if isinstance(tracelet, Tracelet) else tracelet)
        return self

    def add_transformation(self, data_type: str, transformation: Transformation) -> 'ExtractionTraceBuilder':
        """
        Override :meth: `ExtractionTraceBuilder.add_transformation`.

        Log an error because ``Hansken.py`` does not yet support adding transformations.
        """
        # TODO HBACKLOG-399 Add datadescriptors to REST API
        log.error("PluginRunner doesn't support add_transformation over REST API, Transformation is dropped")
        if not data_type:
            raise ValueError('data_type is required')
        if transformation is None:
            raise ValueError('transformation is required')
        self._transformations.setdefault(data_type, []).append(transformation)
        return self

    def child_builder(self, name: Optional[str] = None) -> 'ExtractionTraceBuilder':
        """Override :meth: `ExtractionTraceBuilder.child_builder`."""
        return HanskenPyExtractionTraceBuilder(self._hanskenpy_trace_builder.child_builder(name))

    def open(self, data_type: Optional[str] = None, offset: int = 0, size: Optional[int] = None,
             mode: Literal['rb', 'wb', 'w', 'wt'] = 'rb', encoding='utf-8', buffer_size: Optional[int] = None) \
            -> Union[BufferedReader, BufferedWriter, TextIOBase]:
        """Override :meth: `ExtractionTrace.open`."""
        raise ValueError('You are calling open() on a child trace builder, which is currently not supported.'
                         'Reading and writing streamed data does not work for child traces that have not yet been '
                         'created. If you want this please create a ticket on the Hansken backlog. '
                         'Note that it is possible to write small amounts of data non-streamingly using the update '
                         'function.')

    def build(self) -> str:
        """Override :meth: `ExtractionTraceBuilder.get`."""
        return self._hanskenpy_trace_builder.build()


class HanskenPyExtractionTrace(ExtractionTrace):
    """
    Helper class that wraps a trace from ``Hansken.py`` in a ExtractionTrace.

    We delegate all calls of the abstract class Mapping to the ``Hansken.py`` trace,
    since ``Hansken.py`` does a lot of tricks to get things working.
    """

    def __init__(self, trace: AbstractTrace, data_context: DataContext):
        """
        Initialize an ExtractionTrace.

        :param trace: all mapping calls are delegated to this ``Hansken.py`` trace
        :param data_context: ``Hansken.py`` data_context used to perform rest calls
        """
        self._hanskenpy_trace = trace
        self._new_properties: Dict[str, Any] = {}
        self._tracelet_properties: List[Tracelet] = []
        self._transformations: Dict[str, List[Transformation]] = {}
        self._data_context = data_context

    def update(self, key_or_updates=None, value=None, data=None) -> None:
        """Override :meth: `ExtractionTrace.update`."""
        if data is not None:
            self._hanskenpy_trace.update(data=data)

        if key_or_updates is not None or value is not None:
            validate_update_arguments(key_or_updates, value)
            self._hanskenpy_trace.update(key_or_updates, value, overwrite=True)
            updates = key_or_updates

            if isinstance(key_or_updates, str):
                updates = {key_or_updates: value}

            # update does not add the new properties to the trace _source, so
            # keep track of them here, so that we can return them when someone calls get(new_property)
            for name, value in updates.items():
                self._new_properties[name] = value

    def add_tracelet(self,
                     tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> None:
        """
        Override :meth: `ExtractionTrace.add_tracelet`.

        Log an error because ``Hansken.py`` does not yet support adding tracelets.
        """
        # TODO HANSKEN-15372 Extraction plugin tracelet support FVT via REST API
        if isinstance(tracelet, Tracelet) and not value:
            self._tracelet_properties.append(tracelet)
        elif isinstance(tracelet, str) and value:
            self._tracelet_properties.append(Tracelet(tracelet, value))
        else:
            raise TypeError('invalid arguments for adding tracelet, '
                            'need either tracelet type and value or Tracelet object')

        log.error("PluginRunner doesn't support add_tracelet over REST API, Tracelet {} will be dropped",
                  tracelet.name if isinstance(tracelet, Tracelet) else tracelet)

    def add_transformation(self, data_type: str, transformation: Transformation) -> None:
        """
        Override :meth: `ExtractionTrace.add_transformation`.

        Log an error because ``Hansken.py`` does not yet support adding transformations.
        """
        # TODO HBACKLOG-399 Add datadescriptors to REST API
        log.error("PluginRunner doesn't support add_transformation over REST API, Transformation is dropped")
        if not data_type:
            raise ValueError('data_type is required')
        if transformation is None:
            raise ValueError('transformation is required')
        self._transformations.setdefault(data_type, []).append(transformation)

    def open(self, data_type: Optional[str] = None, offset: int = 0, size: Optional[int] = None,
             mode: Literal['rb', 'wb', 'w', 'wt'] = 'rb', encoding: Optional[str] = 'utf-8',
             buffer_size: Optional[int] = None) \
            -> Union[BufferedReader, BufferedWriter, TextIOBase]:
        """
        Override :meth: `ExtractionTrace.open`.

        Note: For hansken.py, modes 'wb', 'w', and 'wt' are not supported.
        """
        if mode in ['wb', 'w', 'wt']:
            raise ValueError(f'Mode "{mode}" is not supported when running extraction plugins with hansken.py.')
        return self._hanskenpy_trace.open(stream=self._data_context.data_type, offset=offset, size=size)

    def child_builder(self, name: Optional[str] = None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTrace.child_builder`."""
        return HanskenPyExtractionTraceBuilder(self._hanskenpy_trace.child_builder(name))

    def get(self, key, default=None) -> Any:
        """Override :meth: `Trace.get`."""
        return self._new_properties[key] if key in self._new_properties else self._hanskenpy_trace.get(key, default)


class HanskenPySearchTrace(SearchTrace):
    """SearchTrace implementation that forwards all calls to a ``Hansken.py`` trace."""

    def __init__(self, trace: AbstractTrace):
        """
        Initialize a SearchTrace.

        :param trace: ``Hansken.py`` trace to forward all calls to
        """
        self._hanskenpy_trace = trace

    def open(self, stream='raw', offset=0, size=None, buffer_size=None) -> BufferedReader:
        """Override :meth: `SearchTrace.open`."""
        return self._hanskenpy_trace.open(stream=stream, offset=offset, size=size)

    def get(self, key, default=None):
        """Override :meth: `Trace.get`."""
        return self._hanskenpy_trace.get(key, default)


class HanskenPySearchResult(SearchResult):
    """SearchResult implementation that wraps the searchresult from ``Hansken.py`` so sdk SearchTraces are returned."""

    def __init__(self, result):
        """
        Initialize a SearchResult.

        :param result: ``Hansken.py`` search result to wrap
        """
        self._result = result

    def __iter__(self):
        return map(HanskenPySearchTrace, self._result.__iter__())

    def total_results(self) -> int:
        """Override :meth: `SearchResult.total_results`."""
        return self._result.num_results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Override :meth: `SearchResult.close`.

        The provided hansken py search result needs to be closed explicitly.
        """
        self._result.close()


class HanskenPyTraceSearcher(TraceSearcher):
    """TraceSearcher implementation that forwards search requests to ``Hansken.py``."""

    def __init__(self, h_py_context: ProjectContext, image_id: str):
        """
        Initialize a TraceSearcher.

        :param h_py_context: ``Hansken.py`` ExtractionContext to perform the required REST calls
        """
        self.h_py_context = h_py_context
        self._image_id = image_id

    def search(self, query: str, count: Optional[int] = None, scope: Union[str, SearchScope] = SearchScope.image,
               start: int = 0, sort: list[SearchSortOption] = [SearchSortOption()]) -> SearchResult:
        """Override :meth: `TraceSearcher.search`."""
        if scope == SearchScope.image:
            query = And(Term('image', self._image_id), HQLHuman(query))

        result = self.h_py_context.search(query=query, start=start, count=count)
        return HanskenPySearchResult(result)


class _PluginRunner:
    """Helper class that allows an Extraction Plugin to be executed with ``Hansken.py``."""

    def __init__(self, extraction_plugin_class: Callable[[], BaseExtractionPlugin]):
        """
        Initialize a PluginRunner.

        :param extraction_plugin_class: callable returning an instance of the extraction plugin to run
        """
        self._extraction_plugin_class = extraction_plugin_class

    def run(self, context: ProjectContext):
        """
        Run the extraction plugin.

        :param context: most plugin calls will be forwarded to this ``Hansken.py`` extraction data_context.
        """
        log.info('PluginRunner is running plugin class {}', self._extraction_plugin_class.__name__)
        plugin = self._extraction_plugin_class()
        _run_plugin(context, plugin)


def _run_plugin(context: ProjectContext, plugin: BaseExtractionPlugin):
    query, data_stream_property, data_stream_value = _split_matcher(plugin.plugin_info().matcher)
    if not isinstance(plugin, (MetaExtractionPlugin, DeferredMetaExtractionPlugin)) and not data_stream_property:
        raise ValueError('Matcher contains not exactly one "$data.property = value" expression (hint: if your plugin '
                         'does not process trace data streams, change the plugin type to MetaExtractionPlugin or'
                         'DeferredMetaExtractionPlugin).')

    with context:
        if not data_stream_property:
            for trace in context.search(query):
                _process(context, plugin, trace, data_type=None)

        # Hansken does not support HQL lite $data queries, so all traces must be checked to see if they match
        # the $data query. If the $data query satisfies, the process method is called.
        elif data_stream_property == 'type':
            # special case: type is not a data stream property, but a key
            for trace in context.search(query):
                if data_stream_value in trace.data_types:
                    _process(context, plugin, trace, data_stream_value)

        else:
            # check which data stream(s) match the data-matcher
            for trace in context.search(query):
                for data_type in trace.data_types:
                    if trace.get(f'data.{data_type}.{data_stream_property}') == data_stream_value:
                        _process(context, plugin, trace, data_type)


def _process(project_context: ProjectContext, plugin: BaseExtractionPlugin, trace: Trace, data_type: Optional[str]):
    if isinstance(plugin, DeferredExtractionPlugin) and data_type:
        data_context = DataContext(data_type, trace.get(f'data.{data_type}.size'))
        # Note: The HanskenPyTraceSearcher needs a project_context to make REST calls to Hansken
        # Not the data_context, which describes data.
        searcher = HanskenPyTraceSearcher(project_context, image_from_trace(trace))
        cast(DeferredExtractionPlugin, plugin).process(HanskenPyExtractionTrace(trace, data_context),
                                                       data_context,
                                                       searcher)
    elif isinstance(plugin, ExtractionPlugin) and data_type:
        data_context = DataContext(data_type, trace.get(f'data.{data_type}.size'))
        cast(ExtractionPlugin, plugin).process(HanskenPyExtractionTrace(trace, data_context), data_context)
    elif isinstance(plugin, MetaExtractionPlugin):
        data_context = DataContext('meta', 0)
        cast(MetaExtractionPlugin, plugin).process(HanskenPyExtractionTrace(trace, data_context))
    elif isinstance(plugin, DeferredMetaExtractionPlugin):
        data_context = DataContext('meta', 0)
        searcher = HanskenPyTraceSearcher(project_context, image_from_trace(trace))
        cast(DeferredMetaExtractionPlugin, plugin).process(HanskenPyExtractionTrace(trace, data_context), searcher)
    else:
        raise ValueError(f'${type(plugin).__name__} is not a valid Extraction Plugin')


def _split_matcher(matcher: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Split a matcher string into three parts; query, data_property and data_value.

    query: everything before $data.<property> = value
    data_property: data property after $data.
    data_value: expression after $data.<property> =

    It requires the $data.<property> = expression to be at the END of the string.
    Example::

        $data.type = raw
        $data.mimeType = image/png
        $data.mimeClass = "Text UTF-8"
        A AND B AND C AND $data.type = raw
        A AND B AND C AND $data.mimeType = image/png
        A AND B AND C AND $data.mimeClass = "Text UTF-8"

    :param matcher: the HQL matcher of this plugin + the $data.type suffix
    :return: A tuple containing the HQL query (before the $data.<property> = expression,
             the data property and the data expression.
    """
    matches: List[Match] = [*data_matcher_pattern.finditer(matcher)]

    if not matches:
        return matcher, None, None

    if len(matches) > 1:
        raise ValueError('only a single $data.property = value matcher is supported when using the Hansken.py '
                         'extraction plugin runner')

    match = matches[0]
    start_position, end_position = match.span()
    operator, data_property, data_value = match.groups()
    if end_position < len(matcher):
        raise ValueError('"$data.property = value" is not at the end of the matcher.')
    elif operator and operator.upper() != 'AND':
        raise ValueError(f'The {operator} operator precedes the "$data.property = value" expression. '
                         f'Only the AND operator is supported.')
    else:
        query = matcher[0:start_position] if start_position > 0 else None
        return query, data_property, data_value.strip('\'"')  # remove quotes if present


def run_with_hanskenpy(extraction_plugin_class: Callable[[], BaseExtractionPlugin], **defaults):
    """
    Run an Extraction Plugin as a script on a specific project, using ``Hansken.py``.

    An Extraction Plugin as scripts is executed against a Hansken server, on a project that already has been extracted.

    extraction_plugin_class: Class of the extraction plugin implementation
    """
    runner = _PluginRunner(extraction_plugin_class)
    run(with_context=runner.run, **defaults)
