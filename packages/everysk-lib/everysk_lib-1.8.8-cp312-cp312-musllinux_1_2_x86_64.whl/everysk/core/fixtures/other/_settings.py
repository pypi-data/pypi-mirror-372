###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import StrField


_EVERYSK_OTHER_PRIVATE: str = 'private-attribute'
EVERYSK_TEST_OTHER_NAME = StrField(default='test-other-case', readonly=True)
EVERYSK_TEST_OTHER_FAKE = True
EVERYSK_TEST_OTHER_INT: int = 2
EVERYSK_TEST_OTHER_FIELD_INHERIT = StrField(default='{EVERYSK_TEST_NAME} as {EVERYSK_TEST_FAKE}')
EVERYSK_TEST_OTHER_VAR_INHERIT = '{EVERYSK_TEST_FAKE} as {EVERYSK_TEST_NAME}'
