"""
FlexiPy - Flexible Python Utilities
-----------------------------------

FlexiPy is a lightweight Python toolkit providing flexible decorators
and helpers for function/class overloading, logging, debugging,
and runtime utilities.

Available Tools:
- smart_overload     – Function/method overloading based on argument types.
- value_overload     – Function/method overloading based on argument values.
- class_overload     – Class constructor overloading based on argument types.
- capture_print      – Executes a function and captures its print output instead of displaying it.
- capture_output     – Executes a function and returns (stdout, stderr).
- timed              – Decorator to measure function execution time.
- AutoCaptureConsole – Automatically captures console output and saves to file.
"""

import atexit
import datetime
import io
import sys
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type


def smart_overload(func: Callable) -> Callable:
    """
    A simple overload decorator for functions and instance methods.

    Allows registering multiple implementations of the same function
    based on the types of positional and keyword arguments.
    If no match is found, it falls back to the default implementation.

    Attributes:
        register (Callable): Decorator to register additional overloads.
        _registry (list): Stores all registered overloads.

    Parameters:
        func (Callable): The default function implementation.

    Returns:
        Callable: A wrapper function supporting overloads.
    """
    registry: List[Tuple[Tuple[Type[Any], ...], Dict[str, Type[Any]], Callable[..., Any]]] = []

    def register(pos_types: Tuple[Type[Any], ...] = (), kw_types: Optional[Dict[str, Type[Any]]] = None) -> Callable:
        """
        Register an additional overload for the function.

        Parameters:
            pos_types (tuple[type], optional): Expected types of positional arguments.
            kw_types (dict[str, type], optional): Expected types of keyword arguments.

        Returns:
            Callable: A decorator that registers the provided function.
        """
        if kw_types is None:
            kw_types = {}

        def inner(f: Callable[..., Any]) -> Callable[..., Any]:
            registry.append((pos_types, kw_types, f))
            return f

        return inner

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Dispatch calls to the appropriate overload based on argument types.

        Parameters:
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.

        Returns:
            Any: The result of the matched overload or the default function.
        """
        # Exact type match
        for pos_types, kw_types, f in registry:
            if len(args) != len(pos_types):
                continue
            if not all(isinstance(a, t) for a, t in zip(args, pos_types)):
                continue
            if not all(k in kwargs and isinstance(kwargs[k], t) for k, t in kw_types.items()):
                continue
            return f(*args, **kwargs)

        # Match by inheritance
        for pos_types, kw_types, f in registry:
            if len(args) != len(pos_types):
                continue
            if not all(issubclass(type(a), t) for a, t in zip(args, pos_types)):
                continue
            if not all(k in kwargs and isinstance(kwargs[k], t) for k, t in kw_types.items()):
                continue
            return f(*args, **kwargs)

        # Fallback to default function
        return func(*args, **kwargs)

    wrapper.register = register  # type: ignore
    wrapper._registry = registry  # type: ignore
    return wrapper


class ValueOverload:
    """
    Overloading based on *specific argument values* instead of types.

    Can be used for both free functions and class methods.
    """

    def __init__(self, func: Callable[..., Any]) -> None:
        self.default: Callable[..., Any] = func
        self.registry: Dict[Any, Callable[..., Any]] = {}
        self.is_method: bool = False
        wraps(func)(self)

    def register(self, value: Any) -> Callable[[Callable[..., Any]], "ValueOverload"]:
        """
        Register a new implementation for a specific value.

        Parameters:
            value (Any): The argument value to overload.

        Returns:
            Callable: A decorator that registers the overload.
        """

        def wrapper(func: Callable[..., Any]) -> "ValueOverload":
            self.registry[value] = func
            return self

        return wrapper

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the correct overload (function or method).

        Returns:
            Any: The result of the overload or default function.
        """
        if self.is_method:  # Called as method
            self_instance, first_arg, *rest = args
            if first_arg in self.registry:
                return self.registry[first_arg](self_instance, first_arg, *rest, **kwargs)
            return self.default(self_instance, first_arg, *rest, **kwargs)
        else:  # Called as function
            first_arg, *rest = args
            if first_arg in self.registry:
                return self.registry[first_arg](first_arg, *rest, **kwargs)
            return self.default(first_arg, *rest, **kwargs)

    def __get__(self, instance: Any, owner: Type) -> Any:
        """
        Support usage as class method (descriptor protocol).

        Returns:
            Callable: Bound method when accessed via instance.
        """
        if instance is None:
            return self
        self.is_method = True
        return self.__call__


def value_overload(func: Callable[..., Any]) -> ValueOverload:
    """
    Function decorator enabling overload by specific values.

    Parameters:
        func (Callable): The default function.

    Returns:
        ValueOverload: A wrapper object supporting `.register`.
    """
    return ValueOverload(func)


def capture_print(func: Callable[..., Any]) -> Callable[..., str]:
    """
    Capture all print output of the function and return it as a string.

    Parameters:
        func (Callable): The function to wrap.

    Returns:
        Callable: Wrapped function that returns captured print output.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        try:
            func(*args, **kwargs)
            return buffer.getvalue()
        finally:
            sys.stdout = old_stdout

    return wrapper


def capture_output(func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """
    Call a function, capture any printed output, and return it as a string.

    Parameters:
        func (Callable): Function to call.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        str: Captured console output.
    """
    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        func(*args, **kwargs)
        return buffer.getvalue()
    finally:
        sys.stdout = old_stdout


def class_overload(cls: Type) -> Type:
    """
    Enable constructor overloading for a class.

    Usage:
        @class_overload
        class Example:
            def __init__(self, *args, **kwargs):
                print("Default init:", args, kwargs)

        @Example.register(pos_types=(str, int))
        class _:
            def __init__(self, self, name, age):
                print(f"Init (str,int): {name}, {age}")
    """
    registry: Dict[str, List[Tuple[Tuple[Type[Any], ...], Dict[str, Type[Any]], Callable[..., Any]]]] = {}
    original_init = cls.__init__

    def register(pos_types: Tuple[Type[Any], ...] = (), kw_types: Optional[Dict[str, Type[Any]]] = None) -> Callable:
        if kw_types is None:
            kw_types = {}

        def inner(overload_cls: Type) -> Type:
            overload_init = getattr(overload_cls, "__init__")
            if "__init__" not in registry:
                registry["__init__"] = []
            registry["__init__"].append((pos_types, kw_types, overload_init))
            return overload_cls

        return inner

    @wraps(original_init)
    def new_init(self, *args: Any, **kwargs: Any) -> Any:
        init_overloads = registry.get("__init__", [])

        # Exact match
        for pos_types, kw_types, f in init_overloads:
            if len(args) != len(pos_types):
                continue
            if not all(isinstance(a, t) for a, t in zip(args, pos_types)):
                continue
            if not all(k in kwargs and isinstance(kwargs[k], t) for k, t in kw_types.items()):
                continue
            return f(self, *args, **kwargs)

        # Match by inheritance
        for pos_types, kw_types, f in init_overloads:
            if len(args) != len(pos_types):
                continue
            if not all(issubclass(type(a), t) for a, t in zip(args, pos_types)):
                continue
            if not all(k in kwargs and isinstance(kwargs[k], t) for k, t in kw_types.items()):
                continue
            return f(self, *args, **kwargs)

        return original_init(self, *args, **kwargs)

    cls.__init__ = new_init  # type: ignore
    cls.register = staticmethod(register)  # type: ignore
    return cls


def capture_logs(func: Callable[..., Any]) -> Callable[..., str]:
    """
    Capture all printed output (logs) of the function and return it as a string.

    Parameters:
        func (Callable): Function to wrap.

    Returns:
        Callable: Wrapped function returning captured logs.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        try:
            func(*args, **kwargs)
            return buffer.getvalue()
        finally:
            sys.stdout = old_stdout

    return wrapper


def timed(func: Callable[..., Any]) -> Callable[..., Tuple[Any, float]]:
    """
    Measure execution time of a function.

    Parameters:
        func (Callable): Function to time.

    Returns:
        Callable: Wrapped function returning (result, elapsed_time).
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[Any, float]:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result, end - start

    return wrapper


class AutoCaptureConsole:
    """
    Automatically capture console output/errors until program exit, and save to a file.

    Parameters:
        filename (str, optional): File to save captured output.
        capture (str): One of {"all", "stdout", "stderr"}.
        mode (str): "w" overwrite or "a" append.
    """

    def __init__(self, filename: Optional[str] = None, capture: str = "all", mode: str = "w") -> None:
        if capture not in {"all", "stdout", "stderr"}:
            raise ValueError('capture must be one of "all", "stdout", "stderr"')
        self.capture: str = capture
        self.mode: str = mode

        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"console_capture_{timestamp}.txt"
        self.filename: str = filename

        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.buffer_out = io.StringIO()
        self.buffer_err = io.StringIO()

        if capture in {"all", "stdout"}:
            sys.stdout = self.buffer_out
        if capture in {"all", "stderr"}:
            sys.stderr = self.buffer_err

        atexit.register(self._save)

    def _save(self) -> None:
        """Restore streams and write captured output to file."""
        if self.capture in {"all", "stdout"}:
            sys.stdout = self.old_stdout
        if self.capture in {"all", "stderr"}:
            sys.stderr = self.old_stderr

        captured = ""
        if self.capture in {"all", "stdout"}:
            captured += self.buffer_out.getvalue()
        if self.capture in {"all", "stderr"}:
            captured += self.buffer_err.getvalue()

        with open(self.filename, self.mode, encoding="utf-8") as f:
            f.write(captured)
