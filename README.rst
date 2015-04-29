====================
Chainable Validators
====================

This package contains a set of simple functions to facilitate creation of
chainable validator methods for developing data validation schemata.

Although it provides a few validation function, it's main purpose is
extensibility.

Installing
==========

The PyPI package name is ``chainable-validators``. You can install the package
using ``pip`` or ``easy_install``::

    pip install chainable-validators

    easy_install chainable-validators

Basic concepts
==============

The basis of all validation are chainable validators (validation functions) and
the validation chains which are created using ``make_chain()`` calls.

The chainable validators are found in the ``validators.validators`` module. For
convenience, they can be imported directly from the ``validators`` package::

    >>> from validators import required, istype, gte

The chainable validators can be used stand-alone or as part of a chain. For
standalone usage, pass the value to the validator. ::

    >>> required(None)
    Traceback (most recent call last):
    ...
    ValueError: required value missing

Some validators are parametric. They are first invoked with a parameter, and
the return value is then used as a chainable validator. ::

    >>> isint = istype(int)
    >>> isint('foo')
    Traceback (most recent call last):
    ...
    ValueError: not int

To build a chain of desired validators, we first compile a list of chainable
validators::

    >>> from validators import make_chain
    >>> fns = [required, istype(int), gte(2)]
    >>> chain = make_chain(fns)
    >>> chain(None)
    Traceback (most recent call last):
    ...
    ValueError: required value missing
    >>> chain('1')
    Traceback (most recent call last):
    ...
    ValueError: not int
    >>> chain(1)
    Traceback (most recent call last):
    ...
    ValueError: value too small
    >>> chain(3)
    3

The validators in the chain are invoked in order until the last one is called,
or ``ValueError`` or ``validators.ReturnEarly`` is raised. When no exceptions
are raised, the return value of the last chainable validator is returned. In
case ``ReturnEarly`` is raised, it is not propagated to the chain's caller, but
instead the original value is returned.

List of built-in validators
===========================

The following is a list of built-in vaidators.

Validators can be parametric or simple. Simple validators can be used directly.
Parametric validators take an argument and return a chainable validator
functions.

In the list below, if you encounter a validator that looks like ``foo(bar)``,
it's a parametric validator.

- ``optional(default=None)`` - interrupts validation chain if value is None or
  a user-supplied default value
- ``required`` - rejects None
- ``nonemtpy`` - rejects empty sequences (string, list, dict)
- ``boolean`` - reject non-boolean values (other than True, False, 1, and 0)
- ``istype(t)`` - rejects values that are not of type ``t``
- ``isin(collection)`` - rejects values that are not in ``collection``
  (collection is a sequence such as string, list, or dict)
- ``gte(num)`` - rejects values that are not greater than or equal to ``num``
- ``lte(num)`` - rejects values that are not less than or equal to ``num``
- ``match(regex)`` - rejects values that do not match the ``regex`` object
  (``regex`` object is a valid ``re.RegExp`` instance or object with a
  ``match()`` method)
- ``url`` - rejects values that are not URLs
- ``timestamp(fmt)`` - rejects values that cannot be converted to ``datetime``
  using ``datetime.strptime()`` and given format string

Helper functions
================

There are a few helper functions that help you modify the behavior or one or
more functions in the chain.

- ``OR(*fns)`` - rejects value if and only if all of the functions passed to it
  fail to validate, otherwise passes
- ``NOT(fn)`` - reverses the behavior of ``fn``

For example::

    >>> my_chain = [foo, OR(bar, baz), NOT(fam)]

This chain will validate using ``foo`` first, then either ``bar`` or ``baz``
(whichever passes), then ``fam``, reversing the results of ``fam`` (if it
raises, then the validation will succeed and vice versa).

Spec validator
==============

Another helper function, that is not mentioned in the previous section, is
``spec_validator()`` factory function. It takes a spec, which is a dict mapping
key/attribute names to chains and returns a validator function that validates
objects.

Let's take a look at an example, and then explain things as we go::

    >>> import re
    >>> from validator import *
    >>> spec = {
    ...     'foo': [required, istype(int)],
    ...     'bar': [optional, match(re.compile(r'te.*')],
    ...     'baz': [optional, boolean]
    ... }

Each key in spec represents the key we expect to find in the object. The key
could be a dictionary key, list/tuple index, or an object attribute. It could
also be an arbitrary value based on which the value will be extracted.

The way keys map to values is defined by a key function which can be passed
using the ``key`` argument. This function must accept a spec key name and
return a function that returns the value given an object. The default key
function is ``operator.itemgetter``. For example, if we have an object that as
attributes we want to validate, we could create the validator like so::

    >>> import operator
    >>> attr_validator = spec_validator(spec, key=operator.attrgetter)

Each key maps to an iterable which represents the validator chain. Chains are
applied to values matching the key.

The ``spec_validator()`` function returns a validator function. ::

    >>> validator = spec_validator(spec)

When passed the object to be validated, the validator function returns a dict
which maps keys to any ``ValueError`` exceptions raised by the individual
chains. If data is valid, the dict is empty. ::

    >>> data = {'foo': 1, 'bar': 'test', 'baz': None}
    >>> validator(data)
    {}
    >>> data['foo'] = None
    >>> validator(data)
    {'foo': ValueError('required value is missing')}

Thanks to this behavior, you can test whether object is valid, by testing if
the returned dict is empty.

Writing your own validators
===========================

It is possible to write your own validators. To write a simple chainable
validator, use the ``validators.chain.chainable`` decorator. ::

    >>> from validators import chainable
    >>> @chainable
    ... def my_validator(s):
    ...     if not s.startswith('foo'):
    ...         raise ValueError('does not start with foo')
    ...     return s
    ... 
    >>> my_validator('foobar')
    'foobar'
    >>> my_validator('barfoo')
    Traceback (most recent call last):
    ...
    ValueError: does not start with foo

To write a parametric validator, define the chainable validator in a closure::

    >>> def my_parametric(start):
    ...     @chainable
    ...     def validator(s):
    ...         if not s.startswith(start):
    ...             raise ValueError('does not sart with {}'.format(start))
    ...         return s
    ...     return validator
    ... 
    >>> validator = my_parametric('baz')
    >>> validator('bazfoo')
    'bazfoo'
    >>> validator('foo')
    Traceback (most recent call last):
    ...
    ValueError: does not sart with baz

Now you can use these validators in chains like other validators.

Reporting bugs
==============

Please report any bugs or feature requests to the `issue tracker`_.

.. _issue tracker: https://github.com/Outernet-Project/chainable-validators/issues
