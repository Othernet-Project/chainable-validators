"""
Built-in validator functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime

from .re_patterns import URL_RE
from .chain import chainable, ReturnEarly


def optional(default=None):
    @chainable
    def validator(s):
        if s in [None, default]:
            raise ReturnEarly()
        return s
    return validator


@chainable
def required(s):
    if s is None:
        raise ValueError('required value missing')
    return s


@chainable
def nonempty(s):
    if s in ['', [], {}]:
        raise ValueError('empty sequence')
    return s


@chainable
def boolean(v):
    if v not in [True, False]:
        raise ValueError('not boolean')
    return v


def istype(t):
    @chainable
    def validator(v):
        if type(v) is not t:
            raise ValueError('not {}'.format(t.__name__))
        return v
    return validator


def isin(collection):
    @chainable
    def validator(s):
        if s not in collection:
            raise ValueError('not in collection')
        return s
    return validator


def gte(num):
    @chainable
    def validator(v):
        if not v >= num:
            raise ValueError('value too small')
        return v
    return validator


def lte(num):
    @chainable
    def validator(v):
        if not v <= num:
            raise ValueError('value too large')
        return v
    return validator


def match(regex):
    @chainable
    def validator(s):
        if not regex.match(s):
            raise ValueError('wrong format')
        return s
    return validator


def url(fn):
    return match(URL_RE)(fn)


def timestamp(fmt):
    @chainable
    def validator(s):
        datetime.datetime.strptime(s, fmt)
        return s
    return validator
