"""
Miscellaneous helper functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from .chain import chainable


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
