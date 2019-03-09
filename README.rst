==================================================
class_proxy - a transparent proxy class for Python
==================================================

.. image:: https://badge.fury.io/gh/herczy%2Fclass_proxy.svg
    :target: https://badge.fury.io/gh/herczy%2Fclass_proxy

.. image:: https://badge.fury.io/py/class_proxy.svg
    :target: https://badge.fury.io/py/class_proxy

.. image:: https://travis-ci.org/herczy/class_proxy.svg?branch=master
    :target: https://travis-ci.org/herczy/class_proxy

Introduction
============

`class_proxy` can be used to create simple proxy objects for any value. The
proxy can be any class.

For example, lets say that we have a parser and need to be able to tell where
a value came from (source file name, line number and column). We might have a
`Source` class handling this information:

.. code-block:: python

  class Source(object):
      def __init__(self, filename, line, column):
          self.filename = filename
          self.line = line
          self.column = column

      def __str__(self):
          return "file {}, line {}, column {}".format(
              self.filename, self.line, self.column
          )

      def __repr__(self):
          return "Source({!r}, {!r}, {!r})".format(
              self.filename, self.line, self.column
         )

If we attach this source to some class we control, there is no problem. But
what if we want to tell where an integer, string or any scalar, builtin came
from?

The solution is to make a wrapper for the scalar classes:

.. code-block:: python

   import class_proxy

   class SourceValue(object):
       def __init__(self, source):
           self.source = source

       def __str__(self):
           return "{} (from {})".format(
               class_proxy.instance(self), self.source
           )

       def __repr__(self):
           return "SourceValue({!r}, {!r})".format(
               class_proxy.instance(self), self.source
           )

   IntProxy = class_proxy.wrap_with(int, SourceValue)
   StrProxy = class_proxy.wrap_with(str, SourceValue)

   number = IntProxy(123, Source('example', 1, 2))
   print(number)  # will print: 1 (from file example, line 1, column 2)

   string = StrProxy('hello', Source('example', 5, 7))
   print(repr(number))  # will print: hello (from file example, line 5, column 7)

   other_number = IntProxy(456, Source('example', 7, 8))
   print(number < other_number)  # will print: True

The `class_proxy.instance` call will return the original, wrapped
instance for the proxy.

The `class_proxy.wrap_with` call will create a proxy class expecting the
wrapped value as the first parameter, while the remaining parameters are passed
to the `SourceValue` constructor.

When retrieving attributes from the proxy class (e.g. `IntProxy`), it
will look up the proxy base class first (e.g. `SourceValue`) and later
the wrapped class (e.g. `int`). This is the reason we care about what
class we're wrapping: we want to be able to wrap the class too, not just
the instance.

In case we're looking up members from the instance, at first we will look it up
from the instance of the proxy class, and then from the wrapped class.

If you don't care about class values, you can also omit the wrapped class:

.. code-block:: python

   GenericProxy = class_proxy.wrap_with(SourceValue)

   generic = GenericProxy(SomeGenericClass(1, 2), Source('example', 10, 0))

In this case, we wrap the `object`.

There is also a convenience wrapper for the `wrap_with` function, in case
you don't need to define it for multiple wrapped classes:

.. code-block:: python

   import class_proxy

   @class_proxy.proxy_of(int)
   class IntProxy(object):
       def clamp(self, minval, maxval):
           if self < minval:
               result = minval

           elif self > maxval:
               result = maxval

           else:
               result = class_proxy.instance(self)

           return IntProxy(result)

   value = IntProxy(50).clamp(-10, 10)
   print(value)  # will print: 10

This also has a generic variant:

.. code-block:: python

   import class_proxy

   @class_proxy.proxy
   class Proxy(object):
       def map(self, func):
           return func(class_proxy.instance(self))

   value = Proxy(100)
   print(value.map(lambda val: -val))  # will print: -100

Inspiration
===========

`class_proxy` was heavily inspired by `zyga/padme`, an excellent tool for
creating proxy classes. However, `padme` has a few problems:

* It generates a lot of logs, which can not only be annoying, but create odd
  infinite recursions when trying to format the wrapped value for a log string.
* The proxied special methods are written out manually, which seems like an
  unneccessary thing.

So with these limitations I felt the need to write a similar tool that
addresses the issues above.
