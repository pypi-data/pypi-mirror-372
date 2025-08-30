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
    UpdateableAPIResource,
    FilterableAPIResource
)

###############################################################################
#   Portfolio Implementation
###############################################################################
class Portfolio(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    CreateableAPIResource,
    UpdateableAPIResource,
    FilterableAPIResource
):
    """
    This class inherits from various API resource classes to provide different operations on the portfolio resource:
        - RetrievableAPIResource
        - ListableAPIResource
        - DeletableAPIResource
        - CreateableAPIResource
        - UpdateableAPIResource
        - FilterableAPIResource
    """
    pass
