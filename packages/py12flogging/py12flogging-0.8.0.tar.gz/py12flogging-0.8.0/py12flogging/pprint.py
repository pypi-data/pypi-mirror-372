#!/usr/bin/env python3
# Author(s): Toni Sissala
# Copyright 2025 Finnish Social Science Data Archive FSD / University of Tampere
# Licensed under the EUPL. See LICENSE.txt for full license.
"""PrettyPrint JSON from stdin and flush immmediatelly to stdout.

First write a sample program (test_flush.py) which prints out JSON using py12flogging::

    import time, logging
    from py12flogging import log_formatter

    log_formatter.setup_app_logging('myapp')
    for i in range(5):
        logging.info(i)
        time.sleep(1)

Run test_flush.py and direct output unbuffered to py12flogging.pprint::

    python test_flush.py | python -m py12flogging.pprint

If the application whose log output is getting prettyprinted has configured it's own
``logformat``, it may be necessary to do some formatting before piping the stream
to pprint. Example of a sed-command, which discards characters before the first
curly bracket. Note that the buffer should be flushed immediately::

    ./myapp.py | stdbuf -o0 sed 's/[^{]*{/{/' | python -m py12flogging.pprint
"""
import sys
import json
from json.decoder import JSONDecodeError


def main():
    """Indents JSON serialized lines.

    Load the line from stdin as a JSON object. Indent it and flush
    immediately to stdout. If line won't decode as a JSON object
    flush it as-is to stdout.

    :returns: 0 on success.
    :rtype: int
    """
    for line in sys.stdin:
        try:
            obj = json.loads(line)
        except JSONDecodeError:
            sys.stdout.write(line)
        else:
            json.dump(obj, sys.stdout, indent=4)
            sys.stdout.write('\n')
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
