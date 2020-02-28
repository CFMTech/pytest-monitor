.. image:: docs/sources/_static/pytestmonitor_readme.png
   :width: 160
   :align: center
   :alt: Pytest-Monitor

------

==============
pytest-monitor
==============

.. image:: https://readthedocs.org/projects/pytest-monitor/badge/?version=latest
    :target: https://pytest-monitor.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/pytest-monitor.svg
    :target: https://pypi.org/project/pytest-monitor
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-monitor.svg
    :target: https://circleci.com/gh/jsd-spif/pymonitor.svg?style=svg&circle-token=cdf89a7212139aff0cc236227cb519363981de0b
    :alt: Python versions

.. image:: https://circleci.com/gh/CFMTech/pytest-monitor/tree/master.svg?style=shield&circle-token=054adaaf6a19f4f55a4f0ad419649f1807e70ea9
    :target: https://circleci.com/gh/CFMTech/pytest-monitor/tree/master
    :alt: See Build Status on Circle CI

.. image:: https://anaconda.org/conda-forge/pytest-monitor/badges/platforms.svg
    :target: https://anaconda.org/conda-forge/pytest-monitor

.. image:: https://anaconda.org/conda-forge/pytest-monitor/badges/version.svg
    :target: https://anaconda.org/conda-forge/pytest-monitor

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT
    

Pytest-monitor is a pytest plugin designed for analyzing resource usage.

----


Features
--------

- Analyze your resources consumption through test functions:

  * memory consumption
  * time duration
  * CPU usage
- Keep a history of your resource consumption measurements.
- Compare how your code behaves between different environments.


Usage
-----

Simply run *pytest* as usual: *pytest-monitor* is active by default as soon as it is installed.
After running your first session, a .pymon `sqlite` database will be accessible in the directory where pytest was run.

Example of information collected for the execution context:

+-----------------------------------+-----------+-------------------+---------+-------------------------------------------+---------------+--------------------+------------+-------------------------------+-------------------------------+--------------------------------------------------+
|                              ENV_H|  CPU_COUNT|  CPU_FREQUENCY_MHZ| CPU_TYPE|                                 CPU_VENDOR|  RAM_TOTAL_MB |       MACHINE_NODE |MACHINE_TYPE| MACHINE_ARCH                  |  SYSTEM_INFO                  |                                       PYTHON_INFO|
+===================================+===========+===================+=========+===========================================+===============+====================+============+===============================+===============================+==================================================+                   
|  8294b1326007d9f4c8a1680f9590c23d |        36 |              3000 |  x86_64 | Intel(R) Xeon(R) Gold 6154 CPU @ 3.00GHz  |      772249   | some.host.vm.fr    |     x86_64 |       64bit                   | Linux - 3.10.0-693.el7.x86_64 | 3.6.8 (default, Jun 28 2019, 11:09:04) \n[GCC ...|
+-----------------------------------+-----------+-------------------+---------+-------------------------------------------+---------------+--------------------+------------+-------------------------------+-------------------------------+--------------------------------------------------+

Here is an example of collected data stored in the result database:

+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|                      RUN_DATE|                             ENV_H|                                    SCM_ID|             ITEM_START_TIME|                                    ITEM|      KIND| COMPONENT|  TOTAL_TIME|  USER_TIME|  KERNEL_TIME|   CPU_USAGE|  MEM_USAGE|
+==============================+==================================+==========================================+============================+========================================+==========+==========+============+===========+=============+============+===========+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:36.890477 |             pkg1.test_mod1/test_sleep1 | function |     None |   1.005669 |      0.54 |       0.06  |  0.596618  | 1.781250  |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:39.912029 |       pkg1.test_mod1/test_heavy[10-10] | function |     None |   0.029627 |      0.55 |        0.08 |  21.264498 |  1.781250 |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:39.948922 |     pkg1.test_mod1/test_heavy[100-100] | function |     None |   0.028262 |      0.56 |        0.09 |  22.998773 |  1.781250 |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:39.983869 |   pkg1.test_mod1/test_heavy[1000-1000] | function |     None |   0.030131 |      0.56 |        0.10 |  21.904277 |  2.132812 |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:40.020823 | pkg1.test_mod1/test_heavy[10000-10000] | function |     None |   0.060060 |      0.57 |        0.14 |  11.821601 | 41.292969 |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:40.093490 |        pkg1.test_mod2/test_sleep_400ms | function |     None |   0.404860 |      0.58 |        0.15 |   1.803093 |  2.320312 |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:40.510525 |      pkg2.test_mod_a/test_master_sleep | function |     None |   5.006039 |      5.57 |        0.15 |   1.142620 |  2.320312 |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:45.530780 |          pkg3.test_mod_cl/test_method1 | function |     None |   0.030505 |      5.58 |        0.16 | 188.164762 |  2.320312 |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+
|   2020-02-17T09:11:36.731233 | 8294b1326007d9f4c8a1680f9590c23d | de23e6bdb987ae21e84e6c7c0357488ee66f2639 | 2020-02-17T09:11:50.582954 |     pkg4.test_mod_a/test_force_monitor | function |     test |   1.005015 |     11.57 |       0.17  | 11.681416  | 2.320312  |
+------------------------------+----------------------------------+------------------------------------------+----------------------------+----------------------------------------+----------+----------+------------+-----------+-------------+------------+-----------+

Documentation
-------------

A full documentation is `available <https://pytest-monitor.readthedocs.io/en/latest/?badge=latest>`_.

Installation
------------

You can install *pytest-monitor* via *conda* (through the `conda-forge` channel)::

    $ conda install pytest-monitor -c https://conda.anaconda.org/conda-forge

Another possibility is to install *pytest-monitor* via `pip`_ from `PyPI`_::

    $ pip install pytest-monitor


Requirements
------------

You will need a valid Python 3.5+ interpreter. To get measures, we rely on:

- *psutil* to extract CPU usage
- *memory_profiler* to collect memory usage
- and *pytest* (obviously!)

Contributing
------------

Contributions are very welcome. Tests can be run with `tox`_. Before submitting a pull request, please ensure
that:

* both internal tests and examples are passing.
* internal tests have been written if necessary.
* if your contribution provides a new feature, make sure to provide an example and update the documentation accordingly.

License
-------

This code is distributed under the `MIT`_ license.  *pytest-monitor* is free, open-source software.


Issues
------

If you encounter any problem, please `file an issue`_ along with a detailed description.

Author
------

The main author of `pytest-monitor` is Jean-Sébastien Dieu, who can be reached at jean-sebastien.dieu@cfm.fr.

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/CFMTech/pytest-monitor/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
