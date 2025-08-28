"""This package contains a test framework to verify the output of extraction plugins."""


class FriendlyError(Exception):
    """A validation error raised with a user-friendly error message."""

    def __init__(self, message):
        """
        Create a FriendlyError.

        Args:
            message: the message shown to the user
        """
        super().__init__(message)
