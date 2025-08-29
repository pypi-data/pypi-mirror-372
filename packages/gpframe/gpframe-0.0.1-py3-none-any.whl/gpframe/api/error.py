"""
Exception handling policy for gpframe.

Defines the ``Raises`` enumeration, an ``IntFlag`` used to
specify which categories of exceptions should be re-raised.

Notes:
    - Members can be combined with bitwise operations.
    - ``Raises.ALL`` is equivalent to combining all flags.
"""

from enum import IntFlag, auto

class Raises(IntFlag):
    """
    Enumeration of flags that control which exceptions are re-raised.

    Members:
        SUPPRESS
            Suppress all exceptions.
        ROUTINE
            Re-raise exceptions raised in routines.
        FRAME
            Re-raise exceptions raised during frame control.
        HANDLER
            Re-raise exceptions raised in handlers.
        ALL
            Equivalent to combining ROUTINE, FRAME, and HANDLER.
    """
    SUPPRESS = 0
    ROUTINE = auto()
    FRAME = auto()
    HANDLER = auto()
    ALL = ROUTINE | FRAME | HANDLER

    def matches(self, r: Exception | None, f: Exception | None, h: Exception | None) -> bool:
        """
        Check whether any of the given exceptions should be re-raised.

        Args:
            r: Exception from a routine, or None if none occurred.
            f: Exception from frame control, or None if none occurred.
            h: Exception from a handler, or None if none occurred.

        Returns:
            True if at least one exception matches this Raises setting,
            otherwise False.
        """
        result = r is not None and self & Raises.ROUTINE
        result |= f is not None and self & Raises.FRAME
        result |= h is not None and self & Raises.HANDLER
        return bool(result)
