"""
Transparent class proxy module.

A wrapper class can be created using the function `wrap_with` or
the decorators `proxy_of` (if the wrapped object type is specified
explicitly) or `proxy` (if the wrapped object isn't specified).
"""

__all__ = ["wrap_with", "proxy_of", "proxy", "instance", "reset_proxy_cache"]
IGNORE_WRAPPED_METHODS = frozenset(
    (
        "__new__",
        "__init__",
        "__getattr__",
        "__setattr__",
        "__delattr__",
        "__getattribute__",
    )
)
PROXY_CACHE = {}


def wrap_with(class_0, class_1=None, name=None):
    """
    Wrap a class with a proxy.

    This function can be called in two ways:

    If the wrapped class is specified, `wrap` will take two class parameters,
    the wrapped class and the proxy class:

    >>> class Proxy(object):
    ...     pass
    >>> print(wrap_with(int, Proxy).__name__)
    Proxy[int]

    If the wrapped class is not specified, `wrap` will only take the proxy class
    as a parameter:

    >>> print(wrap_with(Proxy).__name__)
    Proxy[object]

    Custom class names can also be specified:
    >>> print(wrap_with(int, Proxy, name="MyName").__name__)
    MyName
    """

    if class_1 is None:
        wrapped_class = object
        proxy_class = class_0

    else:
        wrapped_class = class_0
        proxy_class = class_1

    return _wrap_with_raw(wrapped_class, proxy_class, name)


def proxy_of(wrapped_class, name=None):
    """
    Decorator for making typed proxy classes.

    This works like the `wrap_with` method, except as a decorator.

    Usage:

    >>> @proxy_of(int)
    ... class Proxy(object):
    ...     pass
    >>> print(Proxy.__name__)
    Proxy[int]

    Custom names can also be specified:
    >>> @proxy_of(int, name="MyProxy")
    ... class Proxy(object):
    ...     pass
    >>> print(Proxy.__name__)
    MyProxy
    """

    def _decorator(proxy_class):
        return wrap_with(wrapped_class, proxy_class, name)

    return _decorator


def proxy(proxy_class):
    """
    Decorator for making generic proxy classes.

    This works like the `wrap_with` method, except as a decorator.

    Usage:

    >>> @proxy
    ... class Proxy(object):
    ...     pass
    >>> print(Proxy.__name__)
    Proxy[object]
    """

    return wrap_with(proxy_class)


def instance(obj):
    """
    Return the instance the proxy is wrapping.

    Usage:

    >>> class Example(object):
    ...     pass
    >>> class Proxy(object):
    ...     pass
    >>> Proxy = wrap_with(Example)
    >>> example = Example()
    >>> proxy_obj = Proxy(example)
    >>> instance(proxy_obj) is example
    True
    """

    return obj.__instance__


def reset_proxy_cache():
    """
    Reset all cached proxy classes.

    Only call this if you want to clear all cached proxy classes.
    """

    global PROXY_CACHE
    PROXY_CACHE.clear()


def _wrap_with_raw(wrapped_class, proxy_class, name):
    global PROXY_CACHE

    key = (wrapped_class, proxy_class, name)
    if key not in PROXY_CACHE:
        PROXY_CACHE[key] = _create_raw_wrapper(wrapped_class, proxy_class, name)

    return PROXY_CACHE[key]


def _create_raw_wrapper(wrapped_class, proxy_class, name):
    instances = _instance_wrapper()

    common = _mro_common(wrapped_class, proxy_class)
    base_methods = _resolve_proxy_members(proxy_class, common)
    base_methods.update(IGNORE_WRAPPED_METHODS)
    resolution = _resolve_wrapped_members(wrapped_class, base_methods)

    members = {}
    members.update(
        {
            name: _proxied_value(base, name, instances)
            for name, base in resolution.items()
        }
    )
    members.update(proxy_class.__dict__)

    proxy_init = _resolve_without_get(proxy_class, "__init__")

    @_overwrite_method(members)
    def __init__(self, inner, *args, **kwargs):
        if not isinstance(inner, wrapped_class):
            raise TypeError(
                "type {!r} cannot wrap object {!r} with type {!r}".format(
                    type(self), inner, type(inner)
                )
            )
        instances.set_instance(self, inner)
        proxy_init(self, *args, **kwargs)

    @_overwrite_method(members, name="__instance__")
    @property
    def _instance_property(self):
        return instances.get_instance(self)

    if name is None:
        name = "{}[{}]".format(proxy_class.__name__, wrapped_class.__name__)

    return type(name, (proxy_class,), members)


def _overwrite_method(members, name=None):
    def _decorator(func):
        fname = name
        if fname is None:
            fname = func.__name__

        members[fname] = func
        return func

    return _decorator


class _deleted(object):
    pass


class _proxied_value(object):
    def __init__(self, base, name, instances):
        self._base = base
        self._name = name
        self._instances = instances

    def __get__(self, instance, owner):
        state = self._instances.get_state(instance)
        if self._name in state:
            result = state[self._name]

        elif self._name in self._base.__dict__:
            result = self._base.__dict__[self._name]
            owner = self._base
            if instance is not None:
                instance = self._instances.get_instance(instance)

        else:
            assert 0, "unreachable code"

        if result is _deleted:
            raise AttributeError(
                "type object {!r} has no attribute {!r}".format(
                    owner.__name__, self._name
                )
            )

        if hasattr(result, "__get__"):
            result = result.__get__(instance, owner)

        return result

    def __set__(self, instance, value):
        state = self._instances.get_state(instance)
        state[self._name] = value

    def __delete__(self, instance):
        state = self._instances.get_state(instance)
        state[self._name] = _deleted


class _instance_wrapper(object):
    def __init__(self):
        self._wrapped_objects = {}
        self._states = {}

    def set_instance(self, proxy, instance):
        self._wrapped_objects[id(proxy)] = instance

    def get_instance(self, proxy):
        return self._wrapped_objects[id(proxy)]

    def del_instance(self, proxy):
        del self._wrapped_objects[id(proxy)]
        self._states.pop(id(proxy), None)

    def get_state(self, proxy):
        if id(proxy) not in self._states:
            self._states[id(proxy)] = {}

        return self._states[id(proxy)]


def _resolve_without_get(cls, name):
    for base in cls.__mro__:
        if name in base.__dict__:
            return base.__dict__[name]

    raise AttributeError(name)


def _mro_common(left, right):
    left_mro = list(left.__mro__)
    left_mro.reverse()

    right_mro = list(right.__mro__)
    right_mro.reverse()

    result = [
        left_base
        for left_base, right_base in zip(left_mro, right_mro)
        if left_base == right_base
    ]
    result.reverse()

    return result


def _resolve_proxy_members(proxy_class, common):
    base_methods = set()
    for base in reversed(proxy_class.__mro__):
        if base in common:
            continue

        for name in base.__dict__.keys():
            base_methods.add(name)
    return base_methods


def _resolve_wrapped_members(wrapped_class, base_methods):
    resolution = {}
    for base in reversed(wrapped_class.__mro__):
        for name in base.__dict__.keys():
            if name in base_methods:
                continue

            resolution[name] = base

    return resolution
