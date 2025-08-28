"""
This module contains a gRPC implementation of RawIOBase.

This is useful when retrieving raw data streams from Hansken.
"""
from array import array
from io import RawIOBase, SEEK_CUR, SEEK_END, SEEK_SET
from mmap import mmap
from typing import Union

from google.protobuf.any_pb2 import Any as GrpcAny
from typing_extensions import Protocol

from hansken_extraction_plugin.runtime import unpack
from hansken_extraction_plugin.runtime.constants import MAX_CHUNK_SIZE


class RawRead(Protocol):
    """The type of grpc_handler_read, which can be a function with the same signature as __call__."""

    def __call__(self, offset: int, size: int) -> GrpcAny:
        """Type definition of the method."""
        pass


# inspo:https://stackoverflow.com/questions/58702442/wrap-an-io-bufferediobase-such-that-it-becomes-seek-able
class _GrpcRawIO(RawIOBase):
    """RawIOBase implementation that retrieves data using gRPC calls."""

    def __init__(self, grpc_handler_read: RawRead, stream_offset: int, size: int, first_bytes: bytes):
        """
        Initialize this class.

        :param grpc_handler_read: callable that can be used to perform a gRPC read request: e.g.
                                  hansken_extraction_plugin.runtime.extraction_plugin_server.ProcessHandler.read
        :param stream_offset: start of the stream
        :param size: total size of the stream
        :param first_bytes: first bytes of the stream
        """
        self._grpc_handler_read = grpc_handler_read
        self._size = size
        self._first_bytes = first_bytes or bytes()
        self._position = 0
        if stream_offset is not None:
            self.seek(stream_offset)

    def seekable(self):
        return True

    def readable(self):
        return True

    def writable(self):
        return False

    def _read(self, size: int):
        if self._position >= len(self._first_bytes):
            # data to be read not in _first_bytes, so read over gRPC
            return self._read_chunks(size, self._position)
        else:
            # data to be read partially in _first_bytes, we just return that part, the user can read again to get the
            # remainder, and that is when we read over gRPC if it needs that chunk (BufferedReaders might not need the
            # rest)
            bytes_to_read = min(len(self._first_bytes) - self._position, size)
            return self._first_bytes[self._position:self._position + bytes_to_read]

    def _read_chunks(self, size: int, position: int) -> bytes:
        """
        Divide requested data into chunks of the maximum allowed size per gRPC message.

        @param size: length of the requested data
        @param position: position to start read from
        @return: a bytes() representation of the RpcBytes response from the server
        """
        if size == 0:
            # reading 0 bytes is valid, at any given position (even if position is larger than the stream size)
            # to avoid expensive grpc calls, just return a 0-length bytes (HANSKEN-20824, occurs e.g. when using pillow)
            return bytes()

        offset = position
        # just one chunk
        if size <= MAX_CHUNK_SIZE:
            return unpack.bytez(self._grpc_handler_read(offset=offset, size=size))
        else:
            # multiple chunks
            buffer = bytes()
            no_of_chunks = size // MAX_CHUNK_SIZE
            for i in range(no_of_chunks):
                chunk_offset = offset + (i * MAX_CHUNK_SIZE)
                buffer += unpack.bytez(self._grpc_handler_read(offset=chunk_offset, size=MAX_CHUNK_SIZE))
            last_offset = offset + no_of_chunks * MAX_CHUNK_SIZE
            last_size = size - last_offset
            if last_size > 0:
                buffer += unpack.bytez(self._grpc_handler_read(offset=last_offset, size=last_size))
            return buffer

    def readinto(self, __buffer: Union[bytearray, memoryview, array, mmap]) -> int:  # type: ignore
        # type of buffer should be collections.abc.Buffer (Python 3.12 forward)
        __size = len(__buffer)
        if __size + self._position > self._size:
            __size = self._size - self._position

        read_bytes = self._read(__size)
        __buffer[:len(read_bytes)] = read_bytes

        self._position += len(read_bytes)
        return len(read_bytes)

    def tell(self) -> int:
        return self._position

    def seek(self, position: int, whence: int = SEEK_SET) -> int:
        relative_to = {
            SEEK_SET: 0,
            SEEK_CUR: self._position,
            SEEK_END: self._size,
        }.get(whence, 0)

        new_position: int = relative_to + position
        if new_position < 0:
            raise ValueError(f'the position must not be negative: {new_position}')

        if new_position > self._size:
            raise ValueError(
                f'the position must not be greater than the size of the data: {new_position} > {self._size}')

        self._position = new_position
        return self._position

    def close(self):
        super().close()
