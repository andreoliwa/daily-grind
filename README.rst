========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |github-actions|
        | |codecov|
    * - package
      - | |commits-since|

.. |github-actions| image:: https://github.com/andreoliwa/daily-grind/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/andreoliwa/daily-grind/actions

.. |codecov| image:: https://codecov.io/gh/andreoliwa/daily-grind/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/andreoliwa/daily-grind

.. |commits-since| image:: https://img.shields.io/github/commits-since/andreoliwa/daily-grind/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/andreoliwa/daily-grind/compare/v0.0.0...master



.. end-badges

Easily open all the apps you use every day

* Free software: MIT license

Installation
============

::

    pip install daily-grind

You can also install the in-development version with::

    pip install https://github.com/andreoliwa/daily-grind/archive/master.zip


Documentation
=============


To use the project:

.. code-block:: python

    import daily_grind
    daily_grind.longest()


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
