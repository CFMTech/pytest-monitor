=========
Changelog
=========
* :release:`to be discussed`
* :bug: `#79` Fix a bug concerning commandline flag `--no-monitor` causing tests that are supposed to fail to pass instead
* :feature:`#75` Automatically gather CI build information for Bitbucket CI.
* :release:`1.6.6 <2023-05-06>`
* :bug:`#64` Prepare version 1.7.0 of pytest-monitor. Last version to support Python <= 3.7 and all pytest <= 5.*
* :bug:`#0` Improve and fix some CI issues, notably one that may cause python to not be the requested one but a more recent one.

* :release:`1.6.5 <2022-10-16>`
* :bug:`#60` Make sure that when psutil cannot fetch cpu frequency, the fallback mechanism is used.

* :release:`1.6.4 <2022-05-18>`
* :bug:`#56` Force the CPU frequency to 0 and emit a warning when unable to fetch it from the system.
* :bug:`#54` Fix a bug that crashes the monitor upon non ASCII characters in commit log under Perforce. Improved P4 change number extraction.

* :release:`1.6.3 <2021-12-22>`
* :bug:`#50` Fix a bug where a skipping fixture resulted in an exception during teardown.

* :release:`1.6.2 <2021-08-24>`
* :bug:`#40` Fix a bug that cause the garbage collector to be disable by default.

* :release:`1.6.1 <2021-08-23>`
* :bug:`#43` Fixes a bug that prevent sending session tags correctly.
* :bug:`#40` Force garbage collector to run between tests (better result accuracy)

* :release:`1.6.0 <2021-04-16>`
* :feature:`#0` Support for python 3.5
* :feature:`#35` Better support for Doctest item.
* :feature:`#24` Prefer JSON data type for storing session extended information instead of plain text.


* :release:`1.5.1 <2021-02-05>`
* :bug:`#31` Rename option --remote into --remote-server as it seems to conflict with some plugins.  
* :bug:`#23` Fix requirements minimum version.

* :release:`1.5.0 <2020-11-20>`
* :feature:`25` Automatically gather CI build information (supported CI are Drone CI, Gitlab CI, Jenkins CI, Travis CI, Circle CI)
* :bug:`#23 major` psutil min requirement is now 5.1.0
* :bug:`#28 major` Fix a bug that cause output to be printed multiple times

* :release:`1.4.0 <2020-06-04>`
* :feature:`21` Using json format to populate the RUN_DESCRIPTION field (through --description and --tag fields)

* :release:`1.3.0 <2020-05-12>`
* :feature:`19` Normalized http codes used for sending metrics to a remote server.

* :release:`1.2.0 <2020-04-17>`
* :feature:`13` Change default analysis scope to function.
* :bug:`12 major` No execution contexts pushed when using a remote server.
* :bug:`14 major` A local database is always created even with --no-db option passed.

* :release:`1.1.1 <2020-03-31>`
* :bug:`9` Fix remote server interface for sending measures.

* :release:`1.1.0 <2020-03-30>`
* :feature:`5` Extend item information and separate item from its variants.
* :feature:`3` Compute user time and kernel time on a per test basis for clarity and ease of exploitation.
* :feature:`4` Added an option to add a description to a pytest run

* :release:`1.0.1 <2020-03-18>`
* :bug:`2` pytest-monitor hangs infinitely when a pytest outcome (skip, fail...) is issued.

* :release:`1.0.0 <2020-02-20>`
* :feature:`0` Initial release
