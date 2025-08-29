from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Protocol

import inspect
import logging
import threading
from multiprocessing import Queue, Manager, Process
from multiprocessing.managers import DictProxy, SyncManager

from ..api.gpframe import FrameType, FrameError, TerminatedError, NotTerminatedError
from ..api.error import Raises
from ..api.outcome import Outcome

from .state import _create_usage_state_role
from .state import _RoleTOC as _UsageStateRoleTOC

from .handler.error import HandlerError

from .handler.redo import RedoHandlerWrapper
from .handler.redo import RedoHandler

from .handler.exception import ExceptionHandlerWrapper
from .handler.exception import ExceptionHandler

from .syncm import SynchronizedMap, SynchronizedMapReader, SynchronizedMapUpdater

from .context.controller import Controller, create_controller_context
from .context.event import EventContext, create_event_context
from .context.routine import RoutineContext, create_routine_context

from .stop import StopInterfaceSource, FutureStopperSource,  SubprocessStopperSource, SyncUnstoppableSource

from .result import RoutineResultSource
from .result import NO_VALUE

from .handler.event import EventHandlerWrapper
from .handler.event import EventHandler

from .outcome import OutcomeSource

from .handler.terminated import TerminatedHandlerWrapper
from .handler.terminated import TerminatedHandler

Routine = Callable[[RoutineContext], Any] | Callable[[RoutineContext], Awaitable[Any]]
RoutineCaller = Callable[[asyncio.AbstractEventLoop], tuple[Any, Exception | asyncio.CancelledError | None]]

class _ConstantTOC(Protocol):
    ALL_EVENTS: tuple[str, ...]

class _StateTOC(Protocol):
    usage: _UsageStateRoleTOC
    
    frame_name: str
    logger: logging.Logger

    raises_policy: Raises

    event_handlers: dict[str, EventHandlerWrapper]
    redo_handler: RedoHandlerWrapper
    exception_handler: ExceptionHandlerWrapper
    
    
    environments: dict
    requests: dict

    sync_manager: SyncManager | None

    environment_map: SynchronizedMap | None
    request_map: SynchronizedMap | None
    event_msg_map: SynchronizedMap | None
    routine_msg_map: SynchronizedMap | None
    routine_result: RoutineResultSource | None

    routine_stopper: StopInterfaceSource | None

    outcome_source: OutcomeSource | None
    
    terminated_callback: TerminatedHandlerWrapper



class _CoreTOC(Protocol):
    def initialize(self) -> None:
        ...

    def _get_routine_call_kind(self) -> str:
        ...
    
    def load_subprocess_manager_if_needed(self, as_subprocess):
        ...

    def get_lock_factory(self) -> Callable[[], threading.Lock]:
        ...
    
    def get_map_factory(self) -> Callable[[], dict[str, Any]] | Callable[[], DictProxy[str, Any]]:
        ...
    
    def _get_updater_reader(self, syncm: SynchronizedMap) -> tuple[SynchronizedMapUpdater, SynchronizedMapReader]:
        ...
    
    def create_messages(self, lock_factory, map_factory, requests) -> tuple[Controller, EventContext, RoutineContext]:
        ...
    
    def _close_subprocess(self) -> None:
        ...

    def create_routine_caller(self, msg: RoutineContext) -> Callable[[asyncio.AbstractEventLoop], tuple[Any, Exception | None]]:
        ...

    def _struct_outcome(self, frame_error: Exception | None) -> OutcomeSource:
        ...
    async def frame(self, routine_caller, emsg: EventContext) -> None:
        ...

class _RoleTOC(Protocol):
    constant: _ConstantTOC
    state: _StateTOC
    core: _CoreTOC
    interface: FrameType

def _subprocess_entry(routine: Routine, msg: RoutineContext, queue: Queue):
    try:
        queue.put((routine(msg), None))
    except Exception as e:
        queue.put((NO_VALUE, e))


def create_frame_role(routine: Routine):

    if not callable(routine):
        raise TypeError("routine must be a callable")

    class _Constant(_ConstantTOC):
        __slots__ = ()
        ALL_EVENTS = (
            'on_open',
            'on_start',
            'on_end',
            'on_cancel',
            'on_close'
        )
    constant = _Constant()

    class _State(_StateTOC):
        __slots__ = ()
        usage: _UsageStateRoleTOC = _create_usage_state_role()
        
        frame_name: str = "noname"
        logger: logging.Logger = logging.getLogger("gpframe")

        raises_policy: Raises = Raises.ALL

        event_handlers: dict[str, EventHandlerWrapper] = {}
        redo_handler: RedoHandlerWrapper = RedoHandlerWrapper()
        exception_handler: ExceptionHandlerWrapper = ExceptionHandlerWrapper()

        sync_manager: SyncManager | None = None

        environments: dict = {}
        requests: dict = {}

        environment_map: SynchronizedMap | None = None
        request_map: SynchronizedMap | None = None
        event_msg_map: SynchronizedMap | None  = None
        routine_msg_map: SynchronizedMap | None = None
        routine_result: RoutineResultSource | None = None

        routine_stopper: StopInterfaceSource | None = None

        outcome_source: OutcomeSource | None = None

        terminated_callback = TerminatedHandlerWrapper()

    state = _State()

    class _Core(_CoreTOC):
        __slots__ = ()
        def initialize(self) -> None:
            state.event_handlers.update({
                event_name : EventHandlerWrapper(event_name)
                for event_name in constant.ALL_EVENTS
            })

        def _get_routine_call_kind(self) -> str:
            if inspect.iscoroutinefunction(routine):
                return "async"
            else:
                return "subprocess" if state.sync_manager else "sync"
        
        def load_subprocess_manager_if_needed(self, as_subprocess):
            if as_subprocess:
                if inspect.iscoroutinefunction(routine):
                    raise TypeError("async routine cannot be started as a subprocess")
                state.sync_manager = Manager()

        def get_lock_factory(self) -> Callable[[], threading.Lock]:
            call_kind = self._get_routine_call_kind()
            if call_kind in ("sync", "async"):
                return threading.Lock
            elif call_kind == "subprocess":
                assert state.sync_manager
                return state.sync_manager.Lock
            else:
                raise RuntimeError(f"Internal error: Unexpected call kind. {call_kind}")
        
        def get_map_factory(self) -> Callable[[], dict[str, Any]] | Callable[[], DictProxy[str, Any]]:
            call_kind = self._get_routine_call_kind()
            if call_kind in ("sync", "async"):
                return dict
            elif call_kind == "subprocess":
                assert state.sync_manager
                return state.sync_manager.dict
            else:
                raise RuntimeError(f"Internal error: Unexpected call kind. {call_kind}")
        
        def _get_updater_reader(self, syncm: SynchronizedMap) -> tuple[SynchronizedMapUpdater, SynchronizedMapReader]:
            return syncm.updater, syncm.reader
        
        def create_messages(self, lock_factory, map_factory) -> tuple[Controller, EventContext, RoutineContext]:
            def access_validator():
                if state.usage.interface.terminated:
                    raise TerminatedError
            
            lock = lock_factory()

            state.environment_map = SynchronizedMap(lock, map_factory(state.environments), access_validator)
            state.request_map = SynchronizedMap(lock, map_factory(state.requests), access_validator)
            state.event_msg_map = SynchronizedMap(lock, map_factory(), access_validator)
            state.routine_msg_map = SynchronizedMap(lock, map_factory(), access_validator)

            _, env_reader = self._get_updater_reader(state.environment_map)
            req_updater, req_reader = self._get_updater_reader(state.request_map)
            emsg_updater, emsg_reader = self._get_updater_reader(state.event_msg_map)
            rmsg_updater, rmsg_reader = self._get_updater_reader(state.routine_msg_map)

            routine_result = RoutineResultSource(lock, access_validator)
            routine_result_reader = routine_result.interface
            state.routine_result = routine_result

            call_kind = core._get_routine_call_kind()
            if call_kind == "sync":
                state.routine_stopper = SyncUnstoppableSource(lock)
            elif call_kind == "async":
                state.routine_stopper = FutureStopperSource(lock)
            elif call_kind == "subprocess":
                state.routine_stopper = SubprocessStopperSource(lock)
            else:
                raise RuntimeError(f"Internal error: Unexpected call kind. {call_kind}")
            
            controller_msg = create_controller_context(
                state.frame_name,
                state.logger,
                state.sync_manager is not None,
                env_reader,
                req_updater,
                emsg_reader,
                rmsg_reader,
                routine_result_reader,
                state.routine_stopper.interface)
            event_msg = create_event_context(
                state.frame_name,
                state.logger,
                state.sync_manager is not None,
                env_reader,
                req_reader,
                emsg_updater,
                rmsg_reader,
                routine_result_reader)
            routine_msg = create_routine_context(
                state.frame_name,
                state.logger.name,
                state.sync_manager is not None,
                env_reader,
                req_reader,
                emsg_reader,
                rmsg_updater)
            
            return controller_msg, event_msg, routine_msg
        
        def _close_subprocess(self) -> None:
            if state.sync_manager:
                try:
                    state.sync_manager.shutdown()
                except Exception as e:
                    state.logger.exception(f"subprocess_manger raises exception {type(e).__name__}")

        def create_routine_caller(self, msg: RoutineContext) -> RoutineCaller:
            if inspect.iscoroutinefunction(routine):
                async_routine = routine # supports static type checking
                def routine_caller_async(loop) -> tuple[Any, Exception | asyncio.CancelledError | None]:
                    try:
                        future = asyncio.run_coroutine_threadsafe(async_routine(msg), loop)
                        assert state.routine_stopper
                        state.routine_stopper.set_entity(future)
                        return future.result(), None
                    except Exception as e:
                        return NO_VALUE, e
                return routine_caller_async
            else:
                if state.sync_manager is not None:
                    def routine_caller_subprocess(_) -> tuple[Any, Exception | None]:
                        
                        q = Queue()
                        p = Process(
                            target = _subprocess_entry,
                            args = (routine, msg, q)
                        )
                        p.start()
                        assert state.routine_stopper
                        state.routine_stopper.set_entity(p)
                        try:
                            p.join()
                            if not q.empty():
                                return q.get_nowait()
                            else:
                                return NO_VALUE, None
                        finally:
                            q.close()
                            q.join_thread()
                    return routine_caller_subprocess
                else:
                    def routine_caller_sync(_) -> tuple[Any, Exception | None]:
                        try:
                            assert state.routine_stopper
                            state.routine_stopper.set_entity(True)
                            result = routine(msg)
                            state.routine_stopper.set_entity(False)
                            return result, None
                        except Exception as e:
                            assert state.routine_stopper
                            state.routine_stopper.set_entity(False)
                            return NO_VALUE, e
                    return routine_caller_sync

        def _struct_outcome(
                self,
                frame_error: Exception | None,
                handler_error: Exception | None
            ) -> None:
            assert state.routine_result
            routine_result = state.routine_result.get_routine_result_unsafe()
            routine_error = state.routine_result.get_routine_error_unsafe()
            assert state.request_map
            requests = state.request_map.copy_map_without_usage_state_check()
            assert state.event_msg_map
            event_msg = state.event_msg_map.copy_map_without_usage_state_check()
            assert state.routine_msg_map
            routine_msg = state.routine_msg_map.copy_map_without_usage_state_check()

            state.outcome_source = OutcomeSource(
                routine_result,
                routine_error,
                frame_error,
                handler_error,
                requests,
                event_msg,
                routine_msg)
        
        def _cleanup(self) -> None:
            assert state.environment_map
            state.environment_map.clear_map_unsafe()
            assert state.request_map
            state.request_map.clear_map_unsafe()
            assert state.event_msg_map
            state.event_msg_map.clear_map_unsafe()
            assert state.routine_msg_map
            state.routine_msg_map.clear_map_unsafe()
            assert state.routine_result
            state.routine_result.clear_routine_result_unsafe()
            state.routine_result.clear_routine_error_unsafe()
        
        
        async def frame(self, routine_caller: RoutineCaller, emsg: EventContext) -> None:
            frame_error = None
            handler_error = None
            try:
                loop = asyncio.get_running_loop()
                
                ev_handlers = state.event_handlers

                try:
                    await ev_handlers["on_open"](emsg)
                except HandlerError as e:
                    await asyncio.shield(state.exception_handler(emsg, 'event', e))
                
                while True:
                    try:
                        await ev_handlers["on_start"](emsg)
                    except HandlerError as e:
                        await asyncio.shield(state.exception_handler(emsg, 'event', e))

                    result, e = routine_caller(loop)

                    if isinstance(e, asyncio.CancelledError):
                        await asyncio.shield(state.exception_handler(emsg, 'routine', e))
                        e = None
                    
                    if e:
                        await asyncio.shield(state.exception_handler(emsg, 'routine', e))
                        
                    
                    assert state.routine_result
                    state.routine_result.set(result, e)
                    
                    try:
                        await ev_handlers["on_end"](emsg)
                    except HandlerError as e:
                        await asyncio.shield(state.exception_handler(emsg, 'event', e))
                    
                    try:
                        redo = await state.redo_handler(emsg)
                    except HandlerError as e:
                        await asyncio.shield(state.exception_handler(emsg, 'redo', e))

                    if not redo:
                        break

            except asyncio.CancelledError as e:
                try:
                    try:
                        await asyncio.shield(ev_handlers["on_cancel"](emsg))
                    except HandlerError as he:
                        try:
                            await asyncio.shield(state.exception_handler(emsg, 'event', he))
                        except HandlerError:
                            handler_error = he
                except Exception as fe:
                    frame_error = fe
            except HandlerError as e:
                # This HandlerError was re-raised by the ExceptionHandler.
                handler_error = e
            except Exception as e:
                try:
                    await asyncio.shield(state.exception_handler(emsg, 'frame', e))
                except Exception as fe:
                    frame_error = fe
            finally:
                try:
                    try:
                        await asyncio.shield(ev_handlers["on_close"](emsg))
                    except HandlerError as he:
                        try:
                            await asyncio.shield(state.exception_handler(emsg, 'event', he))
                        except HandlerError:
                            handler_error = he
                except Exception as fe:
                    frame_error = fe

                def to_terminate():
                    core._struct_outcome(frame_error, handler_error)

                state.usage.interface.terminate(to_terminate)

                core._cleanup()
                core._close_subprocess()
                
                assert state.outcome_source
                routine_error = state.outcome_source.interface.routine_error

                try:
                    try:
                        await asyncio.shield(state.terminated_callback(state.outcome_source.interface))
                    except HandlerError as he:
                        try:
                            await asyncio.shield(state.exception_handler(emsg, 'terminated', he))
                        except HandlerError:
                            handler_error = he
                except Exception as fe:
                    frame_error = fe

                if state.raises_policy.matches(routine_error, frame_error, handler_error):
                    raise FrameError(routine_error, frame_error, handler_error)
    core = _Core()

    class _Interface(FrameType):
        __slots__ = ()
        def set_name(self, name: str) -> None:
            def fn():
                state.frame_name = name
            state.usage.interface.load(fn)
    
        def set_logger(self, logger: logging.Logger):
            def fn():
                state.logger = logger
            state.usage.interface.load(fn)
        
        def set_raises(self, raises: Raises):
            def fn():
                state.raises_policy = raises
            state.usage.interface.load(fn)

        def set_environments(self, environments: dict):
            def fn():
                state.environments = dict(environments)
            state.usage.interface.load(fn)
        
        def set_requests(self, requests: dict):
            def fn():
                state.requests = dict(requests)
            state.usage.interface.load(fn)
        
        def set_exception_handler(self, handler: ExceptionHandler):
            def fn():
                state.exception_handler.set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_terminated_callback(self, handler: TerminatedHandler):
            def fn():
                state.terminated_callback.set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_redo_handler(self, handler: RedoHandler):
            def fn():
                state.redo_handler.set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_open(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_open"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_start(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_start"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_end(self, handler:EventHandler) -> None:
            def fn():
                state.event_handlers["on_end"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_cancel(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_cancel"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def set_on_close(self, handler: EventHandler) -> None:
            def fn():
                state.event_handlers["on_close"].set_handler(handler)
            state.usage.interface.load(fn)
        
        def start(self, *, as_subprocess: bool = False) -> tuple[Controller, asyncio.Task[None]]:
            state.usage.interface.activate()
            core.load_subprocess_manager_if_needed(as_subprocess)
            lock_factory = core.get_lock_factory()
            map_factory = core.get_map_factory()
            cmsg, emsg, rmsg = core.create_messages(lock_factory, map_factory)
            routine_caller = core.create_routine_caller(rmsg)
            task = asyncio.create_task(core.frame(routine_caller, emsg))
            return cmsg, task
        
        def get_outcome(self) -> Outcome:
            if state.usage.interface.terminated:
                assert state.outcome_source
                return state.outcome_source.interface
            else:
                raise NotTerminatedError
            
        def peek_outcome(self) -> Outcome | None:
            if state.usage.interface.terminated:
                assert state.outcome_source
                return state.outcome_source.interface
            else:
                return None
    interface = _Interface()

    @dataclass(slots = True)
    class _Role(_RoleTOC):
        constant: _ConstantTOC
        state: _StateTOC
        core: _CoreTOC
        interface: FrameType
    
    return _Role(constant = constant, state = state, core = core, interface = interface)


