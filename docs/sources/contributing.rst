==================
Contribution guide
==================

If you want to contribute to this project, you are welcome to do so!

Create your own development environment
---------------------------------------
We use conda as our main packaging system, though pip works as well.

The following instructions describe how to create your development environment using conda:

#. Create a new environment:

    .. code-block:: bash

       conda create -n pytest-monitor-dev python=3 -c https://conda.anaconda.org/conda-forge -c defaults
        
#. Install the dependencies:

    .. code-block:: bash

       conda install --file requirements.dev.txt -n pytest-monitor-dev -c https://conda.anaconda.org/conda-forge -c defaults
        
#. Make sure to have pip install or install it if missing:

    .. code-block:: bash

        # Check for pip
        conda list | grep pip
        # Install if needed
        conda install -n pytest-monitor-dev pip -c https://conda.anaconda.org/conda-forge

#. Activate your environment:

    .. code-block:: bash

        conda activate pytest-monitor-dev

#. Install `pytest-monitor` in development mode:

    .. code-block:: bash

       python -m pip install -e ".[dev]"

#. Install the pre-commit hooks
    .. code-block:: bash

       pre-commit install

#. You're done!

Feature requests and feedback
-----------------------------

We would be happy to hear about your propositions and suggestions. Feel free to
`submit them as issues <https://github.com/CFMTech/pytest-monitor/issues>`_ and:

* Explain in details the expected behavior.
* Keep the scope as narrow as possible.  This will make them easier to implement.


.. _reportbugs:

Bug reporting
-------------

Report bugs for `pytest-monitor` in the `issue tracker <https://github.com/CFMTech/pytest-monitor/issues>`_. Every filed bugs should include:

 * Your operating system name and version.
 * Any details about your local setup that might be helpful in troubleshooting, specifically:
     * the Python interpreter version,
     * installed libraries,
     * and your `pytest` version.
 * Detailed steps to reproduce the bug.

.. _fixbugs:

Bug fixing
----------

Look through the `GitHub issues for bugs <https://github.com/CFMTech/pytest-monitor/issues>`_.
Talk to developers to find out how you can fix specific bugs.

Feature implementation
----------------------

Look through the `GitHub issues for enhancements <https://github.com/CFMTech/pytest-monitor/labels/type:%20enhancement>`_.

Talk to developers to find out how you can implement specific features.

Thank you!
