"""This module contains the definition of a Transformation."""
from abc import ABC
from dataclasses import dataclass
from typing import List


class Transformation(ABC):
    """A super class for data transformations. Currently only :class:RangedTransformation is supported."""

    pass


@dataclass(frozen=True)
class Range:
    """A Range describes a range of bytes with a offset and length."""

    offset: int  #: the starting point of the data
    length: int  #: the size of the data


class RangedTransformation(Transformation):
    """A :class:RangedTransformation describes a data transformation consisting of a list of :class:Range."""

    def __init__(self, ranges: List[Range]):
        """:type ranges: list of :class:Range."""
        self.ranges = ranges

    @staticmethod
    def builder():
        """:return a Builder."""
        return RangedTransformation.Builder()

    class Builder:
        """Helper class that implements a transformation builder."""

        def __init__(self) -> None:
            """Initialize a Builder."""
            self._ranges: List[Range] = []

        def add_range(self, offset: int, length: int) -> 'RangedTransformation.Builder':
            """
            Add a range to a ranged transformation by providing the range's offset and length.

            :param offset the offset of the data transformation
            :param length the length of the data transformation
            :return: this `.RangedTransformation.Builder`
            """
            if offset is None:
                raise ValueError('offset is required')
            if length is None:
                raise ValueError('length is required')
            self._ranges.append(Range(offset=offset, length=length))
            return self

        def build(self) -> 'RangedTransformation':
            """
            Return a RangedTransformation.

            :return: a :class:RangedTransformation
            """
            return RangedTransformation(ranges=self._ranges)
