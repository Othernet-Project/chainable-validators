"""
Miscellaneous helper functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import operator

from .chain import chainable, make_chain


def OR(*fns):
    """ Validate with any of the chainable valdator functions """
    if len(fns) < 2:
        raise TypeError('At least two functions must be passed')

    @chainable
    def validator(v):
        for fn in fns:
            last = None
            try:
                return fn(v)
            except ValueError as err:
                last = err
        if last:
            raise last
    return validator


def NOT(fn):
    """ Reverse the effect of a chainable validator function """
    @chainable
    def validator(v):
        try:
            fn(v)
        except ValueError:
            return v
        raise ValueError('invalid')
    return validator


def spec_validator(spec, key=operator.itemgetter):
    """ Take a spec in dict form, and return a function that validates objects

    The spec maps each object's key to a chain of validator functions.

    The ``key`` argument can be used to customize the way value matching a spec
    key from the object. By default, it uses ``operator.itemgetter``. It should
    be assigned a function that takes a key value and returns a function that
    returns the vale from an object that is passed to it.
    """
    spec = {k: (key(k), make_chain(v)) for k, v in spec.items()}

    def validator(obj):
        errors = {}
        for k, v in spec.items():
            getter, chain = v
            val = getter(obj)
            try:
                chain(val)
            except ValueError as err:
                errors[k] = err
        return errors

    return validator
