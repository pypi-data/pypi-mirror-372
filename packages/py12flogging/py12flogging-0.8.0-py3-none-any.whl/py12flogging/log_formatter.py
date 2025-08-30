# Author(s): Toni Sissala
# Copyright 2025 Finnish Social Science Data Archive FSD / University of Tampere
# Licensed under the EUPL. See LICENSE.txt for full license.
"""Logformatter for microservices.

Use to setup application wide logging of structured JSON
conforming to 12 factor app methodology.

Setup JSON logging for application::

    from py12flogging.log_formatter import setup_app_logging
    setup_app_logging('my_app')

Use arbitrary key-value pairs in logrecord. The key-value pairs
are cleared after push to the logrecord; the context won't persist
between logevents::

    from py12flogging.log_formatter import push_to_ctx
    push_to_ctx('my_key', 'my_value')

Register custom ctx populator to gain more control over the context::

    from py12flogging.log_formatter import set_ctx_populator
    def populate_log_context(push):
        push('arbitrary_key', 'value')
    set_ctx_populator(populate_log_context)

:note: push_to_ctx() cannot be used with a custom ctx populator, since
       push_to_ctx() registers its own ctx_populator.

:note: ctx_populator is global, changing it affects logmessages
       application wide. Applications should not change it after
       the initial setup.

After the setup, use logging module normally::

    import logging
    logger = logging.getLogger(__name__)
    logger.info('Start app')
    try:
        run_app()
    except:
        logger.exception('App failed')
"""
import time
import json
import warnings
import traceback
import socket
from uuid import uuid4
from logging import (
    Formatter,
    LogRecord,
    setLogRecordFactory,
    getLogRecordFactory
)
from logging.config import dictConfig
from importlib.metadata import metadata, PackageNotFoundError


#: Declare logmessage keys which are used to store and output
#: application configuration.
#: Applications must not change these after application config
#: has been stored (:func:`set_app_config()` has been called).
LM_KEY_APPNAME = 'app_name'
LM_KEY_APPVERS = 'app_version'
LM_KEY_APPID = 'app_id'
LM_KEY_HOSTIP = 'host_ip'
LM_KEY_PORT = 'port'
LM_KEY_TIMESTAMP = 'timestamp'
LM_KEY_EXCEPTION = 'exception'
LM_KEY_SEVERITY = 'severity'
LM_KEY_NAME = 'name'
LM_KEY_FUNC = 'func'
LM_KEY_LINE = 'line'
LM_KEY_PROCID = 'procid'
LM_KEY_MESSAGE = 'message'

DEFAULT_LOGLEVEL = 'WARNING'
DEFAULT_LOGFORMAT = '%(message)s'

_REGISTER = {
    'ctx_populator': None,  # Callable populates arbitrary keys to logrecord dict.
    'app_config': {},  # Application runtime configs persist for each logrecord.
    'orig_log_record_factory': getLogRecordFactory()  # Store original factory.
}

_DEFAULT_CTX = []


class LogConfigException(Exception):
    """Raised on invalid configuration"""


def _push_to_dict(_dict, *reserved_keys):
    def _push(key, value, overwrite=False):
        if key in reserved_keys:
            warnings.warn("Key %s is reserved in dict. Suffixing with underscores." % (key,))
            while key in reserved_keys:
                key += '_'
        if overwrite is False and key in _dict:
            warnings.warn("Key %s exists in dict. Suffixing with underscores." % (key,))
            while key in _dict:
                key += '_'
        _dict[key] = value
    return _push


def _host_ip():
    """Trying to get host ip without an internet connection.
    Will possibly return 127.0.1.1 if one is declared in /etc/hosts"""
    candidate = socket.gethostbyname(socket.gethostname())
    if candidate == '127.0.1.1':
        candidate = socket.gethostbyname(socket.getfqdn())
    return candidate


def set_app_config(app_name, **kwargs):
    r"""Set global application configs that are logged out in logmessages.

    If applications wish to use arbitrary keys for logmessage output,
    set constants prefixed ``LM_KEY_`` before calling :func:`set_app_config()`

    Optional keyword arguments and [defaults]:

       * app_version [read using importlib.metadata, fallback is None]
       * app_id [str(uuid.uuid4()]
       * host_ip [read using socket module]
       * port [no default. gets ignored completely if not set]

    :param str app_name: Application name.
    :param \*\*kwargs: Optional keyword arguments
    :returns: None
    :raises LogConfigException: If configuration has already been setup.
    """
    if _REGISTER['app_config'] != {}:
        raise LogConfigException("Application logging info already setup")
    app_version = None
    try:
        app_version = metadata(app_name).get("version")
    except PackageNotFoundError:
        warnings.warn(f"Package not found: '{app_name}'")
    _REGISTER['app_config'][LM_KEY_APPNAME] = app_name
    _REGISTER['app_config'][LM_KEY_APPVERS] = kwargs.pop('app_version', app_version)
    _REGISTER['app_config'][LM_KEY_APPID] = kwargs.pop('app_id', str(uuid4()))
    _REGISTER['app_config'][LM_KEY_HOSTIP] = kwargs.pop('host_ip', _host_ip())
    if 'port' in kwargs:  # app may not be a server application, thus no port.
        _REGISTER['app_config'][LM_KEY_PORT] = kwargs.pop('port')
    if kwargs != {}:
        raise TypeError("Invalid keyword arguments: %s" % (', '.join(kwargs),))


def set_ctx_populator(populator):
    """Set callable to populate certain logrecord dict with context of logevent.

    Callable receives a function which accepts two parameters (key, value, overwrite=False) and
    handles pushing key-value pairs to logrecord dict non-desctructively.

    :param callable populator: Context populator.
    :returns: None
    """
    if _REGISTER['ctx_populator'] is not None:
        raise LogConfigException('Cannot overwrite global context populator')
    _REGISTER['ctx_populator'] = populator


def _default_ctx_populator(push):
    """Default context populator clears context after pushing
    to logrecords. Every context exists only for a single logevent.

    :param callable push: push function to call.
    :returns: None
    """
    for key, value, overwrite in _DEFAULT_CTX:
        push(key, value, overwrite)
    _DEFAULT_CTX.clear()


def push_to_ctx(key, value, overwrite=False):
    """Push to context using default context populator.

    Default context populator clears context after each
    push to logrecord.

    :param str key: context key
    :param str value: context value corresponding key
    :param bool overwrite: True to overwrite already populated
                           context with given key. Defaults to
                           False.
    :returns: None
    """
    if _REGISTER['ctx_populator'] is not _default_ctx_populator:
        set_ctx_populator(_default_ctx_populator)
    _DEFAULT_CTX.append((key, value, overwrite))


def config_dict(loglevel, logformat, disable_existing_loggers):
    """Returns dictionary which can be passed to :func:`logging.config.dictConfig()`

    If applications need additional configurations the dictionary can
    be modified before passing it to dictConfig(), in which case
    :func:`setup_app_logging` should be called with configure_logging=False.

    :param str loglevel: Lowest loglevel.
    :param str logformat: Format of a logmessage.
    :param bool disable_existing_loggers: True to disable existing loggers.
    :returns: Logging configuration dictionary
    :rtype: dict
    """
    fmt_qual_name = '.'.join([LogFormatter.__module__, LogFormatter.__qualname__])
    return {
        'version': 1,
        'disable_existing_loggers': disable_existing_loggers,
        'root': {
            'level': loglevel,
            'handlers': ['root_handler']},
        'handlers': {
            'root_handler': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'service_formatter'}},
        'formatters': {
            'service_formatter': {
                'class': fmt_qual_name,
                'format': logformat,
                'datefmt': '%Y-%m-%dT%H:%M:%SZ'
            }}}


def setup_app_logging(app_name,
                      loglevel=DEFAULT_LOGLEVEL,
                      logformat=DEFAULT_LOGFORMAT,
                      disable_existing_loggers=False,
                      configure_logging=True,
                      **kwargs):
    r"""Setup application wide logging with structured JSON and application configuration.

    Registers application configs on global context. Sets JSONLogRecord as logrecordfactory.
    Configures logging by calling :func:`logging.config.dictConfig()`

    Only mandatory argument is ``app_name``. Additional application configuration is
    constructed by passing \*\*kwargs to :func:`set_app_config`, which registers them
    in a global container that gets read with by each logevent.

    Configures logging by setting ``loglevel`` and ``disable_existing_loggers`` if
    ``configure_logging`` is True (default). When ``configure_logging`` is False, bypasses
    the logging configuration and ``loglevel`` and ``disable_existing_loggers`` are ignored.

    :param str app_name: application name.
    :param str loglevel: Lowest loglevel to output.
    :param str logformat: Format of a logmessage.
    :param bool disable_existing_loggers: True disables existing loggers.
    :param bool configure_logging: False bypasses call to :func:`logging.config.dictConfig`
                                   and ignores ``loglevel`` and ``disable_existing_loggers``.
    :param \*\*kwargs: Additional keyword arguments are passed to :func:`set_app_config`
    :returns: None
    """
    set_app_config(app_name, **kwargs)

    def record_factory(*args, **kwargs):
        return JSONLogRecord(*args, **kwargs)
    setLogRecordFactory(record_factory)
    if configure_logging:
        # dictConfig does not validate the value of disable_existing_loggers
        dictConfig(config_dict(loglevel, logformat, disable_existing_loggers))


def format_exception(exc_type, exc, tb):
    """Format exception info to be used in structured logmessages.

    Parameters correspond to an unpacked tuple retrieved from
    :func:`sys.exc_info()`.

    :param exc_type: Exception class
    :param exc: Exception class instance
    :param tb: Traceback object
    :returns: Structured exception info
    :rtype: dict
    """
    traceback_lines = []
    lines = traceback.extract_tb(tb)
    for line in lines:
        traceback_lines.append({
            'file': line[0],
            'lineno': line[1],
            'function': line[2],
            'text': line[3]
        })
    return {'type': str(exc_type),
            'message': str(exc),
            'traceback': traceback_lines}


class LogFormatter(Formatter):
    """Customized formatter to be used with backend services.

    Handle timestamp formatting for log output.
    """

    #: Timestamps as UTC
    converter = time.gmtime

    def format(self, record):
        """Format logrecord by pushing timestamp for JSONLogRecord instances.

        May also be used to simply output timestamps as UTC, without a
        structured log record.

        :param :obj:`logging.LogRecord` record: LogRecord to format.
        :returns: Log event output
        :rtype: str
        """
        if hasattr(record, 'push'):
            record.push(LM_KEY_TIMESTAMP, self.formatTime(record, self.datefmt), overwrite=True)
        return super().format(record)


class JSONLogRecord(LogRecord):
    """LogRecord for structured logging output.

    Introduces a public interface :func:`push`, which should
    be used to push key-value pairs to logging output structure.
    """
    def __init__(self, *args, **kwargs):
        self._log_dict = dict(_REGISTER['app_config'])
        self.push = _push_to_dict(self._log_dict,
                                  LM_KEY_EXCEPTION,
                                  LM_KEY_SEVERITY,
                                  LM_KEY_NAME,
                                  LM_KEY_FUNC,
                                  LM_KEY_LINE,
                                  LM_KEY_PROCID,
                                  LM_KEY_MESSAGE)
        super().__init__(*args, **kwargs)

    def getMessage(self):
        """Construct and return logmessage.

        Populates structured logmessage by calling ``ctx_populator``
        if one is declared, formatting exception if one is provided,
        and inserting application configs. Returns JSON serialized
        structured logmessage string.

        :returns: JSON string
        :rtype: str
        """
        ctx_populator = _REGISTER.get('ctx_populator', None)
        if ctx_populator is not None:
            ctx_populator(self.push)
        if self.exc_info:
            exc_type, exc, tb = self.exc_info
            # Make sure exception gets logged properly
            self._log_dict[LM_KEY_EXCEPTION] = format_exception(exc_type, exc, tb)
        self._log_dict[LM_KEY_SEVERITY] = self.levelname
        self._log_dict[LM_KEY_NAME] = self.name
        self._log_dict[LM_KEY_FUNC] = self.funcName
        self._log_dict[LM_KEY_LINE] = self.lineno
        self._log_dict[LM_KEY_PROCID] = self.process
        self._log_dict[LM_KEY_MESSAGE] = super().getMessage()
        return json.dumps(self._log_dict)
