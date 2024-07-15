============
Introduction
============

`pytest-monitor` tracks the resources (like memory and compute time) consumed by a test suite, so that you
can make sure that your code does not use too much of them.

Thanks to `pytest-monitor`, you can check resource consumption in particular through continuous integration, as this is done by monitoring the consumption of test functions. These tests can be functional (as usual) or be dedicated to the resource consumption checks.

Use cases
---------

Examples of use cases include technical stack updates, and code evolutions.

Technical stack updates
~~~~~~~~~~~~~~~~~~~~~~~

In the Python world, libraries often depends on several packages. By updating some (or all) of the dependencies,
you update code that you do not own and therefore do not control. Tracking your application's resource footprint
can prevent unwanted resource consumption, and can thus validate the versions of the packages that you depend on.

Code evolution
~~~~~~~~~~~~~~

Extending your application with new features, or fixing its bugs, might have an impact on the core of your program. The performance of large applications or libraries can be difficult to assess, but by monitoring resource consumption, `pytest-monitor` allows you to check that despite code udpates, the performance of your code remains within desirable limits.


Usage
-----

Simply run pytest as usual: pytest-monitor is active by default as soon as it is installed. After running your first session, a .pymon sqlite database (or optionally another database implementation like PostgreSQL) will be accessible in the directory where pytest was run.
