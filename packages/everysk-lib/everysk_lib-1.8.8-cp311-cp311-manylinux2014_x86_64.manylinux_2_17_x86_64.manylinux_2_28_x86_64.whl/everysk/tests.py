###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=wildcard-import, unused-wildcard-import
try:
    # everysk/api/__init__.py imports requests
    from everysk.api.tests import *
except ModuleNotFoundError as error:
    # This will prevent running these tests if requests is not installed
    if not error.args[0].startswith("No module named 'requests'"):
        raise error

from everysk.core.tests import *
from everysk.sdk.tests import *
from everysk.server.tests import *
