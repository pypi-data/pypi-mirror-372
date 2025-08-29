import asyncio
import inspect
import logging
import threading
from typing import Awaitable, Callable, Union

from ..context.event import EventContext

from .error import HandlerError

ExceptionHandler = Union[
    Callable[[EventContext, str, BaseException], None],
    Callable[[EventContext, str, BaseException], Awaitable[None]]
    ]

ExceptioHandlerAsync = Callable[[EventContext, str, BaseException], Awaitable[None]]

def _log_exception(ctx: EventContext, label: str, exc: BaseException):
    ctx.logger.exception(
        f"Frame[{ctx.frame_name}]: "
        f"{label} raises exception -> "
        f"{type(exc).__name__}"
    )

def _default_handler(ctx: EventContext, where: str, exc: BaseException):
    if where == "event" and isinstance(exc, HandlerError):
        where = exc.event_name
    _log_exception(ctx, where, exc)
    raise exc

class ExceptionHandlerWrapper:
    __slots__ = ('_lock', '_caller',)
    def __init__(self):
        self._lock = threading.Lock()
        self._caller: ExceptioHandlerAsync = _default_handler
    
    async def __call__(self, ctx: EventContext, where: str, exc: BaseException) -> None:
        with self._lock:
            if self._caller is not None:
                await self._caller(ctx, where, exc)
                return
            raise exc
        
    def set_handler(self, handler: ExceptionHandler):
        with self._lock:
            if self._caller is not None:
                raise RuntimeError("Internal error: exception handler is already set.")
            if inspect.iscoroutinefunction(handler):
                self._caller = handler
            else:
                async def sync_caller(message: EventContext, where:str, exc: BaseException) -> None:
                    await asyncio.to_thread(handler, message, where, exc)
                self._caller = sync_caller
