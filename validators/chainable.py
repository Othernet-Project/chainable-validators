"""
Helpers for building chainable validator functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools


class ReturnEarly(Exception):
    """ Raised to cause the validator chain to return early """
    pass


def chainable(fn):
    """ Make function a chainable validator

    The returned function is a chainable validator factory which takes the next
    function in the chain and returns a chained version of the original
    validator: ``fn(next(value))``.

    The chainable validators are used with the ``make_chain()`` function.
    """
    @functools.wraps(fn)
    def wrapper(nxt=lambda x: x):
        if hasattr(nxt, '__call__'):
            return lambda x: nxt(fn(x))
        # Value has been passsed directly, so we don't chain
        return fn(nxt)
    return wrapper


def make_chain(fns):
    """ Take a list of chainable validators and return a chained validator

    The functions should be decorated with ``chainable`` decorator.

    Any exceptions raised by any of the validators are propagated except for
    ``ReturnEarly`` exception which is trapped. When ``ReturnEarly`` exception
    is trapped, the original value passed to the chained validator is returned
    as is.
    """
    chain = lambda x: x
    for fn in reversed(fns):
        chain = fn(chain)

    def validator(v):
        try:
            return chain(v)
        except ReturnEarly:
            return v

    return validator
