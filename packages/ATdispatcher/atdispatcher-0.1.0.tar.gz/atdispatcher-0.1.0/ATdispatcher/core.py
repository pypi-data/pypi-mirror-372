import inspect
from functools import wraps
from typing import Callable, Any, List, Tuple, Dict, Optional, Type

class Dispatcher:
    """A class that dispatches function calls based on defined rules.

    The Dispatcher allows dynamic function selection based on conditions
    applied to arguments and keyword arguments. It supports both standalone
    functions and class methods.

    Attributes:
        fn (Callable): The default function to call if no rules match.
        rules (List[Tuple[Callable, Callable]]): List of (condition, function) pairs.
    """
    def __init__(self, fn: Callable) -> None:
        """Initialize the Dispatcher with a default function.

        Args:
            fn (Callable): The default function to be called if no rules match.
        """
        self.fn = fn
        self.rules: List[Tuple[Callable, Callable]] = []

    def __get__(self, instance: Optional[Any], owner: Type) -> Any:
        """Descriptor method to support instance method binding.

        Args:
            instance (Optional[Any]): The instance of the class (or None for class access).
            owner (Type): The owner class.

        Returns:
            Any: Either the Dispatcher itself or a _BoundDispatcher instance.
        """
        if instance is None:
            return self
        return _BoundDispatcher(self, instance)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the appropriate function based on registered rules.

        Iterates through the rules and executes the first function whose
        condition matches the provided arguments.

        Args:
            *args: Variable positional arguments.
            **kwargs: Variable keyword arguments.

        Returns:
            Any: The result of the matched function or the default function.
        """
        for cond, func in self.rules:
            if cond(args, kwargs):
                return func(*args, **kwargs)
        return self.fn(*args, **kwargs)

    def add_rule(self, cond: Callable, func: Callable) -> 'Dispatcher':
        """Add a new rule to the dispatcher.

        Args:
            cond (Callable): A condition function that evaluates args and kwargs.
            func (Callable): The function to call if the condition is met.

        Returns:
            Dispatcher: Self, for method chaining.
        """
        self.rules.append((cond, func))
        return self

    def values(self, **expected: Any) -> '_RuleBuilder':
        """Create a rule builder for matching specific argument values.

        Args:
            **expected: Keyword arguments with expected values.

        Returns:
            _RuleBuilder: A rule builder instance for further configuration.
        """
        return _RuleBuilder(self, expected=expected)

    def kwargs(self, *keys: str) -> '_RuleBuilder':
        """Create a rule builder for matching specific keyword argument names.

        Args:
            *keys: Names of keyword arguments to check for presence.

        Returns:
            _RuleBuilder: A rule builder instance for further configuration.
        """
        return _RuleBuilder(self, keys=keys)

    def types(self, *types_: Type) -> '_RuleBuilder':
        """Create a rule builder for matching argument types.

        Args:
            *types_: Expected types for positional arguments.

        Returns:
            _RuleBuilder: A rule builder instance for further configuration.
        """
        return _RuleBuilder(self, types_=types_)

class _BoundDispatcher:
    """A wrapper for Dispatcher to handle instance method binding.

    This class ensures that the instance (self) is properly injected into
    method calls when the Dispatcher is used as a method decorator.

    Attributes:
        _d (Dispatcher): The original Dispatcher instance.
        _inst (Any): The instance of the class the Dispatcher is bound to.
    """
    def __init__(self, dispatcher: Dispatcher, instance: Any) -> None:
        """Initialize the bound dispatcher.

        Args:
            dispatcher (Dispatcher): The Dispatcher instance to bind.
            instance (Any): The class instance to bind to.
        """
        self._d = dispatcher
        self._inst = instance

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the appropriate function with the instance injected.

        Args:
            *args: Variable positional arguments.
            **kwargs: Variable keyword arguments.

        Returns:
            Any: The result of the matched function or the default function.
        """
        new_args = (self._inst, *args)
        for cond, func in self._d.rules:
            if cond(new_args, kwargs):
                return func(self._inst, *args, **kwargs)
        return self._d.fn(self._inst, *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying Dispatcher.

        Args:
            name (str): The attribute name.

        Returns:
            Any: The attribute value from the Dispatcher.
        """
        return getattr(self._d, name)

class _RuleBuilder:
    """A builder for creating dispatching rules.

    This class provides a fluent interface for defining conditions based on
    argument values, keyword presence, or argument types.

    Attributes:
        dispatcher (Dispatcher): The Dispatcher to add rules to.
        expected (Dict[str, Any]): Expected argument values.
        keys (Tuple[str, ...]): Required keyword argument names.
        types_ (Tuple[Type, ...]): Expected argument types.
    """
    def __init__(self, dispatcher: Dispatcher, expected: Optional[Dict[str, Any]] = None,
                 keys: Optional[Tuple[str, ...]] = None, types_: Optional[Tuple[Type, ...]] = None) -> None:
        """Initialize the rule builder.

        Args:
            dispatcher (Dispatcher): The Dispatcher to add rules to.
            expected (Optional[Dict[str, Any]]): Expected argument values.
            keys (Optional[Tuple[str, ...]]): Required keyword argument names.
            types_ (Optional[Tuple[Type, ...]]): Expected argument types.
        """
        self.dispatcher = dispatcher
        self.expected = dict(expected or {})
        self.keys = tuple(keys or ())
        self.types_ = tuple(types_ or ())

    def values(self, **expected: Any) -> '_RuleBuilder':
        """Add or update expected argument values.

        Args:
            **expected: Keyword arguments with expected values.

        Returns:
            _RuleBuilder: Self, for method chaining.
        """
        self.expected.update(expected)
        return self

    def kwargs(self, *keys: str) -> '_RuleBuilder':
        """Add or update required keyword argument names.

        Args:
            *keys: Names of keyword arguments to check for presence.

        Returns:
            _RuleBuilder: Self, for method chaining.
        """
        self.keys = tuple(self.keys) + tuple(keys)
        return self

    def types(self, *types_: Type) -> '_RuleBuilder':
        """Set expected argument types.

        Args:
            *types_: Expected types for positional arguments.

        Returns:
            _RuleBuilder: Self, for method chaining.
        """
        self.types_ = tuple(types_)
        return self

    def __call__(self, fn: Callable) -> Dispatcher:
        """Register a function with the defined rule conditions.

        Args:
            fn (Callable): The function to register with the rule.

        Returns:
            Dispatcher: The Dispatcher instance, for method chaining.
        """
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        has_self = bool(params) and params[0].name in ("self", "cls")

        def condition(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> bool:
            """Check if the arguments match the defined conditions.

            Args:
                args (Tuple[Any, ...]): Positional arguments.
                kwargs (Dict[str, Any]): Keyword arguments.

            Returns:
                bool: True if the conditions are met, False otherwise.
            """
            try:
                bound = sig.bind_partial(*args, **kwargs).arguments
            except TypeError:
                return False

            for k, v in self.expected.items():
                if bound.get(k) != v:
                    return False

            if self.types_:
                ordered_vals = list(bound.values())
                if has_self:
                    ordered_vals = ordered_vals[1:]
                if not all(isinstance(a, t) for a, t in zip(ordered_vals, self.types_)):
                    return False

            for k in self.keys:
                if k not in bound:
                    return False
            return True

        self.dispatcher.add_rule(condition, fn)
        return self.dispatcher

def dispatcher(fn: Callable) -> Dispatcher:
    """Decorator to create a Dispatcher for a function or method.

    Args:
        fn (Callable): The function or method to decorate.

    Returns:
        Dispatcher: A Dispatcher instance wrapping the function.
    """
    return wraps(fn)(Dispatcher(fn))

if __name__ == "__main__":
    @dispatcher
    def func(*args: Any, **kwargs: Any) -> None:
        """Default function that raises NotImplementedError."""
        raise NotImplementedError("No matching rule")

    @func.values(name="avi").types(str, int)
    def _(name: str, age: int) -> str:
        """Handle case where name is 'avi' and arguments are str, int."""
        return f"{name} is {age}yo"

    @func.values(name="bob").types(str, int)
    def _(name: str, age: int) -> str:
        """Handle case where name is 'bob' and arguments are str, int."""
        return f"{name} is {age} years young"

    @func.kwargs("name", "age")
    def _(name: str, age: int) -> str:
        """Handle case with name and age keyword arguments."""
        return f"{name} is {age}yo"

    @func.kwargs("name", "age", "gender")
    def _(name: str, age: int, gender: str) -> str:
        """Handle case with name, age, and gender keyword arguments."""
        return f"{name} is {age}yo {gender}"

    print(func("avi", 40))  # Output: avi is 40yo
    print(func("bob", 29))  # Output: bob is 29 years young
    print(func("jery", 25, "male"))  # Output: jery is 25yo male

    class Person:
        """A class demonstrating Dispatcher usage with methods."""
        @dispatcher
        def say(self, *args: Any, **kwargs: Any) -> None:
            """Default method that raises NotImplementedError."""
            raise NotImplementedError("No matching rule")

        @say.values(name="avi").types(str, int)
        def _(self, name: str, age: int) -> str:
            """Handle case where name is 'avi' and arguments are str, int."""
            return f"{name} is {age}yo"

        @say.values(name="bob").types(str, int)
        def _(self, name: str, age: int) -> str:
            """Handle case where name is 'bob' and arguments are str, int."""
            return f"{name} is {age} years young"

        @say.kwargs("name", "age")
        def _(self, name: str, age: int) -> str:
            """Handle case with name and age keyword arguments."""
            return f"{name} is {age}yo"

        @say.kwargs("name", "age", "gender")
        def _(self, name: str, age: int, gender: str) -> str:
            """Handle case with name, age, and gender keyword arguments."""
            return f"{name} is {age}yo {gender}"

    p = Person()
    print(p.say("avi", 40))  # Output: avi is 40yo
    print(p.say("bob", 29))  # Output: bob is 29 years young
    print(p.say("jery", 25, "male"))  # Output: jery is 25yo male