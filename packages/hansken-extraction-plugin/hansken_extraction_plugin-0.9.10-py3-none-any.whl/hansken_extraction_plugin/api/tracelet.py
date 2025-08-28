"""This module contains the definition of a Tracelet."""
from typing import Any, Mapping


class Tracelet:
    """
    A tracelet contains the values of a single fvt (Few Valued Type).

    A few valued type is a trace property type that is a collection of tracelets. A trace can contain multiple few
    valued types containing one or more tracelets. For example, the `trace.identity`` type may look like this::

        {emailAddress: 'interesting@notreally.com'},
        {firstName: 'piet'},
        {emailAddress: 'anotheremail@notreally.com'},

    The trace.identity few valued types contains three different tracelets.
    """

    def __init__(self, name: str, value: Mapping[str, Any]):
        """
        Initialize a tracelet.

        :param name: name or type of the tracelet. In the example this would be ``identity``.
        :param value: Mapping of keys to properties of this tracelet. In the example this could be
                      ``{emailAddress: 'anotheremail@notreally.com'}``.
        """
        self.name = name
        self.value = value
