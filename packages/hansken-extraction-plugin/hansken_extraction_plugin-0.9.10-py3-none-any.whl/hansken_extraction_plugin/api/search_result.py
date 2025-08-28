"""This module contains a representation of a search result."""
from abc import ABC, abstractmethod
from itertools import islice
from typing import Iterable, List, Optional

from hansken_extraction_plugin.api.extraction_trace import SearchTrace


class SearchResult(ABC, Iterable):
    """
    Class representing a stream of traces, returned when performing a search request.

    This result can only be iterated once. Results can be retrieved in three ways:

    Treating the result as an iterable:

    .. code-block:: python

        for trace in result:
            print(trace.name)

    Calling `.take` to process one or more batches of traces:

    .. code-block:: python

        first_100 = result.take(100)
        process_batch(first_100)

    Calling `.takeone` to get a single trace:

    .. code-block:: python

        first = result.takeone()
        second = result.takeone()

        print(first.name, second.name)

    """

    @abstractmethod
    def total_results(self) -> int:
        """
        Return the  total number of hits.

        :return: Total number of hits
        """
        pass

    def takeone(self) -> Optional[SearchTrace]:
        """
        Return a single trace, if this stream is not exhausted.

        :return: A searchtrace, or None if no trace is available
        """
        return next(self.__iter__(), None)

    def take(self, num: int) -> List[SearchTrace]:
        """
        Return a list containing at most num number of traces, or less if they are not available.

        :param num: Number of traces to take
        :return: List containing zero or more traces
        """
        return list(islice(self.__iter__(), num))

    def close(self):
        """
        Close this SearchResult if no more traces are to be retrieved.

        Required to keep compatibility with hansken.py.
        """
        pass
