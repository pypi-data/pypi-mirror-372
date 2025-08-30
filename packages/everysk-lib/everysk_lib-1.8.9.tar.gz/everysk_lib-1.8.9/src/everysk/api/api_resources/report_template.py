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
    DeletableAPIResource,
    RetrievableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource
)

###############################################################################
#   Report Template Implementation
###############################################################################
class ReportTemplate(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    UpdateableAPIResource
):
    """
    Represents a report template.

    This class inherits from the following API resource classes:
    - RetrievableAPIResource
    - ListableAPIResource
    - DeletableAPIResource
    - UpdateableAPIResource
    """
    pass
