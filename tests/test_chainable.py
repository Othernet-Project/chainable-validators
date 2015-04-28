"""
Tests for validators.chainable module

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import validators.chain as mod

MOD = mod.__name__


def test_chainable(func, chainable_func):
    """
    Given chainable-decorated function, when it is called with another function
    as argument, then it should return a chained function where decorated
    function's output is passed to second function as argument.
    """
    x, cx = chainable_func()
    y = func()
    cy = cx(y)
    ret = cy(1)
    assert ret == y.return_value
    y.assert_called_once_with(x.return_value)
    x.assert_called_once_with(1)


def test_chainable_with_value(func, chainable_func):
    """
    Given a chainable-decorated function, when it is called with a non-callable
    value, then the undecorated function should be called.
    """
    x, cx = chainable_func()
    ret = cx(1)
    assert ret == x.return_value
    x.assert_called_once_with(1)


def test_make_chain(chainable_func):
    """
    Given a set of chainable functions, when they are passed to the
    make_chain() function as a list, then a function representing the chain of
    all functions should be returned.
    """
    x, cx = chainable_func()
    y, cy = chainable_func()
    z, cz = chainable_func()
    chain = mod.make_chain([cx, cy, cz])
    ret = chain(1)
    assert ret == z.return_value
    x.assert_called_once_with(1)
    y.assert_called_once_with(x.return_value)
    z.assert_called_once_with(y.return_value)


def test_bail_early_from_chain(chainable_func):
    """
    Given a set of chainable function of which one raises ReturnEarly
    exception, when a chain is created using make_chain() and called, then only
    the functions up to the raising function (inclusive) are called.
    """
    x, cx = chainable_func()
    y, cy = chainable_func()
    z, cz = chainable_func()
    y.side_effect = mod.ReturnEarly
    chain = mod.make_chain([cx, cy, cz])
    chain(1)
    assert x.called
    assert y.called
    assert not z.called


def test_bail_early_return_value(chainable_func):
    """
    Given a set of chainable function of which one raises ReturnEarly
    exception, when chain is created using make_chain() and called, then the
    return value of the call is the original value passed to the chain.
    """
    x, cx = chainable_func()
    y, cy = chainable_func()
    z, cz = chainable_func()
    y.side_effect = mod.ReturnEarly
    chain = mod.make_chain([cx, cy, cz])
    assert chain(1) == 1
