"""
Tests for validators.helpers test

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import validators.helpers as mod


def test_or(chainable_func):
    """
    Given two or more chainable functions, when passing them to OR(), then it
    returns a function that validates using the first function that does not
    raise ValidationError.
    """
    x, cx = chainable_func()
    y, cy = chainable_func()
    fn = mod.OR(cx, cy)
    ret = fn(1)
    assert ret == x.return_value
    assert x.called
    assert not y.called


def test_or_validation_error(chainable_func):
    """
    Given two of more chainable functions of which first one raises
    ValueError, when passing them to OR(), then second one is invoked to
    perform the validation, and validation does not fail.
    """
    x, cx = chainable_func()
    y, cy = chainable_func()
    x.side_effect = ValueError
    fn = mod.OR(cx, cy)
    ret = fn(1)
    assert ret == y.return_value
    assert x.called
    assert y.called


def test_or_all_fail(chainable_func):
    """
    Given two or more chainable functions of which all raise ValueError
    exception, when passing them to OR(), then ValueError is raied.
    """
    x, cx = chainable_func()
    y, cy = chainable_func()
    x.side_effect = ValueError
    y.side_effect = ValueError
    fn = mod.OR(cx, cy)
    with pytest.raises(ValueError):
        fn(1)


def test_not(chainable_func):
    """
    Given a chainable function, when NOT() is called with the function, then a
    function is returned that reverses the effects.
    """
    x, cx = chainable_func()
    rev = mod.NOT(cx)
    with pytest.raises(ValueError):
        rev(1)
    x.side_effect = ValueError
    assert rev(1) == 1


def test_spec_validator(chainable_func):
    """
    Given a validation spec as dict that maps object keys/attributes to
    validation chain, when calling spec_validator() with the dict, then it
    returns a function that will validate an object against the spec.
    """
    x1, cx1 = chainable_func()
    y1, cy1 = chainable_func()
    x2, cx2 = chainable_func()
    y2, cy2 = chainable_func()
    spec = {
        'foo': [cx1, cy1],
        'bar': [cx2, cy2],
    }
    data = {'foo': 1, 'bar': 2}
    fn = mod.spec_validator(spec)
    fn(data)
    x1.assert_called_once_with(1)
    y1.assert_called_once_with(x1.return_value)
    x2.assert_called_once_with(2)
    y2.assert_called_once_with(x2.return_value)


def test_spec_validator_custom_getter(chainable_func):
    """
    Given a validation spec and a custom getter, when calling spec_validator()
    with the spec and getter, it is able to correctly pass the object
    values to chains.
    """
    import operator

    x1, cx1 = chainable_func()
    y1, cy1 = chainable_func()
    x2, cx2 = chainable_func()
    y2, cy2 = chainable_func()
    spec = {
        'foo': [cx1, cy1],
        'bar': [cx2, cy2],
    }

    obj = mock.Mock()
    obj.foo = 1
    obj.bar = 2

    fn = mod.spec_validator(spec, key=operator.attrgetter)
    fn(obj)
    x1.assert_called_once_with(1)
    y1.assert_called_once_with(x1.return_value)
    x2.assert_called_once_with(2)
    y2.assert_called_once_with(x2.return_value)


def test_spec_validator_failure(chainable_func):
    """
    Given a vlidation spec and and object with invalid data, when calling
    spec_validator() on the spec and then calling the returned validator on the
    object, then it should return a dict that mapes failed keys to error
    objects.
    """
    x1, cx1 = chainable_func()
    y1, cy1 = chainable_func()
    x2, cx2 = chainable_func()
    y2, cy2 = chainable_func()
    y2.side_effect = ValueError
    spec = {
        'foo': [cx1, cy1],
        'bar': [cx2, cy2],
    }
    data = {'foo': 1, 'bar': 2}
    fn = mod.spec_validator(spec)
    ret = fn(data)
    assert 'bar' in ret
    assert 'foo' not in ret
    assert isinstance(ret['bar'], ValueError)
