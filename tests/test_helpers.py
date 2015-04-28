"""
Tests for validators.helpers test

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

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
