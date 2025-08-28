"""This module defines the sort options for a search within Hansken."""
from enum import Enum


class Direction(Enum):
    """
    Enumeration for sorting directions.

    Attributes:
        ASCENDING: Sort in ascending order.
        DESCENDING: Sort in descending order.
    """

    ASCENDING = 'ASCENDING'
    DESCENDING = 'DESCENDING'


class SearchSortOption:
    """
    Represents a search sort option consisting of a field and a direction.

    Attributes:
        _field (str): The field to sort by.
        _direction (Direction): The direction to sort in (ascending or descending).
    """

    def __init__(self, field: str = 'uid', direction: Direction = Direction.ASCENDING):
        """
        Initialize a new SearchSortOption.

        Args:
            field (str): The name of the field to sort on.
            direction (Direction): The direction to sort (ascending or descending).
        """
        self._field = field
        self._direction = direction

    def field(self):
        """
        Get the field to sort on.

        Returns:
            str: Returns the current field.
        """
        return self._field

    def direction(self):
        """
        Get the sorting direction.

        Returns:
            Direction: Returns the current direction.
        """
        return self._direction
