import inspect

class SelfAttr:
    """
    Helper class to specify that a method parameter should take
    its default value from an instance attribute.

    Example:
        class MyClass:
            def __init__(self):
                self.mult = 2

            @method_dispatcher
            def method(self, x: int, y: int = SelfAttr("mult")):
                return x * y

        obj = MyClass()
        obj.method(5)  # y defaults to obj.mult
    """
    def __init__(self, attr):
        self.attr = attr


class FuncDispatcher:
    """
    Dispatcher for regular functions. Supports multiple variants
    of the same function, default arguments, and type hint checking.

    Usage:
        @dispatcher
        def func(a: int, b: int):
            return a + b

        @func.reg()
        def _(a: int, b: int, c: int = 3):
            return a * b * c

        func(2, 4)      # 6
        func(2, 4, 3)   # 24
    """
    def __init__(self, func):
        self.funcs = []
        self.register(func)

    def register(self, func):
        """
        Register a new function variant.
        """
        sig = inspect.signature(func)
        self.funcs.append((func, sig))
        return func

    def reg(self):
        """
        Decorator for registering a new function variant.
        """
        def decorator(func):
            return self.register(func)
        return decorator

    def __call__(self, *args, **kwargs):
        """
        Call the appropriate function variant based on the provided arguments.
        Raises TypeError if no variant matches.
        """
        for func, sig in self.funcs:
            try:
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()

                # Check type hints
                ok = True
                for name, value in bound.arguments.items():
                    ann = sig.parameters[name].annotation
                    if ann is not inspect._empty and not isinstance(value, ann):
                        ok = False
                        break
                if ok:
                    return func(*bound.args, **bound.kwargs)
            except TypeError:
                continue
        raise TypeError("No matching function signature found")


class MethodDispatcher:
    """
    Dispatcher for instance methods. Supports multiple variants, default arguments,
    type hints, and automatic resolution of SelfAttr parameters.

    Usage:
        class MyClass:
            def __init__(self):
                self.mult = 2

            @method_dispatcher
            def method(self, x: int, y: int = SelfAttr("mult")):
                return x * y

        obj = MyClass()
        obj.method(5)      # 10 (y defaults to obj.mult)
        obj.method(5, 3)   # 15 (y explicitly passed)
    """
    def __init__(self, func):
        self.funcs = []
        self.register(func)

    def register(self, func):
        """
        Register a new method variant.
        """
        sig = inspect.signature(func)
        self.funcs.append((func, sig))
        return func

    def reg(self):
        """
        Decorator for registering a new method variant.
        """
        def decorator(func):
            return self.register(func)
        return decorator

    def __get__(self, instance, owner):
        """
        Descriptor to bind 'self' automatically when accessing the method.
        """
        if instance is None:
            return self

        def bound_method(*args, **kwargs):
            return self.__call__(instance, *args, **kwargs)

        return bound_method

    def __call__(self, self_obj, *args, **kwargs):
        """
        Call the appropriate method variant, resolving SelfAttr parameters
        and checking type hints. Raises TypeError if no variant matches.
        """
        for func, sig in self.funcs:
            params = list(sig.parameters.values())
            if not params or params[0].name != "self":
                continue  # Skip if first parameter is not 'self'

            try:
                bound_args = {"self": self_obj}
                args_iter = iter(args)
                for param in params[1:]:
                    try:
                        val = next(args_iter)
                    except StopIteration:
                        if param.name in kwargs:
                            val = kwargs[param.name]
                        elif isinstance(param.default, SelfAttr):
                            val = getattr(self_obj, param.default.attr)
                        else:
                            val = param.default
                    bound_args[param.name] = val

                # Check type hints
                ok = True
                for param in params:
                    ann = param.annotation
                    if ann is not inspect._empty and not isinstance(bound_args[param.name], ann):
                        ok = False
                        break

                if ok:
                    return func(**bound_args)

            except Exception:
                continue

        raise TypeError("No matching function signature found")


# Short aliases / API
dispatcher = FuncDispatcher
method_dispatcher = MethodDispatcher
