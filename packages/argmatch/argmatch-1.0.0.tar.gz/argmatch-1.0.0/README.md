argmatch
======

This project is a fork of [callee](https://github.com/Xion/callee).

Argument matchers for *unittest.mock*

[![Version](https://img.shields.io/pypi/v/argmatch.svg?style=flat)](https://pypi.python.org/pypi/argmatch)
[![Development Status](https://img.shields.io/pypi/status/argmatch.svg?style=flat)](https://pypi.python.org/pypi/argmatch/)
[![Python Versions](https://img.shields.io/pypi/pyversions/argmatch.svg?style=flat)](https://pypi.python.org/pypi/argmatch)
[![License](https://img.shields.io/pypi/l/argmatch.svg?style=flat)](https://github.com/Xion/argmatch/blob/master/LICENSE)
[![Build Status](https://img.shields.io/travis/Xion/argmatch.svg?style=flat)](https://travis-ci.org/Xion/argmatch)

## More robust tests

Python's [mocking library](https://docs.python.org/3/library/unittest.mock.html) (or its [backport](https://pypi.python.org/pypi/mock) for Python <3.3) is simple, reliable, and easy to use.
But it is also a little lacking when it comes to asserting what calls a mock has received.

You can be either very specific::

    my_mock.assert_called_once_with(42, some_foo_object, 'certain string')

or extremely general::

    my_mock.assert_called_with(ANY, ANY, ANY)
    # passes as long as argument count is the same

| The former can make your tests over-specified, and thus fragile.
| The latter could make them too broad, missing some erroneous cases and possibly letting your code fail in production.

----

*argmatch* provides **argument matchers** that allow you to be exactly as precise as you want::

    my_mock.assert_called_with(GreaterThan(0), InstanceOf(Foo), String())

without tedious, handcrafted, and poorly readable code that checks ``call_args`` or ``call_args_list``::

    self.assertGreater(mock.call_args[0][0], 0)
    self.assertIsInstance(mock.call_args[0][1], Foo)
    self.assertIsInstance(mock.call_args[0][2], str)

It has plenty of matcher types to fit all common and uncommon needs, and you can easily write your own if necessary.


Installation
~~~~~~~~~~~~

Installing *argmatch* is easy with pip::

    $ pip install argmatch

| *argmatch* support goes all the way back to Python 2.6.
| It also works both with the ``unittest.mock`` module from Python 3.3+ or its backport.


API reference
~~~~~~~~~~~~~

See the `documentation`_ for complete reference on the library usage and all available matchers.

.. _documentation: http://argmatch.readthedocs.org


Contributing
~~~~~~~~~~~~

Contributions are welcome!
If you need ideas, head to the issue tracker or search for the various ``TODO``\ s scattered around the codebase.
Or just think what matchers you'd like to add :)

After cloning the repository, this should get you up and running::

    # ... create virtualenv as necessary ...
    pip install -r requirements-dev.txt
    tox

To regenerate documentation and display it in the browser, simply run::

    inv docs

Happy hacking!
