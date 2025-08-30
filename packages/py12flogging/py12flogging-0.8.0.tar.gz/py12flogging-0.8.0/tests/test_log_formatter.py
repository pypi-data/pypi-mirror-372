import logging
import unittest
from datetime import datetime, timezone
from io import StringIO
from logging.config import dictConfig
from unittest import mock
from py12flogging import log_formatter


class TestSetupAppLogging(unittest.TestCase):

    maxDiff = None

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_changes_factory(self):
        old_factory = logging.getLogRecordFactory()
        log_formatter.setup_app_logging('py12flogging')
        self.assertNotEqual(logging.getLogRecordFactory(), old_factory)

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_switches_to_JSONLogRecord(self):
        log_formatter.setup_app_logging('py12flogging')
        with self.assertLogs() as cm:
            logging.info('asd')
        self.assertEqual(type(cm.records[0]), log_formatter.JSONLogRecord)

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_sets_app_configs(self):
        self.assertEqual(log_formatter._REGISTER['app_config'], {})
        log_formatter.setup_app_logging('py12flogging', app_id='app_id', app_version='app_version',
                                        host_ip='host_ip', port='port')
        self.assertEqual(log_formatter._REGISTER['app_config'], {
            'app_name': 'py12flogging',
            'app_id': 'app_id',
            'app_version': 'app_version',
            'host_ip': 'host_ip',
            'port': 'port'})

    @mock.patch.object(log_formatter, 'metadata', return_value={"version": "someversion"})
    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_finds_app_version(self, mock_metadata):
        log_formatter.setup_app_logging('someapp')
        self.assertEqual(log_formatter._REGISTER['app_config']['app_version'], 'someversion')
        mock_metadata.assert_called_once_with('someapp')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_raises_Exception_on_consecutive_call(self):
        log_formatter.setup_app_logging('py12flogging')
        with self.assertRaises(log_formatter.LogConfigException):
            log_formatter.setup_app_logging('py12flogging')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_warns_on_nonexisting_appname_and_uses_no_version(self):
        with self.assertWarns(UserWarning) as warn_ctx:
            log_formatter.setup_app_logging('nonexistent_app')
        self.assertEqual(warn_ctx.warning.args, ("Package not found: 'nonexistent_app'",))
        self.assertEqual(log_formatter._REGISTER['app_config']['app_version'], None)

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    @mock.patch.object(log_formatter, 'dictConfig')
    def test_calls_logging_dictConfig(self, mock_dictConfig):
        mock_dictConfig.assert_not_called()
        log_formatter.setup_app_logging('py12flogging')
        self.assertEqual(mock_dictConfig.call_count, 1)

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    @mock.patch.object(log_formatter, 'dictConfig')
    def test_does_not_call_logging_dictConfig(self, mock_dictConfig):
        mock_dictConfig.assert_not_called()
        log_formatter.setup_app_logging('py12flogging', configure_logging=False)
        mock_dictConfig.assert_not_called()

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    @mock.patch.object(log_formatter, 'config_dict', return_value='rval')
    @mock.patch.object(log_formatter, 'dictConfig')
    def test_calls_config_dict_with_params(self, mock_dictConfig, mock_config_dict):
        mock_config_dict.assert_not_called()
        log_formatter.setup_app_logging('py12flogging', loglevel='loglevel',
                                        logformat='some_format',
                                        disable_existing_loggers='disable_existing_loggers')
        mock_config_dict.assert_called_once_with('loglevel', 'some_format', 'disable_existing_loggers')
        mock_dictConfig.assert_called_once_with('rval')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_raises_ValueError_on_invalid_loglevel(self):
        with self.assertRaises(ValueError):
            log_formatter.setup_app_logging('py12flogging', loglevel='invalid')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_raises_TypeError_for_unknown_kwargs(self):
        with self.assertRaises(TypeError):
            log_formatter.setup_app_logging('py12flogging', unknown='kw')


class TestConfigDict(unittest.TestCase):

    def test_sets_root_loglevel(self):
        config_dict = log_formatter.config_dict('loglevel', 'logformat', 'disable_existing_loggers')
        self.assertEqual(config_dict['root']['level'], 'loglevel')

    def test_sets_disable_existing_loggers(self):
        config_dict = log_formatter.config_dict('loglevel', 'logformat', 'disable_existing_loggers')
        self.assertEqual(config_dict['disable_existing_loggers'], 'disable_existing_loggers')

    def test_sets_logformat(self):
        config_dict = log_formatter.config_dict('loglevel', 'logformat', 'disable_existing_loggers')
        self.assertEqual(config_dict['formatters']['service_formatter']['format'], 'logformat')


# Patching to silence superficial resourcewarning about unclosed event loop.
@mock.patch.object(log_formatter, 'warnings', new=mock.Mock())
class TestPushToDict(unittest.TestCase):

    def setUp(self):
        self.adict = {}
        self.pusher = log_formatter._push_to_dict(self.adict)
        super().setUp()

    def test_pushes_to_dict(self):
        self.assertEqual(self.adict, {})
        self.pusher('key', 'value')
        self.assertEqual(self.adict, {'key': 'value'})

    def test_overwrites_existing_when_commanded(self):
        self.assertEqual(self.adict, {})
        self.pusher('first', 1)
        self.assertEqual(self.adict, {'first': 1})
        self.pusher('first', 0, overwrite=True)
        self.assertEqual(self.adict, {'first': 0})

    def test_suffixes_key_if_exists(self):
        self.assertEqual(self.adict, {})
        self.pusher('key', 'value')
        self.pusher('key_', 'another_value')
        self.pusher('key', 'yet_another_value')
        self.assertEqual(self.adict, {'key': 'value',
                                      'key_': 'another_value',
                                      'key__': 'yet_another_value'})

    def test_reserves_keys(self):
        adict = {}
        pusher = log_formatter._push_to_dict(adict, 'reserved', 'also_reserved')
        pusher('reserved', 'some_value')
        self.assertEqual(adict, {'reserved_': 'some_value'})
        pusher('also_reserved', 'some_value', overwrite=True)
        self.assertEqual(adict, {'reserved_': 'some_value', 'also_reserved_': 'some_value'})


@mock.patch.object(log_formatter.json, 'dumps', return_value='testing')
class TestLogEvent(unittest.TestCase):

    def _assert_in(self, _dict, key, value=None):
        self.assertIn(key, _dict)
        if value:
            self.assertEqual(_dict[key], value)

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_log_msg_contains_required_common_contents(self, mock_json_dumps):
        """Log message must contain common contents"""
        mock_json_dumps.asssrt_not_called()
        log_formatter.setup_app_logging('py12flogging')
        # Call (indirect)
        logging.warning('asd')
        # Assert
        self.assertEqual(mock_json_dumps.call_count, 1)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self._assert_in(log_dict, 'severity', 'WARNING')
        self._assert_in(log_dict, 'message', 'asd')
        self._assert_in(log_dict, 'timestamp')
        self._assert_in(log_dict, 'procid')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_log_msg_contains_app_configs(self, mock_json_dumps):
        """Log message must contain app_configs"""
        mock_json_dumps.assert_not_called()
        log_formatter.setup_app_logging('py12flogging', app_version='vers_1',
                                        app_id='some_id', host_ip='some_host',
                                        port='some_port')
        # Call
        logging.warning('qwe')
        # Assert
        self.assertEqual(mock_json_dumps.call_count, 1)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self._assert_in(log_dict, 'app_name', 'py12flogging')
        self._assert_in(log_dict, 'app_version', 'vers_1')
        self._assert_in(log_dict, 'app_id', 'some_id')
        self._assert_in(log_dict, 'host_ip', 'some_host')
        self._assert_in(log_dict, 'port', 'some_port')
        self._assert_in(log_dict, 'message', 'qwe')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_log_msg_contains_populated_ctx(self, mock_json_dumps):
        """ctx_populator must be called and context pushed to log message"""
        mock_json_dumps.assert_not_called()
        mock_populator = mock.Mock(side_effect=lambda push: push('some_key', 'some_value'))
        log_formatter.setup_app_logging('py12flogging')
        log_formatter.set_ctx_populator(mock_populator)
        # Call
        logging.warning('zxc')
        # Assert
        self.assertEqual(mock_json_dumps.call_count, 1)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self._assert_in(log_dict, 'some_key', 'some_value')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_log_msg_contains_exception(self, mock_json_dumps):
        mock_json_dumps.assert_not_called()
        log_formatter.setup_app_logging('py12flogging')
        # Call (indirect)
        try:
            1/0  # create exception
        except:
            logging.exception('exc')
        # Assert
        self.assertEqual(mock_json_dumps.call_count, 1)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self._assert_in(log_dict, 'exception')
        self._assert_in(log_dict['exception'], 'type', "<class 'ZeroDivisionError'>")
        self._assert_in(log_dict['exception'], 'message', 'division by zero')
        self._assert_in(log_dict['exception'], 'traceback')  # Not going to dig into the traceback

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_logging_to_arbitrary_keys_if_changed(self, mock_json_dumps):
        # Setup
        self.assertEqual(log_formatter._REGISTER['app_config'], {})
        old_appname = log_formatter.LM_KEY_APPNAME
        log_formatter.LM_KEY_APPNAME = 'new_appname'
        old_appid = log_formatter.LM_KEY_APPID
        log_formatter.LM_KEY_APPID = 'new_appid'
        old_appvers = log_formatter.LM_KEY_APPVERS
        log_formatter.LM_KEY_APPVERS = 'new_appvers'
        old_hostip = log_formatter.LM_KEY_HOSTIP
        log_formatter.LM_KEY_HOSTIP = 'new_hostip'
        old_port = log_formatter.LM_KEY_PORT
        log_formatter.LM_KEY_PORT = 'new_port'
        # call
        log_formatter.setup_app_logging('py12flogging', app_id='appid', app_version='app_version',
                                        host_ip='host_ip', port='port')
        logging.warning('qwe')
        # assert
        self.assertEqual(mock_json_dumps.call_count, 1)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self._assert_in(log_dict, 'new_appname', 'py12flogging')
        self._assert_in(log_dict, 'new_appid', 'appid')
        self._assert_in(log_dict, 'new_appvers', 'app_version')
        self._assert_in(log_dict, 'new_hostip', 'host_ip')
        self._assert_in(log_dict, 'new_port', 'port')
        # TearDown
        log_formatter.LM_KEY_APPNAME = old_appname
        log_formatter.LM_KEY_APPID = old_appid
        log_formatter.LM_KEY_APPVERS = old_appvers
        log_formatter.LM_KEY_HOSTIP = old_hostip
        log_formatter.LM_KEY_PORT = old_port

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_push_to_ctx_pushes_to_ctx(self, mock_json_dumps):
        # setup
        log_formatter.setup_app_logging('py12flogging')
        log_formatter.push_to_ctx('some_key', 'some_value')
        # call
        logging.warning('asd')
        # assert
        self.assertEqual(mock_json_dumps.call_count, 1)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self._assert_in(log_dict, 'some_key', 'some_value')

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_push_to_ctx_clears_ctx_on_logevent(self, mock_json_dumps):
        # setup
        log_formatter.setup_app_logging('py12flogging')
        log_formatter.push_to_ctx('another_key', 'some_value')
        # call
        logging.warning('asd')
        # assert
        self.assertEqual(mock_json_dumps.call_count, 1)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self._assert_in(log_dict, 'another_key', 'some_value')
        # another call
        logging.warning('qwe')
        self.assertEqual(mock_json_dumps.call_count, 2)
        args, kwargs = mock_json_dumps.call_args
        self.assertEqual(kwargs, {})
        self.assertEqual(len(args), 1)
        log_dict = args[0]
        self.assertNotIn('another_key', log_dict)


class TestLogFormatter(unittest.TestCase):

    def setUp(self):
        # Make sure we are using stdlibs recordfactory
        if logging.getLogRecordFactory() != logging.LogRecord:
            logging.setLogRecordFactory(logging.LogRecord)
        super().setUp()

    def test_formats_std_logrecord(self):
        """LogFormatter must be able to format stdlib's logrecord instance.

        The idea is that LogFormatter can be used to simply switch logging
        timestamp to UTC."""
        dictConfig(log_formatter.config_dict('INFO', '%(message)s', False))
        with self.assertLogs() as cm:
            logging.info('asd')
        self.assertEqual(cm.output, ['INFO:root:asd'])
        self.assertEqual(type(cm.records[0]), logging.LogRecord)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_formats_logformat(self, mock_stdout):
        dictConfig(log_formatter.config_dict('ERROR', '%(levelname)s %(message)s', False))
        # call with warning -> expect no output
        logging.warning('mymessage')
        # Assert
        self.assertEqual(mock_stdout.getvalue(), '')
        # Call with error -> expect correctly formatted output
        logging.error('mymessage')
        # Assert
        self.assertEqual(mock_stdout.getvalue(), 'ERROR mymessage\n')

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_formats_std_logrecord_timestamp(self, mock_stdout):
        dictConfig(log_formatter.config_dict('INFO', '%(asctime)s %(message)s', False))
        # Call
        logging.info('asd')  # First timestamp is generated
        # Assert
        expected_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')  # Second timestamp is generated
        timestamp = mock_stdout.getvalue().split().pop(0)
        self.assertEqual(timestamp, expected_timestamp, msg='In some cases there can a be seconds difference')


class TestPushToCtx(unittest.TestCase):

    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_raises_LogConfigException_if_ctx_populator_is_set(self):
        log_formatter.setup_app_logging('py12flogging')
        log_formatter.set_ctx_populator(lambda push: push('key', 'value'))
        with self.assertRaises(log_formatter.LogConfigException):
            log_formatter.push_to_ctx('some_key', 'somevalue')

    @mock.patch.object(log_formatter, 'set_ctx_populator')
    @mock.patch.dict(log_formatter._REGISTER, {'app_config': {}, 'ctx_populator': None})
    def test_calls_set_ctx_populator_once(self, mock_set_ctx_populator):
        def proxy(populator):
            log_formatter._REGISTER['ctx_populator'] = populator
        mock_set_ctx_populator.side_effect = proxy
        log_formatter.setup_app_logging('py12flogging')
        log_formatter.push_to_ctx('some_key', 'some_value')
        self.assertEqual(mock_set_ctx_populator.call_count, 1)
        log_formatter.push_to_ctx('some_key', 'some_value')
        self.assertEqual(mock_set_ctx_populator.call_count, 1)


if __name__ == '__main__':
    unittest.main()
