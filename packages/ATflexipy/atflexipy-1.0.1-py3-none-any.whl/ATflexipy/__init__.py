"""
ATflexiPy - Flexible Python Utilities
-----------------------------------

ATflexiPy is a lightweight Python toolkit providing flexible decorators
and helpers for function/class overloading, logging, debugging,
and runtime utilities.

Available Tools:
- smart_overload     – Function/method overloading based on argument types.
- value_overload     – Function/method overloading based on argument values.
- class_overload     – Class constructor overloading based on argument types.
- capture_print      – Executes a function and captures its print output instead of displaying it.
- capture_output     – Executes a function and returns (stdout, stderr).
- capture_logs       – Captures all logs from a function call.
- timed              – Decorator to measure function execution time.
- AutoCaptureConsole – Automatically captures console output and saves to file.
"""

from . import ATflexipy

# Public API
from .ATflexipy import (
    smart_overload,
    value_overload,
    class_overload,
    capture_print,
    capture_output,
    capture_logs,
    timed,
    AutoCaptureConsole,
)

__all__ = [
    "smart_overload",
    "value_overload",
    "class_overload",
    "capture_print",
    "capture_output",
    "capture_logs",
    "timed",
    "AutoCaptureConsole",
]

__version__ = "1.0.0"