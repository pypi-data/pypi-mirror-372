import unittest
from unittest import mock
import json
from io import StringIO
from py12flogging import pprint


class TestPprint(unittest.TestCase):

    @mock.patch.object(pprint, 'sys')
    def test_multiple_json_objects(self, mock_sys):
        mock_sys.stdout = StringIO()
        mock_sys.stdin = iter([json.dumps({'index': 1}),
                               json.dumps({'index': 2}),
                               json.dumps({'index': 3})])
        pprint.main()
        # Output is printed to stdout indented by 4 whitespaces
        # and contains newlines.
        expected = ('{\n    "index": 1\n}\n'
                    '{\n    "index": 2\n}\n'
                    '{\n    "index": 3\n}\n')
        self.assertEqual(mock_sys.stdout.getvalue(), expected)

    @mock.patch.object(pprint, 'sys')
    def test_with_non_json_object(self, mock_sys):
        mock_sys.stdout = StringIO()
        mock_sys.stdin = iter(['Traceback (most recent call last):\n',
                               '  File "<stdin>", line 1, in <module>\n',
                               'ZeroDivisionError: division by zero\n'])
        pprint.main()
        expected = ('Traceback (most recent call last):\n'
                    '  File "<stdin>", line 1, in <module>\n'
                    'ZeroDivisionError: division by zero\n')
        self.assertEqual(mock_sys.stdout.getvalue(), expected)

    @mock.patch.object(pprint, 'sys')
    def test_combination(self, mock_sys):
        mock_sys.stdout = StringIO()
        mock_sys.stdin = iter([json.dumps({'some': 'object'}),
                               'some_str',
                               json.dumps({'another': 'object'})])
        pprint.main()
        expected = ('{\n    "some": "object"\n}\n'
                    'some_str'
                    '{\n    "another": "object"\n}\n')
        self.assertEqual(mock_sys.stdout.getvalue(), expected)


if __name__ == '__main__':
    unittest.main()
