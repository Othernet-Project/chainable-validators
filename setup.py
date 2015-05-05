#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

SCRIPTDIR = os.path.dirname(__file__) or '.'
PY3 = sys.version_info >= (3, 0, 0)


def read(fname):
    """ Return content of specified file """
    path = os.path.join(SCRIPTDIR, fname)
    if PY3:
        f = open(path, 'r', encoding='utf8')
    else:
        f = open(path, 'r')
    content = f.read()
    f.close()
    return content


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments for py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='chainable-validators',
    version='0.4.post1',
    author='Outernet Inc',
    author_email='apps@outernet.is',
    description=('Python data validation framework that uses chainable '
                 'validator'),
    license='GPLv3',
    keywords='validation, framework, method chaining',
    url='https://github.com/Outernet-Project/chainable-validators',
    packages=find_packages(),
    long_description=read('README.rst'),
    classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Topic :: Utilities',
    ],
    cmdclass={
        'test': PyTest,
    },
)
