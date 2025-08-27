"""
ATdispatcher
------------

A flexible Python dispatcher for functions and methods.
Supports dispatching based on argument values, keyword presence, and argument types.
"""

from .core import Dispatcher, dispatcher

__all__ = ["Dispatcher", "dispatcher"]
__version__ = "0.1.0"
