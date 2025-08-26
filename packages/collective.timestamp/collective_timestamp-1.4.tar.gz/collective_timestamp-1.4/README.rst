.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/collective.timestamp/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/collective.timestamp/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/collective.timestamp/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/collective.timestamp?branch=main
    :alt: Coveralls

.. image:: https://img.shields.io/pypi/v/collective.timestamp.svg
    :target: https://pypi.python.org/pypi/collective.timestamp/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/collective.timestamp.svg
    :target: https://pypi.python.org/pypi/collective.timestamp
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/collective.timestamp.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/collective.timestamp.svg
    :target: https://pypi.python.org/pypi/collective.timestamp/
    :alt: License


====================
collective.timestamp
====================

Timestamp Files (or any other content types with a file primary field) in Plone.
The `collective.timestamp` behavior must be activated on content types you want to timestamp.


Features
--------

- Allows you to timestamp a file via a toolbar action.
- Provides a way to timestamp files through a content rule action executor.
- Displays a timestamped viewlet on timestamped content.
- The viewlet provides access to a verification view (with files and instructions).
- Timestamping service and verification instructions are configurable via a configlet.


Translations
------------

This product has been translated into

- French


Installation
------------

Install collective.timestamp by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.timestamp


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.timestamp/issues
- Source Code: https://github.com/collective/collective.timestamp


Support
-------

If you are having issues, please let us know.


License
-------

The project is licensed under the GPLv2.
