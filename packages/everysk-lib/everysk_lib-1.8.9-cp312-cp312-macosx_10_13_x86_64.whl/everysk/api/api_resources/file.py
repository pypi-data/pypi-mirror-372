###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.api.api_resources.api_resource import (
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    CreateableAPIResource,
    UpdateableAPIResource
)

###############################################################################
#   File Implementation
###############################################################################
class File(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    CreateableAPIResource,
    UpdateableAPIResource
):
    """
    Represents a file resource.

    This class inherits from the following API resource classes:
        - RetrievableAPIResource
        - ListableAPIResource
        - DeletableAPIResource
        - CreateableAPIResource
        - UpdateableAPIResource
    """
    pass
