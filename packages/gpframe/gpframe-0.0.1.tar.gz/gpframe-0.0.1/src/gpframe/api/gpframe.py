"""
gpframe protocol and core error types.

This module defines the ``Frame`` protocol and the abstract base class
``FrameType``, which represent the entry point for wrapping and managing
routines inside a frame. These provide configuration methods, lifecycle
management, and access to controller contexts.

It also defines core error types:
    - ``FrameError`` — groups exceptions from routines, frame control,
      and event handlers
    - ``TerminatedError`` — raised when an operation requires an active
      frame but it has already terminated
    - ``NotTerminatedError`` — raised when termination was expected but
      the frame has not yet terminated
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio
    import logging

    from .error import Raises
    from ..impl.context.controller import Controller
    from ..impl.frame import Routine
    from ..impl.handler.event import EventHandler
    from ..impl.handler.redo import RedoHandler
    from ..impl.handler.exception import ExceptionHandler
    from ..impl.handler.terminated import TerminatedHandler

    from .outcome import Outcome
    


def Frame(routine: Routine):
    """Create a frame that manages execution of the given routine.

    ``Frame`` is exposed as a factory function (not a class), but the
    returned object behaves like a frame instance with the following features:

        - Executes the routine (sync, async, or subprocess-backed)
        - Manages lifecycle: start, cancel, close, redo
        - Provides access to contexts:
            * ControllerContext
            * EventContext
            * RoutineContext
        - Consolidates results, errors, and messages into an ``Outcome``
        - Raises errors according to the configured ``Raises`` policy

    Notes:
        - Use ``FrameType`` for type annotations and static type checking.
        - This function simply constructs and initializes the underlying frame.
    """
    from ..impl.frame import create_frame_role
    role = create_frame_role(routine)
    role.core.initialize()
    return role.interface


class FrameType(ABC):
    __slots__ = ()
    @abstractmethod
    def set_name(self, name: str) -> None:
        """Set a display name for the frame instance."""
    
    @abstractmethod
    def set_logger(self, logger: logging.Logger):
        """Set the logger used by the frame.

        By default, a logger named ``"gpframe"`` is used.
        """
        
    @abstractmethod
    def set_raises(self, raises: Raises):
        """Configure which categories of exceptions should be re-raised.

        The ``raises`` flag determines how exceptions are propagated out of
        the frame. Possible values are defined in the ``Raises`` enumeration:

            - ``Raises.SUPPRESS`` — suppress all exceptions
            - ``Raises.ROUTINE`` — re-raise exceptions from the routine
            - ``Raises.FRAME`` — re-raise exceptions from frame control
            - ``Raises.HANDLER`` — re-raise exceptions from event handlers
            - ``Raises.ALL`` — re-raise all of the above

        Notes:
            - Flags can be combined with bitwise operations.
            - ``Raises.ALL`` is equivalent to ``ROUTINE | FRAME | HANDLER``.
            - ``asyncio.CancelledError`` is not included; instead, the
            ``on_cancel`` handler is invoked when cancellation occurs.
        """
    
    @abstractmethod
    def set_environments(self, environments: dict):
        """Set the initial environment values for the frame.

        These values populate the shared read-only environment accessible
        from contexts. No interface is provided to modify the environment
        after initialization.

        Notes:
            - Internally, a shallow copy of the given mapping is used.
        """
    
    @abstractmethod
    def set_requests(self, requests: dict):
        """Set the initial request values for the routine.

        These act as the starting instructions provided to the routine.
        Whether or not the routine honors these requests depends on its
        implementation.

        Notes:
            - Internally, a shallow copy of the given mapping is used.
        """

    @abstractmethod
    def start(self, *, as_subprocess: bool = False) -> tuple[Controller, asyncio.Task[None]]:
        """Start the frame and return its controller context and task.

        The frame is launched as an ``asyncio.Task`` that manages the lifecycle
        of the routine. A tuple is returned containing:

            - ``ControllerContext`` — interface for interacting with the running frame
            - ``asyncio.Task`` — the task object representing the running frame

        Args:
            as_subprocess: If True, run the routine in a separate subprocess.
                This option is only supported for synchronous routines.
                If used with an asynchronous routine, a ``TypeError`` is raised.

        Returns:
            A tuple ``(context, task)`` where ``context`` is a ``ControllerContext``
            and ``task`` is the ``asyncio.Task`` running the frame.
        """

    @abstractmethod
    def set_terminated_callback(self, handler: TerminatedHandler):
        """Register a callback to be invoked after the frame has fully closed.

        The given handler is called once termination and cleanup are complete.
        Unlike calling ``FrameType.get_outcome()`` directly, the handler is
        guaranteed to receive a valid ``Outcome`` object.

        Args:
            handler: A callable that takes the final ``Outcome`` of the routine.
        """
    
    @abstractmethod
    def set_exception_handler(self, handler: ExceptionHandler):
        """Register a handler to be called whenever an exception occurs.

        The handler is invoked for each exception raised inside the frame,
        including ``asyncio.CancelledError``.

        Behavior:
            - If the handler completes normally (does not raise), the exception
            is treated as consumed and the frame continues running.
            - If the handler re-raises the exception (or raises another one),
            normal exception processing resumes and the frame may stop.

        Args:
            handler: A callable that takes an exception instance. It should
                either handle the exception silently or re-raise it to let
                the frame propagate the error.
        """

    @abstractmethod
    def set_redo_handler(self, handler: RedoHandler) -> None:
        """Register a handler to decide whether the routine should be re-executed.

        The handler is invoked after ``on_end`` completes. If the handler returns
        ``True``, the routine will be executed again. If it returns ``False``,
        execution finishes normally.

        Notes:
            - If the handler does not return a boolean value, the result is treated
            as ``False``.
            - The handler may be called multiple times if the routine is repeatedly
            re-executed.
        """

    @abstractmethod
    def set_on_open(self, handler: EventHandler) -> None:
        """Register a handler to be called once at the beginning of the frame.

        The open handler is invoked a single time when the frame lifecycle starts,
        before any routine execution begins.

        Notes:
            - Called only once per frame.
            - Use this for initialization that must occur before the first routine run.
        """
    
    @abstractmethod
    def set_on_start(self, handler: EventHandler) -> None:
        """Register a handler to be called immediately before the routine starts.

        The handler is invoked each time the routine is about to execute,
        including repeated executions triggered by a redo handler.
        """
    
    @abstractmethod
    def set_on_end(self, handler: EventHandler) -> None:
        """Register a handler to be called after the routine finishes.

        The handler is invoked immediately after the routine completes,
        regardless of whether it ended normally or with an error.

        Notes:
            - If the routine is executed multiple times (e.g. due to a redo
            handler), this end handler is called after each execution.
            - After the end handler returns, the redo handler (if set) is
            invoked to decide whether the routine should be run again.
        """
    
    @abstractmethod
    def set_on_cancel(self, handler: EventHandler) -> None:
        """Register a handler to be called when the routine is cancelled.

        The handler is invoked if an ``asyncio.CancelledError`` is raised.
        It is executed under ``asyncio.shield`` so that cancellation does not
        propagate into the handler itself.

        After the cancel handler completes, the ``on_close`` handler is invoked
        as part of the normal termination sequence.
        """
    
    @abstractmethod
    def set_on_close(self, handler: EventHandler) -> None:
        """Register a handler to be called during frame shutdown.

        The close handler is always invoked as part of the shutdown sequence,
        regardless of whether the routine finished normally, was cancelled,
        or raised an error. It is executed under ``asyncio.shield`` so that
        cancellation does not propagate into the handler itself.
        """
    
    @abstractmethod
    def get_outcome(self) -> Outcome:
        """Return the final outcome of the frame execution.

        The outcome is only available once the frame has fully terminated.
        If called before termination, a ``NotTerminatedError`` is raised.

        Returns:
            Outcome: The result container holding the routine's return value,
            errors, requests, and message exchange.

        Notes:
            - To obtain the outcome reliably, prefer registering a
            terminated callback via ``set_terminated_callback``.
            - If the routine has not produced a value, the return field
            will be set to ``NO_VALUE``.
        """
    
    @abstractmethod
    def peek_outcome(self) -> Outcome | None:
        """Return the outcome if available, or None if the frame is still running.

        Unlike ``get_outcome``, this method never raises ``NotTerminatedError``.
        It simply returns ``None`` when the frame has not yet terminated.

        Returns:
            Outcome | None: The final outcome if the frame has finished,
            otherwise ``None``.

        Notes:
            - This method is useful for polling without exceptions.
            - To obtain the outcome reliably, prefer registering a
            terminated callback via ``set_terminated_callback``.
        """

class FrameError(Exception):
    """Exception raised when errors occur inside a frame.

    This aggregates exceptions from three possible sources:
        - ``routine_error`` — error raised inside the user routine
        - ``frame_error`` — error raised during frame control
        - ``handler_error`` — error raised in an event handler

    Attributes:
        routine_error (Exception | None): The routine error, if any.
        frame_error (Exception | None): The frame control error, if any.
        handler_error (Exception | None): The last handler error that occurred,
            or None if none occurred. If multiple handler errors arise,
            only the most recent one is stored.

    Notes:
        - Each attribute may be ``None`` if no error of that type occurred.
        - The string representation includes the type names of the collected errors.
        - ``asyncio.CancelledError`` is **not** included here; instead, the
          ``on_cancel`` handler is invoked when cancellation occurs.
    """
    def __init__(
            self,
            routine_error: Exception | None,
            frame_error: Exception | None,
            handler_error: Exception | None
        ):
        super().__init__(
            "Exceptions raised in the frame. "
            f"routine_error = {type(routine_error).__name__ if routine_error else "None"}"
            f"frame_error = {type(frame_error).__name__ if frame_error else "None"}, "
            f"handler_error = {type(handler_error).__name__ if handler_error else "None"}"
        )
        self.routine_error = routine_error
        self.frame_error = frame_error
        self.handler_error = handler_error

class TerminatedError(Exception):
    """Raised when accessing a context resource after frame termination.

    This error is thrown if a ``SynchronizedMapReader``/``SynchronizedMapUpdater``
    (or similar context-managed resource) is accessed after the frame has
    already terminated. It prevents use of stale or invalid state once
    the frame lifecycle has ended.
    """

class NotTerminatedError(Exception):
    """Raised when requesting an outcome before frame termination.

    This error occurs if ``FrameType.get_outcome()`` is called while the
    frame is still running. An outcome is only available once the frame has
    fully terminated.
    """

