###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Final, LiteralString

__all__ = ("__version__", "version")
# the version will be changed on build
version: Final[LiteralString] = "$VERSION"
__version__: Final[LiteralString] = version
