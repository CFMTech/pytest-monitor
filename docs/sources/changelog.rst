=========
Changelog
=========

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
