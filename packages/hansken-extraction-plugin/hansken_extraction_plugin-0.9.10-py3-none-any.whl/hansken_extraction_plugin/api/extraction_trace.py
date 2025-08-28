"""
This module contains the different Trace apis.

Note that there are a couple of different traces:
  * The ExtractionTrace and MetaExtractionTrace, which are offered to the process function.
  * ExtractionTraceBuilder, which is a trace that can be built; it does not exist in hansken yet, but it is added after
    building.
  * SearchTrace, which represents an immutable trace which is returned after searching for traces.
"""
from abc import ABC, abstractmethod
from io import BufferedReader, BufferedWriter, TextIOBase
from typing import Any, Literal, Mapping, Optional, Union

from hansken_extraction_plugin.api.tracelet import Tracelet
from hansken_extraction_plugin.api.transformation import Transformation


class ExtractionTraceBuilder(ABC):
    """
    ExtractionTrace that can be build.

    Represents child traces.
    """

    @abstractmethod
    def update(self, key_or_updates: Optional[Union[Mapping, str]] = None, value: Optional[Any] = None,
               data: Optional[Mapping[str, bytes]] = None) -> 'ExtractionTraceBuilder':
        """
        Update or add metadata properties for this `.ExtractionTraceBuilder`.

        Can be used to update the name of the Trace represented by this builder,
        if not already set.

        :param key_or_updates: either a `str` (the metadata property to be
                               updated) or a mapping supplying both keys and values to be updated
        :param value: the value to update metadata property *key* to (used
                      only when *key_or_updates* is a `str`, an exception will be thrown
                      if *key_or_updates* is a mapping)
        :param data: a `dict` mapping data type / stream name to bytes to be
                     added to the trace
        :return: this `.ExtractionTraceBuilder`
        """

    @abstractmethod
    def add_tracelet(self,
                     tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> 'ExtractionTraceBuilder':
        """
        Add a `.Tracelet` to this `.ExtractionTraceBuilder`.

        :param tracelet: the Tracelet or tracelet type (supplied as a `str`) to add
        :param value: the tracelet properties to add (only applicable when *tracelet* is a `str`)
        :return: this `.ExtractionTraceBuilder`
        """

    @abstractmethod
    def add_transformation(self, data_type: str, transformation: Transformation) -> 'ExtractionTraceBuilder':
        """
        Update or add transformations for this `.ExtractionTraceBuilder`.

        :param data_type: data type of the Transformation
        :param transformation: the Transformation to add
        :return: this `.ExtractionTraceBuilder`
        """

    @abstractmethod
    def child_builder(self, name: Optional[str] = None) -> 'ExtractionTraceBuilder':
        """
        Create a new `.TraceBuilder` to build a child trace to the trace to be represented by this builder.

        .. note::
            Traces should be created and built in depth first order,
            parent before child (pre-order).

        :return: a `.TraceBuilder` set up to save a new trace as the child
                 trace of this builder
        """

    def add_data(self, stream: str, data: bytes) -> 'ExtractionTraceBuilder':
        """
        Add data to this trace as a named stream.

        :param stream: name of the data stream to be added
        :param data: data to be attached
        :return: this `.ExtractionTraceBuilder`
        """
        return self.update(data={stream: data})

    @abstractmethod
    def open(self, data_type: Optional[str] = None, offset: int = 0, size: Optional[int] = None,
             mode: Literal['rb', 'wb', 'w', 'wt'] = 'rb', encoding='utf-8', buffer_size: Optional[int] = None) \
            -> Union[BufferedReader, BufferedWriter, TextIOBase]:
        """
        Open a data stream to read or write data from or to the `.ExtractionTrace`.

        :param data_type: the data type of the datastream, 'raw' by default
        :param offset: byte offset to start the stream on when reading
        :param size: the number of bytes to make available when reading
        :param mode: 'rb' for reading, 'wb' for writing
        :param encoding: encoding for writing text, used to convert `str` values to bytes, \
                         only valid for modes 'w' and 'wt'
        :param buffer_size: buffer size for reading (cache read back/ahead) or writing (cache for flush) data
        :return: a file-like object to read or write bytes from the named stream
        """

    @abstractmethod
    def build(self) -> str:
        """
        Save the trace being built by this builder to remote.

        .. note::
            Building more than once will result in an error being raised.

        :return: the new trace' id
        """


class Trace(ABC):
    """All trace classes should be able to return values."""

    @abstractmethod
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Return metadata properties for this `.ExtractionTrace`.

        :param key: the metadata property to be retrieved
        :param default: value returned if property is not set
        :return: the value of the requested metadata property
        """


class SearchTrace(Trace):
    """SearchTraces represent traces returned when searching for traces."""

    @abstractmethod
    def open(self, stream: str = 'raw', offset: int = 0, size: Optional[int] = None,
             buffer_size: Optional[int] = None) -> BufferedReader:
        """
        Open a data stream of the data that is being processed.

        :param stream: data stream of trace to open. defaults to raw. other examples are html, text, etc.
        :param offset: byte offset to start the stream on
        :param size: the number of bytes to make available
        :param buffer_size: buffer size for reading data
        :return: a file-like object to read bytes from the named stream
        """


class MetaExtractionTrace(Trace):
    """
    MetaExtractionTraces contain only metadata.

    This class represents traces during the extraction of an extraction plugin without a data stream.
    """

    @abstractmethod
    def update(self, key_or_updates: Optional[Union[Mapping, str]] = None, value: Optional[Any] = None,
               data: Optional[Mapping[str, bytes]] = None) -> None:
        """
        Update or add metadata properties for this `.ExtractionTrace`.

        :param key_or_updates: either a `str` (the metadata property to be
                               updated) or a mapping supplying both keys and values to be updated
        :param value: the value to update metadata property *key* to (used
                      only when *key_or_updates* is a `str`, an exception will be thrown
                      if *key_or_updates* is a mapping)
        :param data: a `dict` mapping data type / stream name to bytes to be
                     added to the trace
        """

    @abstractmethod
    def add_tracelet(self,
                     tracelet: Union[Tracelet, str],
                     value: Optional[Mapping[str, Any]] = None) -> None:
        """
        Add a `.Tracelet` to this `.MetaExtractionTrace`.

        :param tracelet: the Tracelet or tracelet type to add
        :param value: the tracelet properties to add (only applicable when *tracelet* is a tracelet type)
        """

    @abstractmethod
    def add_transformation(self, data_type: str, transformation: Transformation) -> None:
        """
        Update or add transformations for this `.ExtractionTraceBuilder`.

        :param data_type: data type of the Transformation
        :param transformation: the Transformation to add
        """

    @abstractmethod
    def child_builder(self, name: Optional[str] = None) -> ExtractionTraceBuilder:
        """
        Create a `.TraceBuilder` to build a trace to be saved as a child of this `.Trace`.

        A new trace will only be added to the index once explicitly saved (e.g.
        through `.TraceBuilder.build`).

        .. note::
            Traces should be created and built in depth first order,
            parent before child (pre-order).

        :param name: the name for the trace being built
        :return: a `.TraceBuilder` set up to create a child trace of this `.MetaExtractionTrace`
        """


class ExtractionTrace(MetaExtractionTrace):
    """Trace offered to be processed."""

    @abstractmethod
    def open(self, data_type: Optional[str] = None, offset: int = 0, size: Optional[int] = None,
             mode: Literal['rb', 'wb', 'w', 'wt'] = 'rb', encoding='utf-8', buffer_size: Optional[int] = None) \
            -> Union[BufferedReader, BufferedWriter, TextIOBase]:
        """
        Open a data stream to read or write data from or to the `.ExtractionTrace`.

        :param data_type: the data type of the datastream, 'raw' by default
        :param offset: byte offset to start the stream on when reading
        :param size: the number of bytes to make available when reading
        :param mode: 'rb' for reading, 'wb' for writing
        :param encoding: encoding for writing text, used to convert `str` values to bytes, \
                         only valid for modes 'w' and 'wt'
        :param buffer_size: buffer size for reading (cache read back/ahead) or writing (cache for flush) data
        :return: a file-like object to read or write bytes from the named stream
        """
