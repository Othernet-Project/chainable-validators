"""
Tests for outernet_metadata.validators test

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re

import pytest

import validators.validators as mod

MOD = mod.__name__


fail = pytest.mark.xfail


def test_optional():
    """
    When optional() is called, it returns a validator that raises ReturnEarly
    if called with None, but not with other values.
    """
    fn = mod.optional()
    with pytest.raises(mod.ReturnEarly):
        fn(None)


@pytest.mark.parametrize('x', ['foo', 1, True, False, 0, '', 2.3])
def test_optional_with_value(x):
    """
    When optional() is called, it returns a function that does not raise for
    none-None values, and returns the value it was passed..
    """
    fn = mod.optional()
    assert fn(x) == x


def test_optional_with_default_value():
    """
    When optional() is called with some value value, then it returns a function
    that raises when it is called with either None or the value passed to
    optional().
    """
    fn = mod.optional('foo')
    with pytest.raises(mod.ReturnEarly):
        fn(None)
    with pytest.raises(mod.ReturnEarly):
        fn('foo')


def test_required():
    """
    When required() is called with None, then it raises ValueError.
    """
    with pytest.raises(ValueError):
        mod.required(None)


@pytest.mark.parametrize('x', ['foo', 1, True, False, 0, '', 2.3])
def test_required_with_value(x):
    """
    When required() is called with a none-None value, then it returns that
    value.
    """
    ret = mod.required(x)
    assert ret == x


@pytest.mark.parametrize('x', ['', [], {}])
def test_nonempty(x):
    """
    When nonempty is called with empty string, list or dict, then it raises
    ValueError.
    """
    with pytest.raises(ValueError):
        mod.nonempty(x)


@pytest.mark.parametrize('x', ['foo', [1, 2], {'bar': 'baz'}])
def test_nonempty_with_value(x):
    """
    When nonemtpy is called with non-empty string, list or dict, then it does
    not raise, and returns the value passed to it.
    """
    assert mod.nonempty(x) == x


@pytest.mark.parametrize('x', ['foo', 2.3, None, fail(True), fail(False)])
def test_boolean(x):
    """
    Given a non-boolean value, when boolean() is called with it, then it raises
    ValueError.
    """
    with pytest.raises(ValueError):
        mod.boolean(x)


@pytest.mark.parametrize('x', [True, False, 1, 0, fail(None)])
def test_boolean_with_bool_value(x):
    """
    Given a boolean value, when boolean() is called with it, then it does not
    raise, and returns the value passed to it.
    """
    assert mod.boolean(x) == x


@pytest.mark.parametrize('x', [
    (1, int),
    (2.5, float),
    ('foo', str),
    (b'bar', bytes),
    (False, bool),
    fail(('bar', bool)),
    fail((12, str)),
    fail((None, int)),
])
def test_istype(x):
    """
    Given a value and its correct type, calling istype() with the type returns
    a function that returns the value it is called with.
    """
    v, t = x
    validator = mod.istype(t)
    assert validator(v) == v


@pytest.mark.parametrize('x', [
    ('bar', bool),
    (12, str),
    (None, int),
    fail((1, int)),
    fail((2.5, float)),
    fail(('foo', str)),
    fail((b'bar', bytes)),
    fail((False, bool)),
])
def test_istype_wrong_type(x):
    """
    Given a value and type that doesn't match the value, calling istype() with
    the type returns a function that raises ValueError when called with the
    value.
    """
    v, t = x
    validator = mod.istype(t)
    with pytest.raises(ValueError):
        validator(v)


@pytest.mark.parametrize('x', [
    ('a', 'foobar'),
    (1, [1, 2, 3, 4]),
    ('a', {'a': 1, 'b': 2}),
])
def test_isin(x):
    """
    Given a sequence, and a value from the sequence, when isin() is called with
    the sequence, then it returns a function that returns the value when called
    with it.
    """
    v, seq = x
    validator = mod.isin(seq)
    assert validator(v) == v


@pytest.mark.parametrize('x', [
    ('x', 'foobar'),
    (0, [1, 2, 3, 4]),
    ('x', {'a': 1, 'b': 2}),
])
def test_isin_not_found(x):
    """
    Given a sequence, and a value that does not belong to it, when isin() is
    called with the sequence, then it returns a function that raises ValueError
    when called with the value.
    """
    v, seq = x
    validator = mod.isin(seq)
    with pytest.raises(ValueError):
        validator(v)


@pytest.mark.parametrize('x', [
    (1, 2),
    (3.4, 4.2),
    (3, 3.5),
    (3, 3),
    fail((2.9, 3)),
    fail((4, 9.2)),
])
def test_gte(x):
    """
    Given two numeric values where one is greater than or equal to the other,
    when gte() is called with the smaller value, then it returns a function
    that will return the value passed to it when called with the larger value.
    """
    sm, lg = x
    validator = mod.gte(sm)
    assert validator(lg) == lg


@pytest.mark.parametrize('x', [
    (1, 2),
    (3.4, 4.2),
    (3, 3.5),
    fail((3, 3)),
    fail((2.9, 3)),
    fail((4, 9.2)),
])
def test_gte_reverse(x):
    """
    Given two numeric values where one is greater than or equal to the other,
    when gte() is called with the larger value, then it returns a function that
    will raise Validation error when passed the smaller value.
    """
    sm, lg = x
    validator = mod.gte(lg)
    with pytest.raises(ValueError):
        validator(sm)


@pytest.mark.parametrize('x', [
    (1, 2),
    (3.4, 4.2),
    (3, 3.5),
    (3, 3),
    fail((2.9, 3)),
    fail((4, 9.2)),
])
def test_lte(x):
    """
    Given two numeric values where one is greater than or equal to the other,
    when lte() is called with the larger value, then it returns a function
    that will return the the smaller value when called with it.
    """
    sm, lg = x
    validator = mod.lte(lg)
    assert validator(sm) == sm


@pytest.mark.parametrize('x', [
    (1, 2),
    (3.4, 4.2),
    (3, 3.5),
    fail((3, 3)),
    fail((2.9, 3)),
    fail((4, 9.2)),
])
def test_lte_reverse(x):
    """
    Given two numeric values where one is greater than or equal to the other,
    when lte() is called with the smaller value, then it returns a function
    that raises ValueError when called with the larger value.
    """
    sm, lg = x
    validator = mod.lte(sm)
    with pytest.raises(ValueError):
        validator(lg)


def test_match():
    """
    Given a regex object and a string that matches the regex pattern, when
    match() is called with the object, then it returns a function that returns
    the string when called with it.
    """
    r = re.compile('^foo.*baz$')
    s = 'foobarbaz'
    validator = mod.match(r)
    assert validator(s) == s


def test_no_match():
    """
    Given a regex object and a string that does not match the regex pattern,
    when match() is called with the object, then it returns a function that
    raises ValueError exception when called with the sting.
    """
    r = re.compile('^foo.*baz$')
    s = 'foobarbazooka'
    validator = mod.match(r)
    with pytest.raises(ValueError):
        validator(s)


@pytest.mark.parametrize('x', [
    'http://www.example.com/',
    'http://example.com/',
    'https://www.example.com/'
    'https://example.com/',
    'http://123.456.789.012/',
    'http://localhost/',
    'ftp://example.com/',
    'ftps://example.com/',
    'outernet://example.com/',
    'outernet://user.outernet/',
    'http://example.com:1234/',
    'http://example.com/foo/bar',
    'http://example.com/foo/bar?baz=1',
    'http://example.com/foo/bar?baz',
])
def test_url(x):
    """
    Given a valid URL, when url() is called with the URL, then it returns the
    URL.
    """
    assert mod.url(x) == x


def test_invalid_url():
    """
    Given an invalid URL, when url() is called with the URL, then it raises
    ValueError.
    """
    with pytest.raises(ValueError):
        mod.url('this is an invalid URL')


@pytest.mark.parametrize('x', [
    ('2015-04-29', '%Y-%m-%d'),
    ('2015-04-29 17:00:01', '%Y-%m-%d %H:%M:%S'),
    fail(('2015-29-04', '%Y-%m-%d')),
    fail(('2015-04-29', '%H:%M:%S')),
])
def test_timestamp(x):
    """
    Given a time- or datestamp and matching format in strptime() notation, when
    timestamp() is called with the format string, then it returns a function
    which returns the timestamp when called with it.
    """
    s, fmt = x
    validator = mod.timestamp(fmt)
    assert validator(s) == s


@pytest.mark.parametrize('x', [
    fail(('2015-04-29', '%Y-%m-%d')),
    fail(('2015-04-29 17:00:01', '%Y-%m-%d %H:%M:%S')),
    ('2015-29-04', '%Y-%m-%d'),
    ('2015-04-29', '%H:%M:%S'),
])
def test_timestamp_reverse(x):
    s, fmt = x
    validator = mod.timestamp(fmt)
    with pytest.raises(ValueError):
        validator(s)


@pytest.mark.parametrize('x', [
    ([1, 2], mod.istype(int)),
    (["a", "bb"], mod.istype(str)),
])
def test_listof_valid(x):
    (value, item_validator) = x
    validator = mod.listof(item_validator)
    assert validator(value) == value


@pytest.mark.parametrize('x', [
    (None, None),
    ({}, None),
    (1, None),
    ("test", None),
    ([1, 2], mod.istype(str))
])
def test_listof_invalid(x):
    (value, item_validator) = x
    validator = mod.listof(item_validator)
    with pytest.raises(ValueError):
        validator(value)
