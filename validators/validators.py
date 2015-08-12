"""
Built-in validator functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re
import datetime

from .re_patterns import URL_RE
from .helpers import spec_validator
from .chain import chainable, ReturnEarly

RELPATH_RE = re.compile(r'^[^/]+(/[^/]+)*$')
CONTENT_TYPES = ['html', 'video', 'audio', 'image', 'generic', 'app']


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


@chainable
def deprecated(k):
    if k != None:
        raise ValueError('Key is deprecated, remove it or ignore this error',
                         'deprecated')
    return k


def isinstance(t):
    @chainable
    def validator(v):
        if not isinstance(v, t):
            raise ValueError('value must be a {}, was {}'.format(
                t.__name__, type(v).__name__), 'istype')
        return v
    return validator


def istype(t):
    @chainable
    def validator(v):
        if type(v) is not t:
            raise ValueError('value must be a {}, was {}'.format(
                t.__name__, type(v).__name__), 'istype')
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
        try:
            if not regex.match(s):
                raise ValueError('value does not match the expected format',
                                 'match')
        except TypeError:
            raise ValueError('value of {} type cannot be tested for '
                             'format'.format(type(s).__name__),
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


def min_len(min=1):
    @chainable
    def validator(v):
        if  v == None or len(v) < min:
            raise ValueError("Key must be longer than {}, was {}".format(min,v),
                             'min_length')
        return v
    return validator


def content_type(TYPE_SPECS):
    @chainable
    def validator(v):
        errors = {}
        for key in v:
            value = v[key]
            key_string = 'content.{}'.format(key)

            if key not in TYPE_SPECS:
                errors['content'] = {
                    key: ValueError('content type must be one of '
                                   '{}'.format(CONTENT_TYPES), 'content_type')}
            elif type(value) != dict:
                errors['content'] = {
                    key: ValueError('{} must be a '
                                    'dict'.format(key), 'content_type')}
            else:
                VALIDATOR = spec_validator(
                    TYPE_SPECS[key], key=lambda k: lambda obj: obj.get(k))
                e = VALIDATOR(value)
                if e:
                    errors[key_string] = e
                elif key == 'audio':
                    i = 0
                    spec = TYPE_SPECS['audio.playlist']
                    VALIDATOR = spec_validator(
                        spec, key=lambda k: lambda obj: obj.get(k))
                    for item in value['playlist']:
                        i += 1
                        e = VALIDATOR(item)
                        if e:
                            s = key_string + '.' + str(i)
                            errors[s] = e
                elif key == 'image':
                    i = 0
                    spec = TYPE_SPECS['image.album']
                    VALIDATOR = spec_validator(
                        spec, key=lambda k: lambda obj: obj.get(k))
                    for item in value['album']:
                        i += 1
                        e = VALIDATOR(item)
                        if e:
                            s = key_string + '.' + str(i)
                            errors[s] = e
        final_set = []
        if errors:
            for key in errors:
                set = []
                for k in errors[key]:
                    key_string = '.'.join([key, k])
                    msg = errors[key][k].args[0]
                    string = '{}: {}'.format(key_string, msg)
                    set.append(string)
                final_set.append('\n'.join(set))
            error_string = '\n' + '\n'.join(final_set)
            raise ValueError(error_string, 'content_type')
        return v
    return validator
