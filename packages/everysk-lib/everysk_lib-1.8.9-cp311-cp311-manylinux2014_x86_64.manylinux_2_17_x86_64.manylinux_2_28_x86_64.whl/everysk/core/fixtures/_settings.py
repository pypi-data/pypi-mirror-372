###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import re
from everysk.core.fields import BoolField, StrField


_EVERYSK_PRIVATE = StrField(default='private-attribute')
EVERYSK_TEST_NAME = StrField(default='test-case', readonly=True)
EVERYSK_TEST_FAKE = True
EVERYSK_TEST_INT: int = 1
EVERYSK_TEST_FIELD_INHERIT = StrField(default='{EVERYSK_TEST_NAME} as {EVERYSK_TEST_FAKE}')
EVERYSK_TEST_VAR_INHERIT = '{EVERYSK_TEST_FAKE} as {EVERYSK_TEST_NAME}'
EVERYSK_TEST_BOOL_VAR = BoolField(default=False)

# Settings with default values
EVERYSK_TEST_STR_DEFAULT_NONE: str = None
EVERYSK_TEST_STR_DEFAULT_UNDEFINED: str = Undefined

# https://everysk.atlassian.net/browse/COD-4197
EVERYSK_TEST_RE_PATTERN: re.Pattern = re.compile(r'[azAZ]')
EVERYSK_TEST_RE_PATTERN_NONE: re.Pattern = None
EVERYSK_TEST_RE_PATTERN_UNDEFINED: re.Pattern = Undefined
