Py12fLogging
============

Python logging module for developing microservices conforming to 12 Factor App
methodology. Depends only on Python standard lib. However, setuptools may be
installed to provide additional functionality.


Installation
------------

Py12fLogging is available to install from PyPI::

   pip install py12flogging


Usage
-----

Py12fLogging is a module used for developing microservices. It is not a standalone
application. See module documentation for more information.

Example use of log_formatter -module::

   import logging
   from py12flogging import log_formatter
   log_formatter.setup_app_logging('my_app')
   logging.info('all done')


PrettyPrint logging output
^^^^^^^^^^^^^^^^^^^^^^^^^^

Developers may wish to restructure log output stream of an application while it's
under development. This can be achieved by using pprint command line application,
which prettyprints the log output stream coming from stdin and flushes immediately
to stdout. See module documentation for more information.

Pipe application's stdout to pprint-module::

   ./my_app.py | python -m py12flogging.pprint
