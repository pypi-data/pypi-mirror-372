Py12fLogging Changelog
======================


0.8.0 (2025-08-29)
------------------

* Add test environment for Python 3.13. and run it in CI.
* Remove test environment for Python 3.8.
* Fix DeprecationWarning in testcase in Python 3.12.
* Make sure to catch warnings in ci with tox env warnings-as-errors.


0.7.0 (2024-08-22)
------------------

* Migrate from setuptools to importlib.metadata when reading
  application version.
* Add test environment for Python 3.12. and run it in CI.


0.6.0 (2024-04-26)
------------------

* Use 'python-latest' in Jenkinsfile instead of 'python3'. In FSD
  Jenkins environment the python-latest always points to latest
  installed Python.
* Add py39, py310, py311 to tox test environments and use it in Jenkinsfile.
* Drop py35, py36, py37 from tox test environments and Jenkinsfile.
* Change project url from bitbucket to gitlab.tuni.


0.5.0 (2021-01-20)
------------------

* Maintenance release fixes setup.py long_description_content_type to
  make it compatible with PyPI. PyPI expects content type value
  'text/x-rst' for reStructuredText.
* Remove the step to obtain package from README.rst since pip can
  download the package automatically from PyPI.
* Update license headers to 2021.


0.4.0 (2020-09-17)
------------------

* Maintenance release with no code changes.
* Add Jenkinsfile.
* Add VERSION.
* Add sonar-project.properties.
* Add LICENSE.txt
* Add .gitignore
* Add MANIFEST.in.
* Add license headers to python code files.
* setup.py reads correct version from VERSION.
* Add more metadata to setup.py.
* Fix typo in README.rst
* Add py38 environment to tox.ini.


0.3.0 (2019-09-03)
------------------

* Add :mod:`py12flogging.pprint` command line application, which reformats log
  output stream by adding indentation and newlines to JSON objects.
* Implement a parameter for :func:`py12flogging.log_formatter.setup_app_logging()`
  and :func:`py12flogging.log_formatter.config_dict()` to setup logging
  formatter's format: ``logformat``.
* Change default logformat from '%(asctime)s %(levelname)s(%(name)s): %(message)s'
  to '%(message)s'. Only the JSON object gets logged by default.
* Change default loglevel to ``WARNING`` to conform python stdlib logging-module
  default.
* :func:`py12flogging.log_formatter.set_app_config()` now raises TypeError if
  called with unknown keyword arguments.


0.2.0 (2019-07-09)
------------------

* Implement a :func:`py12flogging.log_formatter._default_ctx_populator()`
  which clears ctx after each logevent.
* Implement an interface :func:`py12flogging.log_formatter.push_to_ctx()`
  to use the default context populator.


0.1.0 (2019-07-08)
------------------

* Initial release: log_formatting module to bootstrap application wide
  logging in non-disruptive way to conform to 12 factor app methodology.
* Support logging as structured JSON.
* Support arbitrary key-value pairs in logrecord.
