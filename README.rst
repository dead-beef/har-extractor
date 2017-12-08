har-extractor
=============

.. image:: https://img.shields.io/pypi/v/har-extractor.svg
   :target: https://pypi.python.org/pypi/har-extractor
.. image:: https://img.shields.io/pypi/status/har-extractor.svg
   :target: https://pypi.python.org/pypi/har-extractor
.. image:: https://img.shields.io/pypi/format/har-extractor.svg
   :target: https://pypi.python.org/pypi/har-extractor
.. image:: https://img.shields.io/librariesio/github/dead-beef/har-extractor.svg
   :target: https://libraries.io/pypi/har-extractor
.. image:: https://img.shields.io/pypi/pyversions/har-extractor.svg
   :target: https://python.org
.. image:: https://img.shields.io/pypi/l/har-extractor.svg
   :target: https://github.com/dead-beef/har-extractor/blob/master/LICENSE

Overview
--------

Extractor for
`HAR <https://dvcs.w3.org/hg/webperf/raw-file/tip/specs/HAR/Overview.html>`__,
HTTP Archive format.

Requirements
------------

-  `Python 3 <https://www.python.org/>`__

Optional
~~~~~~~~

-  `YAJL 2 <https://lloyd.github.io/yajl/>`__
-  `CFFI <https://pypi.python.org/pypi/cffi>`__

Installation
------------

.. code:: bash

    pip install har-extractor

Usage
-----

::

    usage: har_extractor.py [-h] [-V] [-l] [-o DIRECTORY] [-v] [-nv] [-i] [-ni]
                            [-s] [-ns] [-d] [-nd]
                            FILE

    positional arguments:
      FILE                  HAR file

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -l, --list            list the contents of input file
      -o DIRECTORY, --output DIRECTORY
                            set output directory (default: ./<filename>.d)
      -v, --verbose         turn on verbose output (default)
      -nv, --no-verbose     turn off verbose output
      -i, --iterative       use iterative json parser
      -ni, --no-iterative   do not use iterative json parser (default)
      -s, --strict          exit and delete extracted data after first error
      -ns, --no-strict      ignore errors (default)
      -d, --directories     create url directories (default)
      -nd, --no-directories
                            do not create url directories

Development
-----------

Installation
~~~~~~~~~~~~

.. code:: bash

    git clone https://github.com/dead-beef/har-extractor
    cd har-extractor
    pip install -e .[dev]

Building
~~~~~~~~

.. code:: bash

    ./build.sh

Testing
~~~~~~~

.. code:: bash

    ./test

Licenses
--------

-  `har-extractor <https://github.com/dead-beef/har-extractor/blob/master/LICENSE>`__

