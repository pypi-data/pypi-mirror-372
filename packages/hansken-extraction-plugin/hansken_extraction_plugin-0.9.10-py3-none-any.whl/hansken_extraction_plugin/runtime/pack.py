"""Contains methods to pack sdk api classes to gRPC messages."""

from datetime import datetime
import traceback
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from google.protobuf.any_pb2 import Any as GrpcAny
import grpc
from hansken import util
from hansken.util import GeographicLocation, Vector

from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin, DeferredExtractionPlugin, \
    DeferredMetaExtractionPlugin, ExtractionPlugin, MetaExtractionPlugin
from hansken_extraction_plugin.api.plugin_info import Author, PluginInfo, PluginResources, TransformerLabel
from hansken_extraction_plugin.api.search_sort_option import Direction, SearchSortOption
from hansken_extraction_plugin.api.trace_searcher import SearchScope
from hansken_extraction_plugin.api.tracelet import Tracelet
from hansken_extraction_plugin.api.transformation import RangedTransformation, Transformation
from hansken_extraction_plugin.framework import GRPC_API_VERSION
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcAuthor, RpcDataStreamTransformation, RpcMaturity, \
    RpcPluginIdentifier, RpcPluginInfo, RpcPluginResources, RpcPluginType, RpcRandomAccessDataMeta, RpcRange, \
    RpcRangedTransformation, RpcSearchTrace, RpcTrace, RpcTracelet, RpcTraceProperty, RpcTransformation, \
    RpcTransformer, RpcTransformerArgument, RpcTransformerRequest, RpcTransformerResponse
from hansken_extraction_plugin.framework.PrimitiveMessages_pb2 import (RpcBoolean, RpcBytes, RpcDouble, RpcDoubleList,
                                                                       RpcEmptyList, RpcEmptyMap,
                                                                       RpcIsoDateString,
                                                                       RpcLatLong, RpcList,
                                                                       RpcLong, RpcLongList,
                                                                       RpcMap, RpcString,
                                                                       RpcStringList, RpcStringMap, RpcVector,
                                                                       RpcZonedDateTime)
from hansken_extraction_plugin.framework.RpcCallMessages_pb2 import RpcBeginChild, RpcBeginDataStream, RpcEnrichTrace, \
    RpcFinishChild, RpcFinishDataStream, RpcPartialFinishWithError, RpcProfile, RpcRead, RpcSearchRequest, \
    RpcSearchScope, RpcSearchSortDirection, RpcSearchSortOption, RpcWriteDataStream


def any(message: Any) -> GrpcAny:
    """
    Wrap a message in an Any.

    :param message: the message to wrap in an any

    :return: the wrapped message in an Any
    """
    any_request = GrpcAny()
    any_request.Pack(message)
    return any_request


def _sequence(seq):
    if not seq:
        return RpcEmptyList()

    if all(isinstance(value, str) for value in seq):
        return RpcStringList(values=seq)

    if all(isinstance(value, int) for value in seq):
        return RpcLongList(values=seq)

    if all(isinstance(value, float) for value in seq):
        return RpcDoubleList(values=seq)

    raise TypeError('currently only homogeneous lists of type str, int, or float are supported')


def _mapping(mapping: Mapping):
    if not mapping:
        return RpcEmptyMap()

    if all(isinstance(key, str) and isinstance(value, str) for key, value in mapping.items()):
        msg = RpcStringMap()
        msg.entries.update(mapping)
        return msg

    rpc_map: Dict[str, Any] = {}
    for key, value in mapping.items():
        primitive: GrpcAny = any(_primitive(value))
        rpc_map[key] = primitive
    return RpcMap(entries=rpc_map)


def _to_rpc_iso_date_string(dt: datetime) -> RpcIsoDateString:
    return RpcIsoDateString(value=util.format_datetime(dt))


def _to_rpc_zoned_date_time(dt: datetime):
    epoch_second, nano_of_second = _split_aware_datetime(dt)
    zone_offset = dt.strftime('%z')
    zone_id = str(dt.tzinfo)

    return RpcZonedDateTime(epochSecond=epoch_second, nanoOfSecond=nano_of_second,
                            zoneOffset=zone_offset, zoneId=zone_id)


# NB: the order of this mapping is significant:
#     - bool is a subtype of int
#     - str, bytes, bytearray, GeographicLocation and Vector are subtypes of Sequence
# Note: When this mapping is changed, make sure to edit Transformer.supported_types as well.
_primitive_matchers = {
    bool: lambda value: RpcBoolean(value=value),
    int: lambda value: RpcLong(value=value),
    float: lambda value: RpcDouble(value=value),
    str: lambda value: RpcString(value=value),
    bytes: lambda value: RpcBytes(value=value),
    bytearray: lambda value: RpcBytes(value=bytes(value)),
    datetime: lambda value: _to_rpc_zoned_date_time(value),
    GeographicLocation: lambda value: RpcLatLong(latitude=value[0], longitude=value[1]),
    Vector: lambda value: RpcVector(value=bytes(value)),
    Sequence: lambda value: _sequence(value),
    Mapping: lambda value: _mapping(value),
}


def as_any(rpc_primitive) -> GrpcAny:
    """Packs a Rpc object (i.e. RpcVector) into an gRPC Any object."""
    grpc_any = GrpcAny()
    grpc_any.Pack(rpc_primitive)
    return grpc_any


def _primitive(value: Any):
    for t, packer in _primitive_matchers.items():
        if isinstance(value, t):
            return packer(value)

    raise TypeError(f'cannot pack value of type {type(value)}')


def _property(name: str, value: Any) -> RpcTraceProperty:
    return RpcTraceProperty(
        name=name,
        value=any(_primitive(value)))


def author(author: Author) -> RpcAuthor:
    """
    Convert given Author to their RpcAuthor counterpart.

    :param author: the author to convert

    :return: the converted author
    """
    return RpcAuthor(
        name=author.name,
        email=author.email,
        organisation=author.organisation)


def _resources(resources: PluginResources) -> RpcPluginResources:
    # NB: Generated protobuf code fails to mark these as optional, while proto3 syntax does state that fields are
    #     optional by default. Types here are ignored to appease mypy only
    # TODO: choose better fix for the optional typing here (HANSKEN-15846)
    return RpcPluginResources(
        maxCpu=resources.maximum_cpu or None,  # type: ignore
        maxMemory=resources.maximum_memory or None,  # type: ignore
        maxWorkers=resources.maximum_workers or None  # type: ignore
    )


def partial_finish_with_error(exception: Exception, profile: Dict[str, Union[int, float]]) -> RpcPartialFinishWithError:
    """
    Convert an exception into the gRPC RpcPartialFinishWithError message.

    :param exception: the exception to convert
    :param profile: runtime profile to send along with the finish message

    :return: the converted exception
    """
    exception_lines = traceback.format_exception_only(type(exception), exception)
    traceback_lines = traceback.format_tb(tb=exception.__traceback__, limit=-1)

    return RpcPartialFinishWithError(
        actions=[],  # pending actions have not been implemented yet
        statusCode=grpc.StatusCode.CANCELLED.name,
        errorDescription=''.join(exception_lines + traceback_lines),
        profile=pack_profile(profile)
    )


def transformers(transformers: List[TransformerLabel]) -> List[RpcTransformer]:
    """
    Convert a gigen Transformers to their RpcTransformers counterparts.

    :param transformers: the transformers to convert
    :return: the converted transformers
    """
    return [RpcTransformer(methodName=transformer.method_name,
                           parameters=transformer.parameters,
                           returnType=transformer.return_type)
            for transformer in transformers]


def plugin_info(plugin_info: PluginInfo, plugin: BaseExtractionPlugin) -> RpcPluginInfo:
    """
    Convert given PluginInfo to their RpcPluginInfo counterpart.

    :param plugin_info: the info to convert
    :param plugin: the plugin itself

    :return: the converted info
    """
    return RpcPluginInfo(
        type=_plugin_type(plugin),
        # name is deprecated
        version=plugin_info.version,
        apiVersion=GRPC_API_VERSION,
        description=plugin_info.description,
        author=author(plugin_info.author),
        matcher=plugin_info.matcher,
        webpageUrl=plugin_info.webpage_url,
        maturity=RpcMaturity.ValueType(plugin_info.maturity.value),
        deferredIterations=plugin_info.deferred_iterations,
        id=RpcPluginIdentifier(domain=plugin_info.id.domain,
                               category=plugin_info.id.category,
                               name=plugin_info.id.name),
        license=plugin_info.license,  # type: ignore
        resources=_resources(plugin_info.resources) if plugin_info.resources else None,

        # Generate the transformer attribute on the fly by dynamically retrieving all @transformer decorated methods.
        transformers=transformers([(t.generate_label()) for t in plugin.transformers]),
    )


def _plugin_type(plugin: BaseExtractionPlugin) -> Any:  # noqa
    if isinstance(plugin, MetaExtractionPlugin):
        return RpcPluginType.MetaExtractionPlugin
    if isinstance(plugin, ExtractionPlugin):
        return RpcPluginType.ExtractionPlugin
    if isinstance(plugin, DeferredExtractionPlugin):
        return RpcPluginType.DeferredExtractionPlugin
    if isinstance(plugin, DeferredMetaExtractionPlugin):
        return RpcPluginType.DeferredMetaExtractionPlugin
    raise RuntimeError(f'unsupported type of plugin: {plugin.__class__.__name__}')


def _properties(properties: Dict[str, Any]):
    return [_property(name, value) for name, value in properties.items()]


def _tracelets(tracelets: List[Tracelet]) -> List[RpcTracelet]:
    return [_tracelet(tracelet) for tracelet in tracelets]


def _tracelet(tracelet: Tracelet) -> RpcTracelet:
    rpc_tracelet_properties = [_tracelet_property(tracelet.name, name, value) for name, value in tracelet.value.items()]
    return RpcTracelet(name=tracelet.name, properties=rpc_tracelet_properties)


def _tracelet_property(tracelet_type: str, name: str, value: Any) -> RpcTraceProperty:
    if not name.startswith(f'{tracelet_type}.'):
        # receiving end will expect the fully qualified property name, even inside the tracelet
        name = f'{tracelet_type}.{name}'
    return RpcTraceProperty(name=name, value=any(_primitive(value)))


def _transformations(transformations: Dict[str, List[Transformation]]) -> List[RpcDataStreamTransformation]:
    return [
        RpcDataStreamTransformation(
            dataType=data_type,
            transformations=[_transformation(transformation) for transformation in transformations]
        )
        for data_type, transformations in transformations.items()
    ]


def _transformation(transformation: Transformation) -> RpcTransformation:
    if isinstance(transformation, RangedTransformation):
        return _ranged_transformation(transformation)
    raise ValueError(f'Unsupported transformation type: {type(transformation).__name__}')


def _ranged_transformation(transformation: RangedTransformation) -> RpcTransformation:
    rpc_ranges: List[RpcRange] = [RpcRange(offset=range.offset, length=range.length) for range in transformation.ranges]
    return RpcTransformation(rangedTransformation=RpcRangedTransformation(ranges=rpc_ranges))


def trace(id: str, types: List[str], properties: Dict[str, Any],
          tracelets: List[Tracelet], transformations: Dict[str, List[Transformation]]) -> RpcTrace:
    """
    Create an RpcTrace from a given set of types and prop.

    :param id: the id of the trace
    :param types: the types of the trace
    :param properties: the properties of the trace
    :param tracelets: the Tracelet properties of the trace, together with the other necessary metadata for a trace.
    :param transformations: the transformations of the trace grouped by data type

    :return: the created message
    """
    return RpcTrace(id=id,
                    types=types,
                    properties=_properties(properties),
                    tracelets=_tracelets(tracelets),
                    transformations=_transformations(transformations))


def _rpc_properties(properties: Dict[str, Any]) -> List[RpcTraceProperty]:
    """
    Convert a dictionary to a list of RpcTraceProperties. This list is useful when serializing an RpcTrace.

    :param properties: dict of properties to convert

    :return: list of RpcTraceProperties
    """
    return [_property(name, value) for name, value in properties.items()]


def _rpc_data(datas: Dict[str, int]) -> List[RpcRandomAccessDataMeta]:
    return [RpcRandomAccessDataMeta(type=type, size=size) for type, size in datas.items()]


def search_trace(id: str, properties: Dict[str, Any], datas: Optional[Dict[str, int]] = None) -> RpcSearchTrace:
    """
    Create an RpcSearchTrace from a given id and a set of properties.

    :param id: the id of the trace
    :param properties: the properties of the trace
    :param data: optional data streams information (type and size)

    :return: the created message
    """
    return RpcSearchTrace(
        id=id,
        properties=_rpc_properties(properties),
        data=_rpc_data(datas) if datas else None)


def trace_enrichment(trace_id: str, types: List[str], properties: Dict[str, Any],
                     tracelets: List[Tracelet], transformations: Dict[str, List[Transformation]]) -> RpcEnrichTrace:
    """
    Build an RpcEnrichTrace message.

    Create an RpcEnrichTrace message. This message contains a given set of types and
    properties, which is used by the client to enrich the trace being processed.

    :param trace_id: the id of the trace given to it by gRPC
    :param types: the types of the trace
    :param properties: the properties of the trace
    :param tracelets: the Tracelet properties of the trace
    :param transformations: the transformations of the trace

    :return: the created message
    """
    return RpcEnrichTrace(trace=trace(trace_id, types, properties, tracelets, transformations))


def begin_child(trace_id: str, name: str) -> RpcBeginChild:
    """
    Create an RpcBeginChild message.

    The client uses this message to create a new child with provided name and id.

    :param trace_id: the id of the new child trace
    :param name: the name of the new child trace
    """
    return RpcBeginChild(id=trace_id, name=name)


def finish_child(trace_id: str) -> RpcFinishChild:
    """
    Create an RpcFinishChild message.

    When the client received this message, the child with the provided id will be stored.

    :param trace_id: the id of the child trace to store
    """
    return RpcFinishChild(id=trace_id)


def rpc_read(position: int, size: int, trace_uid: str, data_type: str) -> RpcRead:
    """
    Create an RpcRead message.

    :param position: the position to read at
    :param size: the amount of bytes to read
    :param trace_uid: the uid of the trace to read data from
    :param data_type: the type of data to retrieve; raw, html...

    :return: the created message
    """
    return RpcRead(position=position, count=size, traceUid=trace_uid, dataType=data_type)


def rpc_search_request(query: str, count: int, scope: Union[str, SearchScope], start: int = 0,
                       sort: list[SearchSortOption] = [SearchSortOption()]) -> RpcSearchRequest:
    """
    Create an RpcSearchRequest from a provided query and count.

    :param query: query to pack
    :param count: count to pack
    :param scope: scope to pack
    :param start: start to pack
    :param sort: sort to pack
    :return: packed search request
    """
    rpc_search_scope = RpcSearchScope.Image if scope == SearchScope.image else RpcSearchScope.Project

    direction_map = {
        Direction.DESCENDING: RpcSearchSortDirection.DESCENDING,
        Direction.ASCENDING: RpcSearchSortDirection.ASCENDING
    }

    rpc_search_sort = [
        RpcSearchSortOption(field=sort_item.field(), direction=direction_map[sort_item.direction()])
        for sort_item in sort
    ]

    return RpcSearchRequest(query=query, count=count, scope=rpc_search_scope, start=start, sort=rpc_search_sort)


def rpc_bytes(value: bytes) -> RpcBytes:
    """
    Create an RpcBytes message which contains the supplied byte array.

    :param value: the byte array
    :return: the created message
    """
    return _primitive(value)


def begin_writing(trace_id: str, data_type: str, encoding=Optional[str]) -> RpcBeginDataStream:
    """
    Create an RpcBeginDataStream message.

    This message is used to indicate that the server will start sending data to write. The client can expect more data
    until an RpcFinishWriting message is sent.

    :param trace_id: id of the trace the data belongs to
    :param data_type: type of the data
    :param encoding: if set, interpret the bytes as encoded text given the encoding
    :return: the created message
    """
    return RpcBeginDataStream(traceId=trace_id, dataType=data_type, encoding=encoding)


def write_data(trace_id: str, data_type: str, data: bytes) -> RpcWriteDataStream:
    """
    Create an RpcWriteDataStream message.

    This message contains data to write for a given trace id and type. Data should be sent sequentially.

    :param trace_id: id of the trace the data belongs to
    :param data_type: type of the data
    :param data: raw bytes to write
    :return: the created message
    """
    return RpcWriteDataStream(traceId=trace_id, dataType=data_type, data=data)


def finish_writing(trace_id: str, data_type: str) -> RpcFinishDataStream:
    """
    Create an RpcFinishDataStream message.

    This message is used to indicate the server has finished writing data to the client. Trying to send more data for
    the same id and type will result in an error.

    :param trace_id: id of the trace the data belongs to
    :param data_type: type of the data
    :return: the created message
    """
    return RpcFinishDataStream(traceId=trace_id, dataType=data_type)


def _split_aware_datetime(dt: datetime) -> Tuple[int, int]:
    """
    Split an aware datetime into seconds & nanoseconds.

    :param dt: an aware datetime instance
    :return: (seconds, nanoseconds)
    """
    if dt.tzinfo is None:
        raise ValueError(f'No timezone set for{dt}')
    return int(dt.timestamp()), dt.microsecond * 1000


def pack_profile(profile: Dict[str, Union[int, float]]) -> RpcProfile:
    """
    Create a RpcProfile message for the provided profile.

    :param profile: the profile to pack
    :return: the created RpcProfile message
    """
    profile_ints = {k: v for k, v in profile.items() if isinstance(v, int)}
    profile_doubles = {k: v for k, v in profile.items() if isinstance(v, float)}
    return RpcProfile(profile_int64s=profile_ints, profile_doubles=profile_doubles)


def generic_list(sequence: Sequence) -> RpcList:
    """Pack a Sequence into an RpcList."""
    rpc_list = RpcList()

    for item in sequence:
        # Pack the item into an gRPC variant.
        packed_primitive = transformer_primitive(item)

        # Append the packed object to RpcList as an gRPC Any object.
        rpc_list.values.append(as_any(packed_primitive))

    return rpc_list


def generic_map(mapping: Mapping) -> RpcMap:
    """Pack a Mapping into an RpcMap."""
    rpc_map = RpcMap()

    for (key, value) in mapping.items():
        any_item = rpc_map.entries[key]
        packed_primitive = transformer_primitive(value)
        any_item.Pack(packed_primitive)

    return rpc_map


def transformer_primitive(value):
    """
    Pack a native transformer primitive into a gRPC type.

    :param value: The transformer primitive to pack.
    :return: The packed gRPC equivalent type.

    Note: Alternative packing methods are called for RpcMap and RpcList in order to bypass the use of the deprecated
    non-generic lists and maps (i.e. RpcLongList, RpcStringMap, ...)
    TODO HANSKEN-21534: Remove non-generic lists and maps in extraction plugins, allowing this method to be removed.
    """
    if issubclass(type(value), Mapping):
        return generic_map(value)
    # Specifically filter for list instead of Sequences here to avoid treating strings and vectors as Sequences.
    elif type(value) is list:
        return generic_list(value)
    else:
        return _primitive(value)


def transformer_argument(value: Any) -> RpcTransformerArgument:
    """
    Pack a supported transformer argument into a gRPC type.

    :param value: The transformer argument to pack.
    :return: The packed gRPC equivalent type.
    """
    if isinstance(value, bool):
        packed = _primitive_matchers[bool](value)
        return RpcTransformerArgument(boolean=packed)
    elif isinstance(value, bytes):
        packed = _primitive_matchers[bytes](value)
        return RpcTransformerArgument(bytes=packed)
    elif isinstance(value, int):
        packed = _primitive_matchers[int](value)
        return RpcTransformerArgument(integer=packed)
    elif isinstance(value, float):
        packed = _primitive_matchers[float](value)
        return RpcTransformerArgument(real=packed)
    elif isinstance(value, str):
        packed = _primitive_matchers[str](value)
        return RpcTransformerArgument(string=packed)
    elif isinstance(value, Vector):
        packed = _primitive_matchers[Vector](value)
        return RpcTransformerArgument(vector=packed)
    elif isinstance(value, GeographicLocation):
        packed = _primitive_matchers[GeographicLocation](value)
        return RpcTransformerArgument(latLong=packed)
    elif isinstance(value, datetime):
        packed = _primitive_matchers[datetime](value)
        return RpcTransformerArgument(datetime=packed)
    elif isinstance(value, Sequence):
        packed = generic_list(value)
        return RpcTransformerArgument(list=packed)
    elif isinstance(value, Mapping):
        packed = generic_map(value)
        return RpcTransformerArgument(map=packed)
    else:
        raise Exception("Cannot pack RpcTransformerArgument because it's type is not supported.")


def transformer_response(value: Any) -> RpcTransformerResponse:
    """
    Create a RpcTransformerResponse for a provided response.

    :param value: The response that should be packed into an RpcTransformerResponse.
    :return: The created RpcTransformerResponse.
    """
    return RpcTransformerResponse(response=transformer_argument(value))


def transformer_request(method_name: str, arguments: Dict[str, Any]) -> RpcTransformerRequest:
    """
    Create a RpcTransformerRequest for a provided method and arguments.

    :param method_name: The name of the method.
    :param arguments: The arguments to invoke the transformer with.
    :return: The created RpcTransformerRequest.
    """
    return RpcTransformerRequest(methodName=method_name, namedArguments={
        parameter: transformer_argument(argument) for parameter, argument in arguments.items()
    })
