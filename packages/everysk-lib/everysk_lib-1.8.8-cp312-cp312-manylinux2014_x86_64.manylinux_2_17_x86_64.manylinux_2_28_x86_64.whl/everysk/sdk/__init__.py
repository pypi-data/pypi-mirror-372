###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.string import import_from_string


###############################################################################
#   Private Functions Implementation
###############################################################################
def __getattr__(_name: str):
    from everysk.config import settings # pylint: disable=import-outside-toplevel
    modules = settings.EVERYSK_SDK_MODULES_PATH

    if _name in modules:
        return import_from_string(modules[_name])

    raise AttributeError(f"cannot import name '{_name}' from everysk.sdk")
