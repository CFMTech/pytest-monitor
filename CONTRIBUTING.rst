=============================
Contribution, getting started
=============================

Contributions are highly welcomed and appreciated.  Every little help counts,
so do not hesitate!

.. contents::
   :depth: 2
   :backlinks: none

Create your own development environment
---------------------------------------
We use conda as our main packaging system, though pip work as well. Nevertheless, 
the following instructions describe how to make your development environment using conda.

#. Create a new environment:

    conda create -n pytest-monitor-dev python=3 -c https://conda.anaconda.org/conda-forge -c defaults
    
#. Install the dependencies

    conda install --file requirements.txt -n pytest-monitor-dev -c https://conda.anaconda.org/conda-forge -c defaults
    
#. Activate your environment

    conda activate pytest-monitor-dev

#. Install pytest-monitor in development mode

    python setup.py develop

#. You're done!


.. _submitfeedback:

Feature request and feebacks
----------------------------
We'd like to hear about your propositions and suggestions. Feel free to
`submit them as issues <https://github.com/CFMTech/pytest-monitor/issues>`_ and:

* Explain in detail how they should work.
* Keep the scope as narrow as possible.  This will make it easier to implement.


.. _reportbugs:

Report bugs
-----------
Report bugs for pytest-monitor in the issue tracker. Every filed bugs should include:
 * Your operating system name and version.
 * Any details about your local setup that might be helpful in troubleshooting, specifically:
    * the Python interpreter version
    * installed libraries
    * and pytest version.
 * Detailed steps to reproduce the bug.

.. _fixbugs:

Fix bugs
--------

Look through the `GitHub issues for bugs <https://github.com/CFMTech/pytest-monitor>`_.

:ref:`Talk <contact>` to developers to find out how you can fix specific bugs.

Implement features
------------------

Look through the `GitHub issues for enhancements <https://github.com/CFMTech/pytest-monitor/labels/type:%20enhancement>`_.

:ref:`Talk <contact>` to developers to find out how you can implement specific
features.

.. _`pull requests`:
.. _pull-requests:

Preparing Pull Requests
-----------------------

Short version
~~~~~~~~~~~~~

#. Fork the repository.
#. Enable and install `pre-commit <https://pre-commit.com>`_ to ensure style-guides and code checks are followed.
#. Target ``master`` for bugfixes and doc changes.
#. Target ``features`` for new features or functionality changes.
#. Follow **PEP-8** for naming and `black <https://github.com/psf/black>`_ for formatting.
#. Tests are run using ``tox``::

    tox -e linting,py37

   The test environments above are usually enough to cover most cases locally.

#. Write a ``changelog`` entry: ``changelog/2574.bugfix.rst``, use issue id number
   and one of ``bugfix``, ``removal``, ``feature``, ``vendor``, ``doc`` or
   ``trivial`` for the issue type.
#. Unless your change is a trivial or a documentation fix (e.g., a typo or reword of a small section) please
   add yourself to the ``AUTHORS`` file, in alphabetical order.


Long version
~~~~~~~~~~~~

What is a "pull request"?  It informs the project's core developers about the
changes you want to review and merge.  Pull requests are stored on
`GitHub servers <https://github.com/CFMTech/pytest-monitor/pulls>`_.
Once you send a pull request, we can discuss its potential modifications and
even add more commits to it later on. There's an excellent tutorial on how Pull
Requests work in the
`GitHub Help Center <https://help.github.com/articles/using-pull-requests/>`_.

Here is a simple overview, with pytest-specific bits:

#. Fork the
   `pytest GitHub repository <https://github.com/CFMTech/pytest-monitor>`__.  It's
   fine to use ``pytest`` as your fork repository name because it will live
   under your user.

#. Clone your fork locally using `git <https://git-scm.com/>`_ and create a branch::

    $ git clone git@github.com:YOUR_GITHUB_USERNAME/pytest.git
    $ cd pytest
    # now, to fix a bug create your own branch off "master":

        $ git checkout -b fix/your-bugfix-branch-name master

    # or to instead add a feature create your own branch off "master":

        $ git checkout -b feature/your-feature-branch-name master

   Given we have "major.minor.micro" version numbers, bugfixes will usually
   be released in micro releases whereas features will be released in
   minor releases and incompatible changes in major releases.

   If you need some help with Git, follow this quick start
   guide: https://git.wiki.kernel.org/index.php/QuickStart

#. Install `pre-commit <https://pre-commit.com>`_ and its hook on the pytest repo:

   **Note: pre-commit must be installed as admin, as it will not function otherwise**::

     $ pip install --user pre-commit
     $ pre-commit install

   Afterwards ``pre-commit`` will run whenever you commit.

   https://pre-commit.com/ is a framework for managing and maintaining multi-language pre-commit hooks
   to ensure code-style and code formatting is consistent.

#. Install tox

   Tox is used to run all the tests and will automatically setup virtualenvs
   to run the tests in.
   (will implicitly use http://www.virtualenv.org/en/latest/)::

    $ pip install tox

#. Run all the tests

   You need to have Python 3.7 available in your system.  Now
   running tests is as simple as issuing this command::

    $ tox -e linting,py37

   This command will run tests via the "tox" tool against Python 3.7
   and also perform "lint" coding-style checks.

#. You can now edit your local working copy and run the tests again as necessary. Please follow PEP-8 for naming.

   You can pass different options to ``tox``. For example, to run tests on Python 3.7 and pass options to pytest
   (e.g. enter pdb on failure) to pytest you can do::

    $ tox -e py37 -- --pdb

   Or to only run tests in a particular test module on Python 3.7::

    $ tox -e py37 -- testing/test_config.py


   When committing, ``pre-commit`` will re-format the files if necessary.

#. If instead of using ``tox`` you prefer to run the tests directly, then we suggest to create a virtual environment and use
   an editable install with the ``testing`` extra::

       $ python3 -m venv .venv
       $ source .venv/bin/activate  # Linux
       $ .venv/Scripts/activate.bat  # Windows
       $ pip install -e ".[testing]"

   Afterwards, you can edit the files and run pytest normally::

       $ pytest testing/test_config.py


#. Commit and push once your tests pass and you are happy with your change(s)::

    $ git commit -a -m "<commit message>"
    $ git push -u

#. Create a new changelog entry in ``changelog``. The file should be named ``<issueid>.<type>.rst``,
   where *issueid* is the number of the issue related to the change and *type* is one of
   ``bugfix``, ``removal``, ``feature``, ``vendor``, ``doc`` or ``trivial``. You may not create a
   changelog entry if the change doesn't affect the documented behaviour of Pytest.

#. Add yourself to ``AUTHORS`` file if not there yet, in alphabetical order.

#. Finally, submit a pull request through the GitHub website using this data::

    head-fork: YOUR_GITHUB_USERNAME/pytest
    compare: your-branch-name

    base-fork: pytest-dev/pytest
    base: master          # if it's a bugfix
    base: features        # if it's a feature

