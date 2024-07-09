Use of a remote server
======================

You can easily send your metrics to a remote server. This can turn usefull when it comes to running
tests in parallel with plugins such as *pytest-xdist* of *pytest-parallel*.
To do so, instruct pytest with the remote server address to use:

.. code-block:: shell

   bash $> pytest --remote-server myremote.server.net:port 

This way, *pytest-monitor* will automatically send and query the remote server as soon as it gets
a need.  Note that *pytest-monitor* will revert to a normal behaviour if:

- it cannot query the context or the session for existence
- it cannot create a new context or a new session


Implementing a remote server
============================

How pytest-monitor interacts with a remote server
-------------------------------------------------

The following sequence is used by *pytest-monitor* when using a remote server:

1. Ask the remote server if the **Execution Context** is known.
2. Insert the **Execution Context** if the server knows nothing about it.
3. Ask the remote server if the **Session** is known.
4. Insert the **Session** if the server knows nothing about it.
5. Insert results once measures have been collected.

Used HTTP codes
---------------
Two codes are used by *pytest-monitor* when asked to work with a remote server:

- 200 (OK) is used to indicate that a query has led to a non-empty result.
- 201 (CREATED) is expected by *pytest-monitor** when sending a new entry (**Execution Context**, **Session** or any **Metric**).
- 204 (NO CONTENT) though not checked explicitely should be returned when a request leads to no results.

Mandatory routes
----------------
The following routes are expected to be reachable:

GET /contexts/<str:hash>

    Query the system for a **Execution Context** with the given hash.

    **Return Codes**: Must return *200* (*OK*) if the **Execution Context** exists, *204* (*NO CONTENT*) otherwise

GET /sessions/<str:hash>

    Query the system for a **Session** with the given hash.
    
    **Return Codes**: Must return *200* (*OK*) if the **Session** exists, *204* (*NO CONTENT*) otherwise

POST /contexts/

    Request the system to create a new entry for the given **Execution Context**.
    Data are sent using Json parameters:

    .. code-block:: json

        {
            cpu_count: int, 
            cpu_frequency: int, 
            cpu_type: str, 
            cpu_vendor: str, 
            ram_tota: int,
            machine_node: str, 
            machine_type: str, 
            machine_arch: str, 
            system_info: str, 
            python_info: str, 
            h: str
        }

    **Return Codes**: Must return *201* (*CREATED*) if the **Execution Context** has been created


POST /sessions/

    Request the system to create a new entry for the given **Session**.
    Data are sent using Json parameters:

    .. code-block:: json
       
       {
           session_h: str,
           run_date: str,
           scm_ref: str,
           description: str
       }

    **Return Codes**: Must return *201* (*CREATED*) if the **Session** has been created

POST /metrics/

    Request the system to create a new **Metrics** entry. 
    Data are sent using Json parameters:

    .. code-block:: json

        {
            session_h: str, 
            context_h: str, 
            item_start_time: str,
            item_path: str,
            item: str,
            item_variant: str,
            item_fs_loc: str,
            kind: str, 
            component: str,
            total_time: float,
            user_time: float,
            kernel_time: float,
            cpu_usage: float,
            mem_usage: float,
            passed: bool,
        }

    **Return Codes**: Must return *201* (*CREATED*) if the **Metrics** has been created
