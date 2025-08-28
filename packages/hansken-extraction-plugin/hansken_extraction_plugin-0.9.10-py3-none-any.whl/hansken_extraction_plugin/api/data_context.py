"""This module contains the definition of the DataContext."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DataContext:
    """This class contains the data context of a plugin that is processing a trace."""

    data_type: str  #: the named data type that is being processed
    data_size: int  #: the size / total length of the data stream that is being processed

    def __eq__(self, other):
        # override the default equality check, a subclass is considered equal as long as it matches all the fields this
        # type describes
        return isinstance(other, DataContext) and (self.data_type, self.data_size) == (other.data_type, other.data_size)
