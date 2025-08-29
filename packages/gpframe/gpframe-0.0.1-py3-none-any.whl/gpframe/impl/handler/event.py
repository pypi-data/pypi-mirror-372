import asyncio
import inspect
import threading
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Union

from ..context.event import EventContext

from ...impl.handler.error import HandlerError


EventHandler = Union[Callable[[EventContext], Any], Callable[[EventContext], Awaitable[Any]]]

class EventHandlerWrapper:
    __slots__ = ('_lock', '_event_name', '_caller',)
    def __init__(self, event_name: str):
        self._lock = threading.Lock()
        self._event_name = event_name
        self._caller = None
    
    async def __call__(self, ctx: EventContext):
        with self._lock:
            if self._caller is not None:
                try:
                    return await self._caller(ctx)
                except Exception as e:
                    raise HandlerError(self._event_name, e)
                
        
    def set_handler(self, handler: EventHandler):
        with self._lock:
            if self._caller is not None:
                raise RuntimeError("Internal error: Event handler is already set.")
            if inspect.iscoroutinefunction(handler):
                self._caller = handler
            else:
                async def sync_caller(message: EventContext):
                    return await asyncio.to_thread(handler, message)
                self._caller = sync_caller


