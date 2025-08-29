from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
import threading
from typing import Any, Callable, Literal

from ..api.result import _SentinelValue, NO_VALUE

class RoutineResult(ABC):
    __slots__ = ()
    @property
    @abstractmethod
    def value(self) -> Any | Literal[_SentinelValue.NO_VALUE]:
        ...

    @property
    @abstractmethod
    def error(self) -> Exception | None:
        ...

class RoutineResultSource:
    __slots__ = ("_validator", "_lock", "_routine_result", "_routine_error", "_interface")
    def __init__(self, lock: threading.Lock, validator: Callable[[], None]):
        self._validator = validator
        self._lock = lock
        self._routine_result = NO_VALUE
        self._routine_error = None
        self._interface = self._create_interface()
    
    def _create_interface(self) -> RoutineResult:
        outer = self
        class _Reader(RoutineResult):
            __slots__ = ()
            @property
            def value(self) -> Any | Literal[_SentinelValue.NO_VALUE]:
                outer._validator()
                with outer._lock:
                    return outer._routine_result
            @property
            def error(self) -> Exception | None:
                outer._validator()
                with outer._lock:
                    return outer._routine_error
        return _Reader()
    
    @property
    def interface(self) -> RoutineResult:
        return self._interface
    
    def set(self, result: Any, exc: Exception | None) -> None:
        with self._lock:
            self._routine_result = result
            self._routine_error = exc
    
    def get_routine_result_unsafe(self):
        return self._routine_result
    
    def get_routine_error_unsafe(self):
        return self._routine_error
    
    def clear_routine_result_unsafe(self):
        self._routine_result = NO_VALUE
    
    def clear_routine_error_unsafe(self):
        self._routine_error = None



