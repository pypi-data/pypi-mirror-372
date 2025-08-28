"""This module contains different constants."""

MAX_MESSAGE_SIZE: int = 64 * 1024 * 1024
"""The maximum gRPC message size."""

MESSAGE_OVERHEAD_SIZE = 1024
"""the message wire format takes up some bytes as well, choose a safe value here for now"""

PER_ACTION_OVERHEAD_SIZE = 8
"""overhead per buffered action, chosen a safe value again"""

MAX_CHUNK_SIZE: int = MAX_MESSAGE_SIZE - MESSAGE_OVERHEAD_SIZE - PER_ACTION_OVERHEAD_SIZE
"""an estimate of the maximum chunk size based on the MAX_MESSAGE_SIZE and message overhead"""

DEFAULT_READ_WRITE_BUFFER_SIZE = min(1024 * 1024 * 6, MAX_CHUNK_SIZE)
"""
default write buffer size, as a compromise between internal memory allocation per buffer vs number of network calls
"""
