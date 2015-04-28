import pytest
import mock

from validators.chainable import chainable


@pytest.fixture
def func():
    """
    Mock function factory that returns well-behaved named functions.
    """
    def factory(funcname='func', **kwargs):
        m = mock.Mock(**kwargs)
        m.__name__ = funcname
        return m
    return factory


@pytest.fixture
def chainable_func(func):
    """
    Mock function and its chainable counterpart
    """
    def factory():
        x = func()
        cx = chainable(x)
        return x, cx
    return factory
