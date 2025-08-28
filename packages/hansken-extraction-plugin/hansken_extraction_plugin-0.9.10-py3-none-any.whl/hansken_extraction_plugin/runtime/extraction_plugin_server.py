"""Implementation of the api using generated gRPC code."""
from array import array
from collections import defaultdict, deque
from concurrent import futures
from contextlib import contextmanager
from dataclasses import dataclass, field
from io import BufferedReader, BufferedWriter, RawIOBase, TextIOBase, TextIOWrapper
from mmap import mmap
from queue import Queue
from signal import SIGINT, signal, SIGTERM
import threading
import time
import traceback
from typing import Any, Callable, cast, DefaultDict, Dict, Generator, Iterator, List, Literal, Mapping, NoReturn, \
    Optional, Set, Tuple, Type, Union

from google.protobuf.any_pb2 import Any as GrpcAny
import grpc
from logbook import Logger  # type: ignore

from hansken_extraction_plugin import __version__ as api_version
from hansken_extraction_plugin.api.data_context import DataContext
from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin, DeferredExtractionPlugin, \
    DeferredMetaExtractionPlugin, ExtractionPlugin, MetaExtractionPlugin
from hansken_extraction_plugin.api.extraction_trace import ExtractionTrace, ExtractionTraceBuilder, SearchTrace, \
    Tracelet
from hansken_extraction_plugin.api.search_result import SearchResult
from hansken_extraction_plugin.api.search_sort_option import SearchSortOption
from hansken_extraction_plugin.api.trace_searcher import SearchScope, TraceSearcher
from hansken_extraction_plugin.api.transformation import Transformation
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcPluginInfo, RpcRandomAccessDataMeta, \
    RpcSearchTrace, RpcTrace, RpcTransformerRequest, RpcTransformerResponse
from hansken_extraction_plugin.framework.ExtractionPluginService_pb2_grpc import \
    add_ExtractionPluginServiceServicer_to_server, ExtractionPluginServiceServicer
from hansken_extraction_plugin.framework.Health_pb2 import HealthCheckResponse
from hansken_extraction_plugin.framework.Health_pb2_grpc import add_HealthServicer_to_server, HealthServicer
from hansken_extraction_plugin.framework.RpcCallMessages_pb2 import RpcFinish, RpcRead, RpcSearchResult, RpcStart, \
    RpcSync
from hansken_extraction_plugin.runtime import pack, unpack
from hansken_extraction_plugin.runtime.common import validate_update_arguments
from hansken_extraction_plugin.runtime.constants import DEFAULT_READ_WRITE_BUFFER_SIZE, MAX_CHUNK_SIZE, MAX_MESSAGE_SIZE
from hansken_extraction_plugin.runtime.grpc_raw_io import _GrpcRawIO
from hansken_extraction_plugin.runtime.pack import transformer_response
from hansken_extraction_plugin.utility.type_conversion import get_type_name

MAX_UNSYNCED_REQUESTS = 1000

NUM_TRACE_WORKERS = 16
NUM_STATUS_WORKERS = 2

log = Logger(__name__)


class GrpcExtractionTraceBuilder(ExtractionTraceBuilder):
    """
    Helper class that implements a trace builder that was exchanged with the gRPC protocol.

    This trace will only be created in Hansken when `.build` is called. No gRPC message is sent before `.build` is
    called
    """

    def __init__(self, grpc_handler: 'ProcessHandler', trace_id: str, name: Optional[str]):
        """
        Initialize a builder.

        :param grpc_handler: ProcessHandler that handles gRPC requests.
        :param trace_id: string representing the internal id of this trace.
        :param name: name of this trace. Can be added later using `.update`, but a name is required before building a
                     trace.
        """
        self._grpc_handler = grpc_handler
        self._trace_id = trace_id
        self._next_child_id = 0
        self._types: Set[str] = set()
        self._properties: Dict[str, object] = {}
        self._tracelets: List[Tracelet] = []
        self._transformations: Dict[str, List[Transformation]] = {}
        self._has_been_built = False
        self._datas: Dict[str, bytes] = {}

        if name:
            self.update('name', name)

    def get(self, key: str, default=None):
        """Retrieve property corresponding to a provided key from this trace."""
        return self._properties[key] if key in self._properties else default

    def update(self, key_or_updates=None, value=None, data=None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTraceBuilder.update`."""
        if key_or_updates is not None:
            types, properties = _extract_types_and_properties(self._properties, key_or_updates, value)
            self._types.update(types)
            self._properties.update(properties)
        if data is not None:
            for data_type in data:
                if data_type in self._datas:
                    raise RuntimeError(f'data with type {data_type} already exists on this trace')
            self._datas = data
        return self

    def add_tracelet(self,
                     tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> 'ExtractionTraceBuilder':
        """Override :meth: `ExtractionTraceBuilder.add_tracelet`."""
        if isinstance(tracelet, Tracelet) and not value:
            self._tracelets.append(tracelet)
        elif isinstance(tracelet, str) and value:
            self._tracelets.append(Tracelet(tracelet, value))
        else:
            raise TypeError('invalid arguments for adding tracelet, '
                            'need either tracelet type and value or Tracelet object')
        return self

    def add_transformation(self, data_type: str, transformation: Transformation) -> 'ExtractionTraceBuilder':
        """Override :meth: `ExtractionTraceBuilder.add_transformation`."""
        if not data_type:
            raise ValueError('data_type is required')
        if transformation is None:
            raise ValueError('transformation is required')
        self._transformations.setdefault(data_type, []).append(transformation)
        return self

    def child_builder(self, name: Optional[str] = None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTraceBuilder.child_builder`."""
        if not self._has_been_built:
            raise RuntimeError('parent trace has not been built before creating a child')
        return GrpcExtractionTraceBuilder(self._grpc_handler, self._get_next_child_id(), name)

    def open(self, data_type: Optional[str] = None, offset: int = 0, size: Optional[int] = None,
             mode: Literal['rb', 'wb', 'w', 'wt'] = 'rb', encoding: Optional[str] = None,
             buffer_size: Optional[int] = None) \
            -> Union[BufferedReader, BufferedWriter, TextIOBase]:
        """Override :meth: `ExtractionTrace.open`."""
        raise ValueError('You are calling open() on a child trace builder, which is currently not supported.'
                         'Reading and writing streamed data does not work for child traces that have not yet been '
                         'created. If you want this please create a ticket on the Hansken backlog. '
                         'Note that it is possible to write small amounts of data non-streamingly using the update '
                         'function.')

    def build(self) -> str:
        """Override :meth: `ExtractionTraceBuilder.build`."""
        self._grpc_handler.begin_child(self._trace_id, self.get('name'))
        self._flush()
        self._grpc_handler.write_datas(self._trace_id, self._datas)
        self._grpc_handler.finish_child(self._trace_id)
        self._has_been_built = True
        return self._trace_id

    def _get_next_child_id(self):
        """
        Compute the next id of a child of this trace.

        Note that this may not be the same id the remote uses, as this is computed after the trace is build.
        """
        next_id = self._trace_id + '-' + str(self._next_child_id)
        self._next_child_id = self._next_child_id + 1
        return next_id

    def _flush(self):
        log.debug('Flushing trace builder {}', self._trace_id)
        # remove name property as it was already given through self._grpc_handler#begin_child
        # and the properties are cleared anyway (and flush is only called when the child is built)
        del self._properties['name']
        self._grpc_handler.enrich_trace(self._trace_id,
                                        self._types,
                                        self._properties,
                                        self._tracelets,
                                        self._transformations)
        self._types.clear()
        self._properties.clear()


@dataclass(frozen=True)
class GrpcDataContext(DataContext):
    """Class that extends a DataContext that also could hold the first bytes of the data it represents."""

    first_bytes: bytes = field(compare=False)
    """
    The first bytes of the data stream currently being processed.
    This could be `None` or an empty bytes. This does not imply that there is no data, but it means that the client
    did not send data to fill a data cache. Use `data_size` to verify the presence of data.
    """


class GrpcExtractionTrace(ExtractionTrace):
    """Helper class that exposes a trace that was exchanged with the gRPC protocol."""

    def __init__(self, grpc_handler: 'ProcessHandler', trace_id: str, properties: Dict[str, Any],
                 data_context: Optional[GrpcDataContext], tracelets: List[Tracelet],
                 transformations: Dict[str, List[Transformation]]):
        """
        Initialize an GrpcExtractionTrace.

        :param grpc_handler: ProcessHandler that can be used to perform gRPC requests.
        :param trace_id: string representing the id of this trace.
        :param properties: key, value mapping of all known properties of this trace.
        :param data_context: data_context used to retrieve information about the offered data stream. This argument is
                             not required when running a MetaExtractionPlugin.
        :param tracelets: the tracelets of the trace.
        :param transformations: the data transformations of the trace.
        """
        self._grpc_handler = grpc_handler
        self._trace_id = trace_id
        self._properties = properties
        self._data_context = data_context
        self._tracelets = tracelets
        self._transformations = transformations
        self._next_child_id = 0
        self._new_types: Set[str] = set()
        self._new_properties: Dict[str, object] = {}

    def get(self, key: str, default=None):
        """Override :meth: `Trace.get`."""
        return self._properties[key] if key in self._properties else default

    def update(self, key_or_updates=None, value=None, data=None) -> None:
        """Override :meth: `ExtractionTrace.update`."""
        if key_or_updates is not None:
            types, properties = _extract_types_and_properties(self._properties, key_or_updates, value)
            self._new_types.update(types)
            self._new_properties.update(properties)
            self._properties.update(properties)
        if data is not None:
            self._grpc_handler.write_datas(self._trace_id, data)

    def add_tracelet(self, tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> None:
        """Override :meth: `ExtractionTrace.add_tracelet`."""
        if isinstance(tracelet, Tracelet) and not value:
            self._tracelets.append(tracelet)
        elif isinstance(tracelet, str) and value:
            self._tracelets.append(Tracelet(tracelet, value))
        else:
            raise TypeError('invalid arguments for adding tracelet, '
                            'need either tracelet type and value or Tracelet object')

    def add_transformation(self, data_type: str, transformation: Transformation) -> None:
        """Override :meth: `ExtractionTrace.add_transformation`."""
        if not data_type:
            raise ValueError('data_type is required')
        if transformation is None:
            raise ValueError('transformation is required')
        self._transformations.setdefault(data_type, []).append(transformation)

    def open(self, data_type: Optional[str] = None, offset: int = 0, size: Optional[int] = None,
             mode: Literal['rb', 'wb', 'w', 'wt'] = 'rb', encoding: Optional[str] = None,
             buffer_size: Optional[int] = None) \
            -> Union[BufferedReader, BufferedWriter, TextIOBase]:
        """Override :meth: `ExtractionTrace.open`."""
        if mode not in ['rb', 'w', 'wt', 'wb']:
            raise ValueError(f'Mode "{mode}" is not supported, supported modes: rb, w, wt, and wb.')

        if mode == 'rb':
            if not self._data_context:
                raise RuntimeError('Trying to read data from a trace that has no data.')
            if data_type is not None:
                raise ValueError('Argument data_type is not supported for mode "rb".')
            if encoding:
                raise ValueError('Encoding should not be set for mode "rb".')
            return BufferedReader(self._get_reader(self._data_context, offset, size),
                                  buffer_size=buffer_size or DEFAULT_READ_WRITE_BUFFER_SIZE)

        # generic checks for all write-modes
        if offset != 0:
            raise ValueError(f'Offsets other than 0 are not supported for mode "{mode}".')
        if size is not None:
            raise ValueError(f'Argument size is not supported for mode "{mode}".')

        if mode == 'wb':
            if encoding:
                raise ValueError(f'Encoding should not be set for mode "{mode}", it can only be set for mode "w"')
            binary_writer = self._get_writer(data_type or 'raw', encoding=None)
            buffered_binary_writer = BufferedWriter(binary_writer,
                                                    buffer_size=buffer_size or DEFAULT_READ_WRITE_BUFFER_SIZE)
            return buffered_binary_writer

        if mode == 'w' or mode == 'wt':
            binary_writer = self._get_writer(data_type or 'raw', encoding=encoding or 'utf-8')
            buffered_binary_writer = BufferedWriter(binary_writer,
                                                    buffer_size=buffer_size or DEFAULT_READ_WRITE_BUFFER_SIZE)
            return TextIOWrapper(buffered_binary_writer, write_through=True)  # write_through:rely on writers own buffer

        raise NotImplementedError('mode "{mode}" is not yet implemented')

    def _get_reader(self, data_context: GrpcDataContext, offset: int = 0, size: Optional[int] = None) -> RawIOBase:
        data_size = data_context.data_size
        first_bytes = data_context.first_bytes
        if offset < 0 or offset > data_size:
            raise ValueError('Invalid value for offset')
        if size is None:
            size = data_size

        def read_from_known_trace(offset, size) -> GrpcAny:
            return self._grpc_handler.read(offset=offset, size=size, trace_uid=self._trace_id,
                                           data_type=data_context.data_type)

        return _GrpcRawIO(read_from_known_trace, offset, size, first_bytes)

    def _get_writer(self, data_type: str, encoding: Optional[str]) -> RawIOBase:
        return self._grpc_handler.writer(self._trace_id, data_type, encoding)

    def child_builder(self, name: Optional[str] = None) -> ExtractionTraceBuilder:
        """Override :meth: `ExtractionTrace.child_builder`."""
        return GrpcExtractionTraceBuilder(self._grpc_handler, self._get_next_child_id(), name)

    def _get_next_child_id(self):
        next_id = self._trace_id + '-' + str(self._next_child_id)
        self._next_child_id = self._next_child_id + 1
        return next_id

    def _flush(self):
        """Send all new updates on this trace to the client side."""
        log.debug('Flushing trace builder {}', self._trace_id)

        if not self._has_changes():
            return

        self._grpc_handler.enrich_trace(self._trace_id,
                                        self._new_types,
                                        self._new_properties,
                                        self._tracelets,
                                        self._transformations)
        self._new_types = []
        self._new_properties = {}

    def _has_changes(self) -> bool:
        if self._new_types or self._new_properties or self._tracelets or self._transformations:
            return True
        return False

    def __eq__(self, other):
        if not isinstance(other, GrpcExtractionTrace):
            return False

        return self._properties == other._properties


class BatchedSearchResult(SearchResult):
    """
    Implementation of a SearchResult that can get new results when needed.

    Since it retrieves the results in batches it is not restricted to any limits.
    Implements the SearchResult interface.
    """

    def __init__(self, query: str, count: Optional[int], handler: 'ProcessHandler',
                 scope: Union[str, SearchScope] = SearchScope.image, start: int = 0,
                 sort: list[SearchSortOption] = [SearchSortOption()]):
        """
        Initialize this SearchResult.

        :param query:   HQL-query used for searching
        :param count:   Maximum number of traces to return
        :param handler: A ProcessHandler, which forwards all request through gRPC
        :param scope:   Select search scope: 'image' to search only search for other traces within the image of the
                        trace that is being processed, or 'project' to search in the scope of the full project
                        (either Scope-enum value can be used, or the str-values directly).
        :param start:   Starting index of traces to return
        :param sort:    The fields and directions to sort on
        """
        self._count = count
        self._handler = handler
        self._query = query
        self._scope = scope
        self._sort = sort

        self._trace_list: deque[SearchTrace] = deque()
        self._total_results = 0
        self._trace_index = start
        self._results_gotten = 0

        self._fetch_next_batch()

    def total_results(self) -> int:
        """Override :meth: `SearchResult.total_results`."""
        return self._total_results

    def _unpack_search_trace(self, rpc_trace: RpcSearchTrace) -> SearchTrace:
        """Create a SearchTrace from an RpcSearchTrace."""
        properties = unpack.trace_properties(rpc_trace.properties)
        datas = {data.type: data for data in rpc_trace.data}
        return GrpcSearchTrace(grpc_handler=self._handler, trace_id=rpc_trace.id, properties=properties,
                               meta_datas=datas)

    def _fetch_next_batch(self):
        """Fetch the next batch of results from the handler."""
        if self._count is None:
            # Since we do not know the length the first iteration, just get as many as possible
            num_results_to_get = self._handler.SEARCH_REQUEST_COUNT_LIMIT
        elif self._results_gotten >= self._count:
            num_results_to_get = 0
        else:
            num_results_to_get = min(self._handler.SEARCH_REQUEST_COUNT_LIMIT, self._count - self._trace_index)

        if num_results_to_get <= 0 and self._total_results:  # _total_results is set after first iteration.
            return

        try:
            search_result = self._handler.search_traces(self._query, num_results_to_get, self._scope, self._trace_index,
                                                        self._sort)

            result: RpcSearchResult = unpack.any(search_result, RpcSearchResult)
            self._trace_list = deque([self._unpack_search_trace(rpc_trace) for rpc_trace in result.traces])

            if self._count is None:
                self._count = result.totalResults
            if not self._total_results:
                self._total_results = result.totalResults

            # Adjust _count if it exceeds _total_results
            if self._count > self._total_results:
                self._count = self._total_results
        except Exception as e:
            raise RuntimeError('Failed to fetch new search results') from e

    def __iter__(self):
        count = self._total_results if self._count is None else self._count
        while self._results_gotten < count:
            if not self._trace_list:
                self._fetch_next_batch()
            else:
                # If there are traces get the first and update the index and result count accordingly
                self._trace_index += 1
                self._results_gotten += 1
                yield self._trace_list.popleft()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _extract_types_and_properties(existing_properties: Union[Mapping, str], key_or_updates: Union[Mapping, str],
                                  value=None) -> Tuple[set, dict]:
    """
    Get the new types and properties defined by given 'key_or_updates' and 'value' properties.

    See `api.ExtractionTrace.update` for more information about their format.
    If a property was already set, an error is thrown (validated against 'existing_properties')

    :param existing_properties: the properties which were already set
    :param key_or_updates: the update key or mapping
    :param value: the update value in case 'key_or_updates' was a str
    :return: a tuple of a set of the types, and a mapping of the properties
    """
    validate_update_arguments(key_or_updates, value)

    types = set()
    properties = {}

    updates: Mapping[Any, Any]
    if isinstance(key_or_updates, str):
        updates = {key_or_updates: value}
    else:
        updates = key_or_updates

    for name, value in updates.items():
        if name in existing_properties:
            log.warning('property {} has already been set', name)

        # preview & name are intrinsic types, so DO NOT add them
        if name == 'name' or name.startswith('preview.'):
            properties[name] = value
        elif '.' not in name:
            raise RuntimeError(f"property '{name}' format is invalid, "
                               f'a dot (.) between the type and the property is missing')
        else:
            # determine type from property name
            type = name[0:name.find('.')]

            # add type and property to list of new types
            types.add(type)
            properties[name] = value

    return types, properties


def _create_trace(grpc_handler: 'ProcessHandler', rpc_trace: RpcTrace, data_context: Optional[GrpcDataContext]) -> \
        GrpcExtractionTrace:
    """Convert an RpcTrace into a GrpcExtractionTrace."""
    id, types, properties, tracelets, transformations = unpack.trace(rpc_trace)
    return GrpcExtractionTrace(grpc_handler=grpc_handler,
                               trace_id=id,
                               properties=properties,
                               data_context=data_context,
                               tracelets=tracelets,
                               transformations=transformations)


class GrpcSearchTrace(SearchTrace):
    """Helper class that exposes a SearchTrace that was exchanged with the gRPC protocol."""

    def __init__(self, grpc_handler: 'ProcessHandler', trace_id: str, properties: Dict[str, Any],
                 meta_datas: Mapping[str, RpcRandomAccessDataMeta]):
        """
        Initialize this SearchTrace.

        :param grpc_handler: ProcessHandler used to perform gRPC calls.
        :param trace_id: string representing the id of this trace.
        :param properties: key, value mapping of all known properties of this trace.
        :param meta_datas: Mapping of data_type to MetaData objects representing all data streams associated with this
                           trace.
        """
        self._properties = properties
        self._grpc_handler = grpc_handler
        self._trace_id = trace_id
        self._meta_datas = meta_datas

    def get(self, key: str, default=None):
        """Override :meth: `Trace.get`."""
        return self._properties[key] if key in self._properties else default

    def open(self, stream='raw', offset=0, size=None, buffer_size=None) -> BufferedReader:
        """Override :meth: `SearchTrace.open`."""
        if not self._meta_datas:
            raise ValueError(f'Opening trace data "{stream} failed: this trace has no data streams.')

        if stream not in self._meta_datas:
            raise ValueError(f'Opening trace data "{stream}" failed: this stream is not available on this trace. "'
                             f'Available streams are {", ".join(self._meta_datas)}.')

        data_meta = self._meta_datas[stream]
        if offset < 0 or offset > data_meta.size:
            raise ValueError('Invalid value for offset')
        if size is None or offset + size > data_meta.size:
            size = data_meta.size - offset  # max available bytes

        def read_from_known_trace(offset: int, size: int) -> GrpcAny:
            return self._grpc_handler.read(offset=offset, size=size, trace_uid=self.get('uid'), data_type=stream)

        return BufferedReader(_GrpcRawIO(read_from_known_trace, offset, size, data_meta.firstBytes),
                              buffer_size=buffer_size or DEFAULT_READ_WRITE_BUFFER_SIZE)


class GrpcTraceSearcher(TraceSearcher):
    """Helper class that allows searching for traces using gRPC."""

    def __init__(self, handler: 'ProcessHandler'):
        """Initialize using a ProcessHandler, which forwards all request through gRPC."""
        self._handler = handler

    def search(self, query: str, count: Optional[int] = None, scope: Union[str, SearchScope] = SearchScope.image,
               start: int = 0, sort: list[SearchSortOption] = [SearchSortOption()]) -> SearchResult:
        """Override :meth: `TraceSearcher.search`."""
        return BatchedSearchResult(query, count, self._handler, scope, start, sort)


class GrpcWriter(RawIOBase):
    """Class that writes data to a gRPC connection."""

    def __init__(self, trace_id: str, data_type: str, handler: 'ProcessHandler', encoding: Optional[str] = None):
        """
        Initialize this writer.

        :param trace_id: trace id of the trace the data will belong to
        :param data_type: data type to write.
        :param handler: ProcessHandler used to perform gRPC calls.
        :param encoding: TODO
        """
        self._trace_id = trace_id
        self._data_type = data_type
        self._handler = handler
        self._position = 0

        """Send a start message to indicate we will start writing data to the client."""
        start_message = pack.begin_writing(self._trace_id, self._data_type, encoding)
        self._handler.handle_message(start_message)

    def close(self):
        """Close this writer."""
        if not super().closed:
            finish_message = pack.finish_writing(self._trace_id, self._data_type)
            self._handler.handle_message(finish_message)
            super().close()

    def seekable(self):
        """Return if the writer is seekable."""
        return False

    def readable(self):
        """Return if the writer can read."""
        return False

    def writable(self):
        """Return if the writer can write."""
        return True

    def tell(self) -> int:
        """Return the current position."""
        return self._position

    def write(self, buffer: Union[bytes, bytearray, memoryview, array, mmap], /) -> int:  # type: ignore
        # type of buffer should be collections.abc.Buffer (Python 3.12 forward)
        """
        Write data to gRPC stream.

        This method sends data in separate chunks if it does not fit in one message.
        """
        if isinstance(buffer, memoryview):
            data = buffer.tobytes()
        elif isinstance(buffer, bytes):
            data = buffer
        elif isinstance(buffer, bytearray):
            data = bytes(buffer)
        elif isinstance(buffer, BufferedReader):
            return self._write_from_buffer(buffer)  # recursive call back to write
        elif isinstance(buffer, mmap):
            return self._write_from_mmap(buffer)  # recursive call back to write
        else:
            raise ValueError('Writing data from ' + str(type(buffer)) + ' is currently not supported!')

        size = len(data)
        position = 0
        while position < size:
            write_count = min(size - position, MAX_CHUNK_SIZE)
            data_message = pack.write_data(self._trace_id, self._data_type, data[position:position + write_count])
            self._handler.handle_message(data_message, force_sync=True)
            position += write_count
            self._position += write_count
        return size

    def _write_from_buffer(self, reader: BufferedReader) -> int:
        """
        Write data to gRPC stream.

        This method sends data in separate chunks if it does not fit in one message. A reusable buffer is used.
        """
        # allocate a reusable buffer
        buffer = memoryview(bytearray(MAX_CHUNK_SIZE))
        num_written = 0
        # keep filling the buffer until it runs out
        while (num_read := reader.readinto(buffer)) > 0:
            # write the appropriate chunk of the buffer
            num_written += self.write(buffer[:num_read])
        return num_written

    def _write_from_mmap(self, reader: mmap) -> int:
        """
        Write data to gRPC stream.

        This method sends data in separate chunks if it does not fit in one message. Note that for each write a new
        buffer is created, which might cause many buffers being allocated and deallocated during the read / write loop.
        """
        count = 0
        read_bytes: bytes = reader.read(MAX_CHUNK_SIZE)
        count += len(read_bytes)
        while len(read_bytes) > 0:
            self.write(read_bytes)
            read_bytes = reader.read(MAX_CHUNK_SIZE)
            count += len(read_bytes)
        return count


def _profile(name: str):
    """
    Add the number of invocations and method durations to the profiled metrics.

    :param name: a pretty name to add to the profiler

    :return: the decorator
    """
    def decorator_profile(func):
        def wrapper_profile(self, *args, **kwargs):
            self._profile[f'{name}_count'] += 1
            start = time.perf_counter()
            result = func(self, *args, **kwargs)
            self._profile[f'{name}_duration'] += (time.perf_counter() - start)
            return result
        return wrapper_profile
    return decorator_profile


class ProcessHandler:
    """
    Handles the bidirectional gRPC stream returned by the process method.

    The response iterator allows reading responses sent by the hansken client
    """

    SEARCH_REQUEST_COUNT_LIMIT = 50

    # if the request queue contains this sentinel, it indicates that no more items can be expected
    _sentinel = object()

    def __init__(self, response_iterator: Iterator[GrpcAny]):
        """
        Initialize this handler.

        :param response_iterator: Iterator returned by the gRPC framework containing client responses. If we wish to
                                  wait for a client message, call ``next(response_iterator)``.
        """
        log.debug('Creating a new GRPC process handler')
        # requests is a simple queue, all messages added to this queue are
        # sent to the client over gRPC. The zero indicates that this is an unbound queue
        self._requests: Queue[GrpcAny] = Queue(0)

        # gRPC responses are returned to this iterator
        self._response_iterator = response_iterator

        # stack trace ids, representing the current depth first pre-order scope, in order to translate it to in-order
        # the reason for this is that traces are not sent as soon as one is built (using TraceBuilder#build),
        # because the python API expects each parent trace to be built before their children
        # whereas the gRPC API expects a child to be finished before the parent
        self._trace_stack: List[str] = []

        # profile metrics to evaluate plugin performance for individual traces
        self._profile: DefaultDict[str, Union[int, float]] = defaultdict(int)

        self._unsynced_requests = 0

    def _handle_request(self, request) -> GrpcAny:
        """Block call, send a message to the client, and return its reply."""
        self.handle_message(request)
        return next(self._response_iterator)

    def handle_message(self, message: Any, force_sync=False, force_skip_sync=False):
        """
        Send a message to the client.

        :param message: gRPC any message
        :param force_sync: send a general purpose sync request after this message, so the plugin will block
                     until the client has processed the message
        :param force_skip_sync: skip the sync mechanism, usually used to prevent sending any syncs after a stream is
                     closed
        """
        self._requests.put_nowait(pack.any(message))
        if not force_skip_sync:
            self._sync(force_sync=force_sync)

    def write_datas(self, trace_id: str, data: Mapping[str, bytes]):
        """
        Write all given data streams to the remote for a given trace id.

        :param trace_id: id of the trace to attach data streams
        :param data: mapping from data type to bytes
        """
        for data_type in data:
            self.write_data(trace_id, data_type, data[data_type])

    def write_data(self, trace_id: str, data_type: str, data: bytes):
        """
        Write a single data stream to the client for a given trace id using a GrpcWriter.

        :param trace_id: id of the trace
        :param data_type: type of the data streams
        :param data: the actual data
        """
        with GrpcWriter(trace_id, data_type, self) as writer:
            writer.write(data)

    def writer(self, trace_id: str, data_type: str, encoding: Optional[str]) -> RawIOBase:
        """
        Return a RawIOBase that can be used to stream data to a trace.

        :param trace_id: id of the trace
        :param data_type: type of the data streams
        :param encoding: set the encoding of bytes, optional for text writes
        """
        return GrpcWriter(trace_id, data_type, self, encoding)

    # TODO HANSKEN-15467 Trace Enrichment: pass a trace instead of 5 parameters
    @_profile('rpc_enrich')
    def enrich_trace(self, trace_id: str, types: List[str], properties: Dict[str, Any],
                     tracelets: List[Tracelet], transformations: Dict[str, List[Transformation]]):
        """
        Send a gRPC message to enrich a trace with given properties, types and tracelets.

        :param trace_id: id of the trace
        :param types: types to enrich the trace with
        :param properties: properties to send
        :param tracelets: tracelets to add
        :param transformations: transformations to add
        """
        log.debug('Process handler enriches trace {} with properties {}', trace_id, properties.keys())
        self._assert_correct_trace(trace_id)
        request = pack.trace_enrichment(trace_id, types, properties, tracelets, transformations)
        self.handle_message(request)

    @_profile('rpc_read')
    def read(self, offset: int, size: int, trace_uid: str, data_type: str) -> GrpcAny:
        """
        Send a request to the client to read a single chunk of data from a specific data stream.

        :param offset: byte offset to start reading
        :param size: size of the data chunk
        :param trace_uid: uid of the trace the data stream is associated with
        :param data_type: type of the data
        :return: GrpcAny message containing the data
        """
        log.debug('Reading trace with offset {} and size {} and id {} and type {}', offset, size, trace_uid, data_type)
        self._profile['rpc_read_size'] += size
        rpc_read: RpcRead = pack.rpc_read(offset, size, trace_uid, data_type)
        return self._handle_request(rpc_read)

    @_profile('rpc_search')
    def search_traces(self, query: str, count: int, scope: Union[str, SearchScope], start: int,
                      sort: list[SearchSortOption]) -> GrpcAny:
        """
        Send a request to the client to search for traces.

        :param query: return traces matching this query
        :param count: maximum number of traces to return
        :param scope: scope search to image or project
        :param start: starting offset
        :param sort:  search fields and directions
        :return: GrpcAny message containing a `SearchResult`
        """
        # TODO: HANSKEN-15066 support search results of indefinite size
        if count > self.SEARCH_REQUEST_COUNT_LIMIT:  # safety check to fit answers into one gRPC message
            raise RuntimeError(f'search request count must not exceed the limit of '
                               f'{self.SEARCH_REQUEST_COUNT_LIMIT}')
        log.debug('Searching for {} additional traces', count)
        rpc_search_request = pack.rpc_search_request(query, count, scope, start, sort)
        return self._handle_request(rpc_search_request)

    @_profile('rpc_begin_child')
    def begin_child(self, trace_id: str, name: str) -> None:
        """
        Send a message to the client indicating that we are building a new child.

        Update the internal trace stack to stay aware on which child trace we are working.

        :param trace_id: id of the child trace
        :param name: name of the trace
        """
        log.debug('Process handler is beginning child trace {}', trace_id)
        while self._trace_stack and not self._is_direct_parent(self._trace_stack[-1], trace_id):
            # finish all out of scope traces
            self.handle_message(pack.finish_child(self._trace_stack.pop()))

        request = pack.begin_child(trace_id, name)
        self.handle_message(request)
        self._trace_stack.append(trace_id)

    def _sync(self, force_sync=False):
        if force_sync or self._unsynced_requests > MAX_UNSYNCED_REQUESTS:
            self._unsynced_requests = 0
            self._handle_request(RpcSync())
        else:
            self._unsynced_requests += 1

    @_profile('rpc_finish_child')
    def finish_child(self, trace_id: str) -> None:
        """
        Indicate that we finished building a child trace.

        :param trace_id: id of the child trace.
        """
        log.debug('Process handler is finishing child trace {}', trace_id)
        self._assert_correct_trace(trace_id)
        # not yet flushing here, because the python API stores parent before child (pre-order),
        # but the client expects the other way around (in-order)

    def finish(self):
        """Let the client know the server has finished processing this trace."""
        log.debug('Process handler is finishing processing.')
        try:
            request = RpcFinish(profile=pack.pack_profile(self._profile))
            self.handle_message(request, force_skip_sync=True)
        finally:
            self._finish()

    def finish_with_error(self, exception):
        """Let the client know an exception occurred while processing this trace."""
        log.warning('Finishing processing with an exception:', exc_info=True)
        try:
            rpc_partial_finish = pack.partial_finish_with_error(exception, self._profile)
            self.handle_message(rpc_partial_finish, force_skip_sync=True)
        except Exception:
            # nothing more we can do now...  this is a last-resort catch to (hopefully) get the word out we're done
            log.warning('An exception occurred while reporting an error to the client')
            log.debug('with the following exception', exc_info=True)
        finally:
            # but do try to finish and let the client know it's over
            self._finish()

    def _finish(self):
        """Try to finish with the sentinel."""
        log.debug('Finish by putting the sentinel on the request queue')
        self._requests.put_nowait(self._sentinel)

    def iter(self) -> Iterator[GrpcAny]:
        """Return iterator object to which new messages are pushed, that can be returned to gRPC."""
        return iter(self._requests.get, self._sentinel)

    def _flush_traces(self) -> None:
        """Send all remaining finish messages for the trace ids on the id stack."""
        while self._trace_stack:
            self.handle_message(pack.finish_child(self._trace_stack.pop()))

    def _assert_correct_trace(self, trace_id: str) -> None:
        """Assert that the id passed is the one currently in scope based on the id stack."""
        if not self._trace_stack:
            # if no trace on the stack, assert that we are working on the root
            if '-' not in trace_id:
                return
            raise RuntimeError('trying to update trace {} before initializing it'.format(trace_id))
        # assert that the current trace on the top of the stack is the one we are working on
        if self._trace_stack[-1] != trace_id:
            raise RuntimeError(
                'trying to update trace {} before building trace {}'.format(trace_id, self._trace_stack[-1])
            )

    @staticmethod
    def _is_direct_parent(parent_id: str, child_id: str) -> bool:
        return child_id.startswith(parent_id) and len(parent_id) == child_id.rfind('-')

    def profile(self, name, value):
        """
        Set the value of a profiled metric.

        :param name: the name
        :param value: the value
        """
        self._profile[name] = value


class _PluginProcessSlotTracker:
    """Utility to track the number of concurrent process() calls, and to assert new calls can be made."""

    def __init__(self, max_workers: int):
        if max_workers < 1:
            raise ValueError('there should be at least one process slot')

        self._processing_max = max_workers
        self._processing_lock = threading.Lock()
        self._currently_processing = 0

    def has_available(self) -> bool:
        """Return if there are slots available for processing (True) or not (False)."""
        return self._currently_processing < self._processing_max

    def _assert_available(self, grpc_context: grpc.ServicerContext):
        if not self.has_available():
            # return RESOURCE_EXHAUSTED so client side can load balance or re-try after waiting a little
            log.info(f'[processing] got request, but already processing maximum number of traces '
                     f'({self._currently_processing} of {self._processing_max}), signalling RESOURCE_EXHAUSTED')
            grpc_context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED,
                               'already processing maximum number of traces in this plugin instance')
            # context.abort always raises an Exception (as expected)

    def take_slot_or_raise_exception(self, grpc_context: grpc.ServicerContext):
        """
        Take a processing slot.

        Asserts that a processing slot is available, and throws an gRPC RESOURCE_EXHAUSTED if all slots are currently
        taken.
        For each taken processing slot, the caller should also call a release_slot() EXACTLY ONCE.

        :param grpc_context: context used to create the RESOURCE_EXHAUSTED exception if needed
        """
        with self._processing_lock:
            self._assert_available(grpc_context)
            self._currently_processing += 1
            log.info(f'[processing] currently processing {self._currently_processing} traces '
                     f'({self._processing_max} max total)')

    def release_slot(self):
        with self._processing_lock:
            if self._currently_processing < 1:
                log.error('[processing] releasing a slot, but all have already been released!')
                return
            self._currently_processing -= 1
            log.info(f'[processing] currently processing {self._currently_processing} traces '
                     f'({self._processing_max} max total)')


class ExtractionPluginServicer(ExtractionPluginServiceServicer):
    """This is our implementation of the gRPC generated ExtractionPluginServiceServicer."""

    def __init__(self, extraction_plugin_class: Callable[[], BaseExtractionPlugin],
                 process_slots: Optional[_PluginProcessSlotTracker] = None):
        """
        Initialize this servicer.

        :param extraction_plugin_class: Method returning an instance of a BaseExtractionPlugin.
        :param process_slots: slots to be used for processing traces
        """
        self._slots = process_slots or _PluginProcessSlotTracker(NUM_TRACE_WORKERS)
        self._plugin = extraction_plugin_class()

    def pluginInfo(self, request, context: grpc.RpcContext) -> RpcPluginInfo:  # noqa: N802
        """Convert Extraction Plugin plugin info to gRPC plugininfo and returns it to the requester."""
        return pack.plugin_info(self._plugin.plugin_info(), self._plugin)

    def process(self, response_iterator: Iterator[GrpcAny], grpc_context: grpc.ServicerContext) -> Iterator[GrpcAny]:
        """
        Call the plugin process method.

        Asynchronous process method. This is where the plugin process method gets called
        in a new thread. This call will return immediately. The process thread will do the processing of the trace.
        After the thread completes, a finish message is sent to the client.

        :param response_iterator: The GRPC handler's queue iterator
        :param grpc_context: The trace data_context
        """
        self._slots.take_slot_or_raise_exception(grpc_context)

        log.debug('Handling new process-request')
        grpc_handler = ProcessHandler(response_iterator)
        try:
            self._process_trace_in_new_thread(response_iterator, grpc_handler)
        except Exception as exception:
            self._slots.release_slot()
            grpc_handler.finish_with_error(exception)
        finally:
            # Return the iterator to get the next message or the sentinel, which marks the last entry.
            return grpc_handler.iter()

    @staticmethod
    def raise_grpc_exception(exception: Exception,
                             context: grpc.ServicerContext,
                             error_type: grpc.StatusCode) -> NoReturn:
        """Construct a gRPC exception that can be used to signal the client that something went wrong."""
        # Capture the stack trace and make it available to the client to read upon throwing the exception.
        stack_trace = traceback.format_exc()
        context.set_details(f'Error: {str(exception)}\nStack Trace: {stack_trace}')

        # Sets the status code to a specific failure category to signal this to the client.
        context.set_code(error_type)

        # Raise an exception to signal the client that something has gone wrong.
        raise grpc.RpcError(exception)

    def transform(self, request: RpcTransformerRequest, grpc_context: grpc.ServicerContext) -> RpcTransformerResponse:
        """Reroutes a transformer request to the right transformer. Main entrypoint for transformer requests."""
        # Retrieve all transformer methods with this name. There might be multiple because of super classes implementing
        # a method with the same name.
        transformers = [tfm for tfm in self._plugin.transformers if tfm.method_name == request.methodName]

        # Raise an exception if no transformer with this method name is found.
        if len(transformers) == 0:
            self.raise_grpc_exception(LookupError(f'Transformer with the name {request.methodName} does not exist.'),
                                      grpc_context,
                                      grpc.StatusCode.NOT_FOUND)

        # Raise an exception if multiple transformers with this method name are found.
        if len(transformers) > 1:
            self.raise_grpc_exception(KeyError(f'Multiple transformers with the name {request.methodName}. '
                                               f'Make sure superclasses of your plugin do not already implement this '
                                               f'method.'),
                                      grpc_context,
                                      grpc.StatusCode.INTERNAL)

        # Get the only transformer that is still in the list of transformers.
        transformer = transformers.pop()

        # Compute the parameter names so that we can make sure all required parameters are provided.
        expected_parameters = set(transformer.parameters.keys())
        provided_parameters = set(request.namedArguments.keys())

        # Validate provided parameters with expected parameters
        try:
            validate_transformer_arguments(expected_parameters, provided_parameters, request.methodName)
        except ValueError as exception:
            self.raise_grpc_exception(exception,
                                      grpc_context,
                                      grpc.StatusCode.INVALID_ARGUMENT)

        # Create a dictionary of our arguments including self that we can invoke our transformer with.
        arguments: Dict[str, Any] = {'self': self._plugin}

        # Unpack all arguments containing gRPC primitives to Python primitive types.
        for (key, value) in request.namedArguments.items():
            arguments[key] = unpack.transformer_type(value)

        # Validates if the provided parameters are of the same type as the arguments required.
        for (parameter_name, parameter_type) in transformer.parameters.items():

            # We don't validate `self`, since we dynamically provide the plugin as `self`.
            if parameter_name == 'self':
                continue

            # Retrieve the argument with the same name as the parameter and validate if it has the same type.
            # We already know all arguments are present due to our previous checks.
            argument = arguments[parameter_name]

            if not issubclass(type(argument), parameter_type):
                self.raise_grpc_exception(ValueError(f'Provided argument {parameter_name} is not of type '
                                                     f'{parameter_type} but is type {get_type_name(type(argument))}'),
                                          grpc_context,
                                          grpc.StatusCode.INVALID_ARGUMENT)

        # Call the transformer with our arguments and retrieve the returned value.
        # The ** notation is used to call our function with a dictionary containing the name and value of each argument.
        try:
            response = transformer.function(**arguments)

            # Pack the return value into a response and send it back.
            return transformer_response(response)
        except Exception as e:
            self.raise_grpc_exception(e,
                                      grpc_context,
                                      grpc.StatusCode.INTERNAL)

    @staticmethod
    def _start_message_to_context(start_message: RpcStart) -> GrpcDataContext:
        return GrpcDataContext(data_type=start_message.dataContext.dataType,
                               data_size=start_message.dataContext.data.size,
                               first_bytes=start_message.dataContext.data.firstBytes)

    def _process_trace_in_new_thread(self, response_iterator: Iterator[GrpcAny], grpc_handler: ProcessHandler):
        first_message = next(response_iterator)
        if not first_message.Is(RpcStart.DESCRIPTOR):
            log.error('Expecting RpcStart, but received unexpected message: {}', first_message)
            raise RuntimeError('Expecting RpcStart message')

        start_message = unpack.any(first_message, RpcStart)

        # process in a different thread, so that we can keep this thread to send messages to the client (Hansken)
        if isinstance(self._plugin, ExtractionPlugin):
            data_context = self._start_message_to_context(start_message)
            trace = _create_trace(grpc_handler=grpc_handler, rpc_trace=start_message.trace, data_context=data_context)

            def run_process():
                cast(ExtractionPlugin, self._plugin).process(trace, data_context)

            threading.Thread(target=self._process_trace,
                             args=(run_process, trace, grpc_handler, data_context),
                             daemon=True).start()

        elif isinstance(self._plugin, MetaExtractionPlugin):
            trace = _create_trace(grpc_handler=grpc_handler, rpc_trace=start_message.trace, data_context=None)

            def run_process():
                cast(MetaExtractionPlugin, self._plugin).process(trace)

            threading.Thread(target=self._process_trace,
                             args=(run_process, trace, grpc_handler, None),
                             daemon=True).start()

        elif isinstance(self._plugin, DeferredExtractionPlugin):
            data_context = self._start_message_to_context(start_message)
            trace = _create_trace(grpc_handler=grpc_handler, rpc_trace=start_message.trace, data_context=data_context)
            searcher = GrpcTraceSearcher(grpc_handler)

            def run_process():
                cast(DeferredExtractionPlugin, self._plugin).process(trace, data_context, searcher)

            threading.Thread(target=self._process_trace,
                             args=(run_process, trace, grpc_handler, data_context),
                             daemon=True).start()

        elif isinstance(self._plugin, DeferredMetaExtractionPlugin):
            trace = _create_trace(grpc_handler=grpc_handler, rpc_trace=start_message.trace, data_context=None)
            searcher = GrpcTraceSearcher(grpc_handler)

            def run_process():
                cast(DeferredMetaExtractionPlugin, self._plugin).process(trace, searcher)

            threading.Thread(target=self._process_trace,
                             args=(run_process, trace, grpc_handler, None),
                             daemon=True).start()

        else:
            raise RuntimeError('Unsupported type of plugin: {}', str(type(self._plugin)))

    def _process_trace(self, run_process: Callable[[], None],
                       trace: GrpcExtractionTrace,
                       grpc_handler: ProcessHandler,
                       context: DataContext):
        start_time = time.perf_counter()
        try:
            self._log_start_processing(trace, context)
            run_process()
            self._flush_trace_tree(grpc_handler, trace)
            grpc_handler.profile('duration', time.perf_counter() - start_time)
            grpc_handler.finish()
            log.info('Finished processing trace with id: {}', trace._trace_id)
        except Exception as exception:
            log.exception('Error during processing trace with id: {}', trace._trace_id)
            try:
                self._flush_trace_tree(grpc_handler, trace)
            finally:
                grpc_handler.profile('duration', time.perf_counter() - start_time)
                grpc_handler.finish_with_error(exception)
        finally:
            self._slots.release_slot()

    def _log_start_processing(self, trace: GrpcExtractionTrace, context: DataContext):
        # meta data_context has no associated data stream
        if context is None:
            log.info('Started processing trace with id: {}, data type: meta', trace._trace_id)
        else:
            log.info('Started processing trace with id: {}, data type: {}, size: {}',
                     trace._trace_id,
                     context.data_type,
                     context.data_size)

    def _flush_trace_tree(self, grpc_handler: ProcessHandler, trace: GrpcExtractionTrace):
        # flush cached child traces
        grpc_handler._flush_traces()
        # flush updated information on root trace
        trace._flush()


def validate_transformer_arguments(expected_parameters: Set[str], provided_parameters: Set[str], method_name: str):
    """Compare provided with expected transformer parameters and raise a ValueError if these are not the same."""
    # Check for missing parameters by computing the difference in sets.
    missing_parameters = expected_parameters - provided_parameters
    if missing_parameters:
        raise ValueError(f'Missing parameters while calling transformer {method_name}. '
                         f'Missing: {missing_parameters}.')

    # Check for unexpected parameters that are being provided.
    unexpected_parameters = provided_parameters - expected_parameters
    if unexpected_parameters:
        raise ValueError(f'Unexpected parameters while calling transformer '
                         f'{method_name}. Unexpected: {unexpected_parameters}.')


class HealthServiceServicer(HealthServicer):
    """HealthServicer implementation to expose the plugin status."""

    def __init__(self, slots: _PluginProcessSlotTracker):
        """
        Initialize a HealthServicer.

        :param slots: slots instance to determine if we are ready to serve new process()-requests
        """
        self._slots = slots

    def _status(self):
        return HealthCheckResponse.SERVING if self._slots.has_available() else HealthCheckResponse.NOT_SERVING

    def Check(self, request, context):  # noqa: N802
        """Return SERVING status."""
        return HealthCheckResponse(status=self._status())

    def Watch(self, request, context):  # noqa: N802
        """Yield SERVING status."""
        yield HealthCheckResponse(status=self._status())


def _start_server(extraction_plugin_class: Type[BaseExtractionPlugin], address: str) -> grpc.Server:
    """
    Start extraction plugin server.

    :extraction_plugin_class: Class of the extraction plugin implementation
    :address: Address serving this server
    :return: gRPC server object
    """
    options = (('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
               ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
               ('grpc.so_reuseport', 0))
    num_trace_workers = NUM_TRACE_WORKERS
    plugin_info = extraction_plugin_class().plugin_info()
    if plugin_info.resources and plugin_info.resources.maximum_workers:
        num_trace_workers = plugin_info.resources.maximum_workers

    num_grpc_threads = num_trace_workers + NUM_STATUS_WORKERS
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=num_grpc_threads), options=options)

    process_slots = _PluginProcessSlotTracker(num_trace_workers)
    plugin_servicer = ExtractionPluginServicer(extraction_plugin_class, process_slots)
    add_ExtractionPluginServiceServicer_to_server(plugin_servicer, server)
    add_HealthServicer_to_server(HealthServiceServicer(process_slots), server)
    server.add_insecure_port(address)
    log.info('Starting GRPC Extraction Plugin server with {} workers. Listening on {}.', num_trace_workers, address)
    log.info('Plugin running with API version {}', api_version)
    server.start()
    return server


@contextmanager
def serve(extraction_plugin_class: Type[BaseExtractionPlugin], address: str) -> Generator[grpc.Server, None, None]:
    """
    Return data_context manager to start a server, so a server can be started using the ``with`` keyword.

    :extraction_plugin_class: Class of the extraction plugin implementation
    :address: Address serving this server
    :return: contextmanager of extraction plugin server
    """
    server = _start_server(extraction_plugin_class, address)
    yield server
    server.stop(None)


def serve_indefinitely(extraction_plugin_class: Type[BaseExtractionPlugin], address: str):
    """
    Start extraction plugin server that runs until it is explicitly killed.

    This method installs a SIGTERM handler, so the extraction plugin server
    will be stopped gracefully when the server(container) is requested to stop.
    Therefore, this method can only be called from the main-thread.

    :extraction_plugin_class: Class of the extraction plugin implementation
    :address: Address serving this server
    """
    server = _start_server(extraction_plugin_class, address)

    def handle_signal(*_):
        log.info('Received SIGTERM, stopping the plugin server now')
        log.info('Waiting max 5 seconds for requests to complete')
        server.stop(5).wait(5)
        log.info('Shut down gracefully')

    signal(SIGTERM, handle_signal)
    signal(SIGINT, handle_signal)

    server.wait_for_termination()
    log.info('Server terminated')
