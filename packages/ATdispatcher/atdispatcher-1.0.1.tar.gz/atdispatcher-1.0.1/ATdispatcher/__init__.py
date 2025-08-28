# ATdispatcher/__init__.py
"""
ATdispatcher Package

A flexible Python dispatcher library for functions and methods with multiple options,
default arguments, type checking, and automatic handling of instance attributes (SelfAttr).

Modules:
- core: Core implementation of FuncDispatcher, MethodDispatcher, and SelfAttr.

API:
- dispatcher: Decorator for creating function dispatchers.
- method_dispatcher: Decorator for creating method dispatchers with SelfAttr support.
- SelfAttr: Helper for specifying instance attribute defaults in method dispatchers.

Example Usage:

from ATdispatcher import dispatcher, method_dispatcher, SelfAttr

# Function dispatcher
@dispatcher
def func(a: int, b: int):
    return a + b

@func.reg()
def _(a: int, b: int, c: int = 3):
    return a * b * c

print(func(2, 4))       # 6
print(func(2, 4, 3))    # 24

# Method dispatcher
class MyClass:
    def __init__(self):
        self.mult = 2

    @method_dispatcher
    def method(self, x: int, y: int = SelfAttr("mult")):
        return x * y

obj = MyClass()
print(obj.method(5))     # 10 (uses self.mult)
"""

from .core import dispatcher, method_dispatcher, SelfAttr

__all__ = [
    "dispatcher",
    "method_dispatcher",
    "SelfAttr",
]
