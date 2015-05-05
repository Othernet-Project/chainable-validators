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
        raise ValueError('value is required', 'required')
    return s


@chainable
def nonempty(s):
    if s in ['', [], {}]:
        seqtype = type(s)
        raise ValueError('value cannot be an empty {}'.format(seqtype),
                         'nonempty')
    return s


@chainable
def boolean(v):
    if v not in [True, False]:
        raise ValueError('{} must be True or False'.format(v),
                         'boolean')
    return v


def istype(t):
    @chainable
    def validator(v):
        if type(v) is not t:
            raise ValueError('value must be a {}'.format(t.__name__),
                             'istype')
        return v
    return validator


def isin(collection):
    @chainable
    def validator(s):
        if s not in collection:
            raise ValueError('value must be in {}'.format(collection),
                             'isin')
        return s
    return validator


def gte(num):
    @chainable
    def validator(v):
        if not v >= num:
            raise ValueError('value must be greater than {}'.format(num),
                             'gte')
        return v
    return validator


def lte(num):
    @chainable
    def validator(v):
        if not v <= num:
            raise ValueError('value must be less than {}'.format(num),
                             'lte')
        return v
    return validator


def match(regex):
    @chainable
    def validator(s):
        if not regex.match(s):
            raise ValueError('value does not match the expected format',
                             'match')
        return s
    return validator


def url(fn):
    try:
        return match(URL_RE)(fn)
    except ValueError:
        raise ValueError('value must be a valid URL', 'url')


def timestamp(fmt):
    @chainable
    def validator(s):
        try:
            datetime.datetime.strptime(s, fmt)
        except ValueError:
            raise ValueError("{} does not match the format '{}'".format(
                s, fmt), 'timestamp')
        return s
    return validator
