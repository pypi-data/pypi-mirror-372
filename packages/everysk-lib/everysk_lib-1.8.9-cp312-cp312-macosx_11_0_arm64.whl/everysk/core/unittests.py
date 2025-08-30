###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['TestCase', 'mock', 'skip', 'skipUnless', 'SkipTest', 'skipIf']

import difflib
import pprint
from time import time
from typing import Any
from unittest import TestCase as PythonTestCase, mock, skip, skipUnless, SkipTest, skipIf
from unittest.util import _common_shorten_repr
from warnings import warn

from everysk.config import settings
from everysk.core.object import BaseDict


###############################################################################
#   TestCase Class Implementation
###############################################################################
class TestCase(PythonTestCase):

    def _callTestMethod(self, method: callable) -> None:
        # For some tests the time could not pass 1 second, gzip tests for example.
        # So we use mock to fix the time for the tests.
        original_time = time()
        with mock.patch('time.time', return_value=original_time):
            # We could not use super here because the stacklevel would be wrong
            if method() is not None:
                warn(
                    f'It is deprecated to return a value that is not None from a test case ({method})',
                    DeprecationWarning,
                    stacklevel=3
                )

    def assertDictEqual(self, d1: dict | BaseDict, d2: dict | BaseDict, msg: str = None):
        # pylint: disable=protected-access
        self.assertIsInstance(d1, (dict, BaseDict), 'First argument is not a dictionary')
        self.assertIsInstance(d2, (dict, BaseDict), 'Second argument is not a dictionary')

        # We need to ensure that both objects are of the same type to proceed
        if isinstance(d1, dict) and isinstance(d2, BaseDict):
            d1 = type(d2)(**d1)

        elif isinstance(d2, dict) and isinstance(d1, BaseDict):
            d2 = type(d1)(**d2)

        if d1 != d2:
            standardMsg = '%s != %s' % _common_shorten_repr(d1, d2) # pylint: disable=consider-using-f-string, invalid-name
            diff = ('\n' + '\n'.join(difflib.ndiff(
                            pprint.pformat(d1).splitlines(),
                            pprint.pformat(d2).splitlines())))
            standardMsg = self._truncateMessage(standardMsg, diff) # pylint: disable=invalid-name
            self.fail(self._formatMessage(msg, standardMsg))


###############################################################################
#   EveryskMagicMock Class Implementation
###############################################################################
class EveryskMagicMock(mock.MagicMock): # pylint: disable=too-many-ancestors

    def __init__(self, *args: Any, **kw: Any) -> None:
        super().__init__(*args, **kw)
        # To avoid infinite recursion inside serialize.dumps we need to remove this method
        delattr(self, settings.SERIALIZE_CONVERT_METHOD_NAME)

mock.MagicMock = EveryskMagicMock
