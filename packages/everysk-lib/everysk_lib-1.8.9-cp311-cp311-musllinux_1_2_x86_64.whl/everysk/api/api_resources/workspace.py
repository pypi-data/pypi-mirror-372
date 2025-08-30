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
#   Workspace Implementation
###############################################################################
class Workspace(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    CreateableAPIResource,
    UpdateableAPIResource
):
    """
    Represents a workspace object

    Args:
        RetrievableAPIResource (_type_): _description_
        ListableAPIResource (_type_): _description_
        DeletableAPIResource (_type_): _description_
        CreateableAPIResource (_type_): _description_
        UpdateableAPIResource (_type_): _description_
    """
    pass
