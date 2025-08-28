"""Methods to unpack gRPC messages to sdk classes."""
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple, Type, Union

from google.protobuf.any_pb2 import Any as GrpcAny
from google.protobuf.message import Message
from hansken.util import GeographicLocation, Vector
import pytz

from hansken_extraction_plugin.api.plugin_info import Author, MaturityLevel, PluginId, PluginInfo, PluginResources, \
    TransformerLabel
from hansken_extraction_plugin.api.tracelet import Tracelet
from hansken_extraction_plugin.api.transformation import Range, RangedTransformation, Transformation
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcDataStreamTransformation, RpcPluginInfo, RpcRange, \
    RpcRangedTransformation, RpcTrace, RpcTracelet, RpcTraceProperty, RpcTransformerArgument, RpcTransformerResponse
from hansken_extraction_plugin.framework.PrimitiveMessages_pb2 import RpcBoolean, RpcBytes, RpcDouble, RpcEmptyList, \
    RpcEmptyMap, RpcInteger, RpcIsoDateString, RpcLatLong, RpcList, RpcLong, RpcLongList, RpcMap, RpcNull, RpcString, \
    RpcStringList, RpcStringMap, RpcUnixTime, RpcVector, RpcZonedDateTime


def any(message: GrpcAny, unpacker: Callable[[], Message]):
    """
    Unwrap a GrpcAny message and return the containing message.

    :param message: message to unwrap
    :param unpacker: method to convert GrpcAny message to the specific message
    :return: unwrapped message
    """
    unpacked = unpacker()
    message.Unpack(unpacked)
    return unpacked


def _rpc_zoned_date_time(zdt: RpcZonedDateTime) -> datetime:
    epoch_nanos_in_seconds: float = zdt.nanoOfSecond / 1000_000_000.0
    timezone = pytz.timezone(zdt.zoneId)

    return datetime.fromtimestamp(zdt.epochSecond + epoch_nanos_in_seconds, timezone)


def _rpc_unix_time(ut: RpcUnixTime) -> datetime:
    epoch_seconds: float = ut.value / 1000.0

    return datetime.fromtimestamp(epoch_seconds, pytz.utc)


def _map(rpc_map: RpcMap) -> Dict[str, Any]:
    converted_map: Dict[str, Any] = {}
    for key, value in rpc_map.entries.items():
        converted_map[key] = _primitive(value)
    return converted_map


_primitive_matchers: Dict[
    Type[Union[
        RpcNull,
        RpcBytes,
        RpcBoolean,
        RpcDouble,
        RpcInteger,
        RpcLong,
        RpcString,
        RpcEmptyList,
        RpcStringList,
        RpcLongList,
        RpcEmptyMap,
        RpcMap,
        RpcStringMap,
        RpcUnixTime,
        RpcZonedDateTime,
        RpcIsoDateString,
        RpcLatLong,
        RpcVector,
        RpcList
    ]],
    Callable[[Any], Any]
] = {
    RpcNull: lambda value: None,
    RpcBytes: lambda value: value.value,
    RpcBoolean: lambda value: value.value,
    RpcInteger: lambda value: value.value,
    RpcLong: lambda value: value.value,
    RpcDouble: lambda value: value.value,
    RpcString: lambda value: value.value,
    RpcEmptyList: lambda value: [],
    RpcStringList: lambda value: value.values,
    RpcLongList: lambda value: value.values,
    RpcEmptyMap: lambda value: {},
    RpcMap: lambda value: _map(value),
    RpcStringMap: lambda value: value.entries,
    RpcUnixTime: lambda value: _rpc_unix_time(value),
    RpcZonedDateTime: lambda value: _rpc_zoned_date_time(value),
    RpcIsoDateString: lambda value: datetime.strptime(value.value, '%Y-%m-%dT%H:%M:%S%z'),
    RpcLatLong: lambda value: GeographicLocation(value.latitude, value.longitude),
    RpcVector: lambda value: vector(value),
    RpcList: lambda value: generic_list(value)
}


def vector(value: RpcVector) -> Vector:
    """Unpack RpcVector to Vector."""
    return Vector(value.value)


def transformer_response(value: RpcTransformerResponse) -> RpcTransformerArgument:
    """Unpack RpcTransformerResponse to an RpcTransformerArgument."""
    return value.response


def _primitive(value: GrpcAny):
    # unpacks a primitive value that is wrapped inside an (Grpc)Any
    for matchertype, unpacker in _primitive_matchers.items():
        if value.Is(matchertype.DESCRIPTOR):
            return unpacker(any(value, matchertype))

    raise RuntimeError('unable to unpack primitive value of type {} '.format(value))


def _tracelet(rpc_tracelet: RpcTracelet) -> Tracelet:
    value = {property.name: _primitive(property.value) for property in rpc_tracelet.properties}
    return Tracelet(rpc_tracelet.name, value)


def _transformation(rpc_data_stream_transformation: RpcDataStreamTransformation) -> Tuple[str, List[Transformation]]:
    transformations: List[Transformation] = []
    for rpc_transformation in rpc_data_stream_transformation.transformations:
        type = rpc_transformation.WhichOneof('value')
        if rpc_transformation.rangedTransformation:
            transformations.append(_ranged_transformation(rpc_transformation.rangedTransformation))
        else:
            raise ValueError(f'Unsupported transformation type: {type}')

    return rpc_data_stream_transformation.dataType, transformations


def _ranged_transformation(rpc_ranged_transformation: RpcRangedTransformation) -> RangedTransformation:
    return RangedTransformation([_range(range) for range in rpc_ranged_transformation.ranges])


def _range(rpc_range: RpcRange) -> Range:
    return Range(offset=rpc_range.offset, length=rpc_range.length)


def plugin_info(rpc_plugin_info: RpcPluginInfo) -> Tuple[PluginInfo, str]:
    """
    Unpack plugin info from grpc.

    :param: rpc_plugin_info to unpack
    :return: the unpacked version
    """
    plugin_info_fields = {
        'author': Author(rpc_plugin_info.author.name, rpc_plugin_info.author.email,
                         rpc_plugin_info.author.organisation),
        'deferred_iterations': rpc_plugin_info.deferredIterations,
        'description': rpc_plugin_info.description,
        'id': PluginId(rpc_plugin_info.id.domain, rpc_plugin_info.id.category, rpc_plugin_info.id.name),
        'license': rpc_plugin_info.license,
        'matcher': rpc_plugin_info.matcher,
        'maturity': MaturityLevel(rpc_plugin_info.maturity),
        'version': rpc_plugin_info.version,
        'webpage_url': rpc_plugin_info.webpageUrl,
        'transformers': rpc_transformers(rpc_plugin_info.transformers),
    }

    api_version = rpc_plugin_info.apiVersion

    if rpc_plugin_info.resources and (rpc_plugin_info.resources.maxCpu or rpc_plugin_info.resources.maxMemory):
        plugin_info_fields['resources'] = PluginResources(maximum_cpu=rpc_plugin_info.resources.maxCpu or None,
                                                          maximum_memory=rpc_plugin_info.resources.maxMemory or None)

    return PluginInfo(**plugin_info_fields), api_version  # type: ignore


def trace(trace: RpcTrace) -> Tuple[str, List[str], Dict[str, Any], List[Tracelet], Dict[str, List[Transformation]]]:
    """
    Convert a RpcTrace to a quintuplet (id, types, properties, tracelets, transformations) of the trace.

    :param trace: the trace to convert.
    :return: quintuplet with id, types, properties, tracelets and transformations.
    """
    id: str = trace.id
    types: List[str] = list(trace.types)
    properties: Dict[str, Any] = {prop.name: _primitive(prop.value) for prop in trace.properties}
    tracelets = [_tracelet(tracelet) for tracelet in trace.tracelets]
    transformation_tuples = [_transformation(transformation) for transformation in trace.transformations]
    transformations: Dict[str, List[Transformation]] = dict(transformation_tuples)
    return id, types, properties, tracelets, transformations


def trace_properties(properties: Iterable[RpcTraceProperty]) -> Dict[str, Any]:
    """
    Unpack a list of RpcTraceProperties to a dictionary of property name to their values.

    :param properties: iterable of gRPC trace properties to unpack
    :return: dictionary of property names to unpacked values
    """
    return {prop.name: _primitive(prop.value) for prop in properties}


def bytez(bites: GrpcAny) -> bytes:
    """
    Convert GrpcAny to a primitive bytes() stream.

    @param bites: gRPC message containing bytes
    @return: primitive bytes()
    """
    return _primitive(bites)


def rpc_transformers(rpc_transformers) -> List[TransformerLabel]:
    """
    Convert list of RpcTransformers to a list of Transformers.

    :param rpc_transformers: list of RpcTransformers to convert
    :return: list of Transformers
    """
    return [TransformerLabel(method_name=rpc_transformer.methodName,
                             parameters=dict(rpc_transformer.parameters),
                             return_type=rpc_transformer.returnType)
            for rpc_transformer in rpc_transformers]


def generic_list(rpc_list: RpcList) -> Sequence:
    """
    Unpack an RpcList into a Sequence.

    :param rpc_list: The RpcList to unpack.
    :return: The unpacked RpcList that is converted to a Sequence.

    Note: This unpacking method supports non-homogeneous sequences (i.e. different types of values).
    """
    return [transformer_primitive(value) for value in rpc_list.values]


def generic_map(rpc_map: RpcMap) -> Mapping:
    """
    Unpack an RpcMap into a Mapping.

    :param rpc_map: The RpcMap to unpack.
    :return: The unpacked RpcMap that is converted to a Mapping.

    Note: This unpacking method supports non-homogeneous mappings (i.e. string to different target values).
    """
    return {key: transformer_primitive(value) for key, value in rpc_map.entries.items()}


def transformer_primitive(value: GrpcAny):
    """
    Unpack a transformer primitive that is packed as a GrpcAny.

    :param value: The RPC primitive packed as a gRPC Any that should be unpacked.
    :return: The unpacked value.

    Note: Alternative unpacking methods are called for RpcMap and RpcList in order to bypass the use of the deprecated
    non-generic lists and maps (i.e. RpcLongList, RpcStringMap, ...)
    TODO HANSKEN-21534: Remove non-generic lists and maps in extraction plugins, allowing this method to be removed.
    """
    if value.type_url == RpcMap:
        rpc_map = RpcMap()
        value.Unpack(rpc_map)
        return generic_map(rpc_map)
    elif value.type_url == RpcList:
        rpc_list = RpcList()
        value.Unpack(rpc_list)
        return generic_list(rpc_list)
    else:
        return _primitive(value)


def transformer_type(value: RpcTransformerArgument):
    """
    Unpack an RpcTransformerArgument into a native Python type.

    :param value: The RpcTransformerArgument to unpack.
    :return: The unpacked native primitive.
    """
    type_name = value.WhichOneof('type')

    if type_name == 'boolean':
        return _primitive_matchers[RpcBoolean](value.boolean)
    elif type_name == 'bytes':
        return _primitive_matchers[RpcBytes](value.bytes)
    elif type_name == 'integer':
        return _primitive_matchers[RpcLong](value.integer)
    elif type_name == 'real':
        return _primitive_matchers[RpcDouble](value.real)
    elif type_name == 'string':
        return _primitive_matchers[RpcString](value.string)
    elif type_name == 'vector':
        return _primitive_matchers[RpcVector](value.vector)
    elif type_name == 'latLong':
        return _primitive_matchers[RpcLatLong](value.latLong)
    elif type_name == 'datetime':
        return _primitive_matchers[RpcZonedDateTime](value.datetime)
    elif type_name == 'list':
        return generic_list(value.list)
    elif type_name == 'map':
        return generic_map(value.map)
    else:
        type_name_str = '' if type_name is None else type_name
        raise Exception("Cannot unpack RpcTransformerArgument because its type '"
                        + type_name_str + "' is not supported.")
