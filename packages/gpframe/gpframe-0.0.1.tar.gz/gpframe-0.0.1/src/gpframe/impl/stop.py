from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import Future
from multiprocessing import Process
import threading
from typing import Any


class StopInterface(ABC):
    __slots__ = ()
    @abstractmethod
    def stop(self, *, kill: bool = False) -> None:
        ...
    @property
    @abstractmethod
    def routine_is_running(self) -> bool:
        ...


class StopInterfaceSource(ABC):
    @property
    @abstractmethod
    def interface(self) -> StopInterface:
        ...
    @abstractmethod
    def set_entity(self, entity: Any) -> None:
        ...

class SubprocessStopperSource(StopInterfaceSource):
    __slots__ = ("_lock", "_process", "_interface")
    def __init__(self, lock: threading.Lock):
        self._lock = lock
        self._process = None
        self._interface = self._create_interface()
    
    def _create_interface(self) -> StopInterface:
        outer = self
        class _Interface(StopInterface):
            def stop(self, *, kill: bool = False) -> None:
                with outer._lock:
                    if outer._process is not None:
                        if kill:
                            outer._process.kill()
                        else:
                            outer._process.terminate()
                    else:
                        pass # Dose nothing
            @property
            def routine_is_running(self) -> bool:
                with outer._lock:
                    if outer._process is not None:
                        return outer._process.is_alive()
                    else:
                        return False
        
        return _Interface()

    @property
    def interface(self) -> StopInterface:
        return self._interface
    
    def set_entity(self, entity: Any):
        if not isinstance(entity, Process):
            raise TypeError("entity must be a Process")
        with self._lock:
            self._process = entity
    
class FutureStopperSource(StopInterfaceSource):
    __slots__ = ("_lock", "_future", "_interface")
    def __init__(self, lock: threading.Lock):
        self._lock = lock
        self._future = None
        self._interface = self._create_interface()
    
    def _create_interface(self) -> StopInterface:
        outer = self
        class _Interface(StopInterface):
            def stop(self, *, kill: bool = False) -> None:
                with outer._lock:
                    if outer._future is not None:
                        outer._future.cancel()
                    else:
                        pass # Dose nothing
            
            def routine_is_running(self) -> bool:
                with outer._lock:
                    if outer._future is not None:
                        return not outer._future.done()
                    else:
                        return False
        
        return _Interface()
    
    @property
    def interface(self) -> StopInterface:
        return self._interface

    def set_entity(self, entity: Any):
        if not isinstance(entity, Future):
            raise TypeError("entity must be a Future")
        with self._lock:
            self._future = entity


class SyncUnstoppableSource(StopInterfaceSource):
    __slots__ = ("_lock", "_is_running", "_interface")
    def __init__(self, lock: threading.Lock):
        self._lock = lock
        self._is_running = None
        self._interface = self._create_interface()
    
    def _create_interface(self) -> StopInterface:
        outer = self
        class _Interface(StopInterface):
            def stop(self, *, kill: bool = False) -> None:
                raise TypeError("Synchronous, non-subprocess routine cannot be stopped.")
            
            def routine_is_running(self) -> bool:
                with outer._lock:
                    if outer._is_running is not None:
                        return outer._is_running
                    else:
                        return False
        
        return _Interface()

    @property
    def interface(self) -> StopInterface:
        return self._interface

    def set_entity(self, entity: Any):
        if not isinstance(entity, bool):
            raise TypeError("entity must be a bool")
        with self._lock:
            self._is_running = entity

