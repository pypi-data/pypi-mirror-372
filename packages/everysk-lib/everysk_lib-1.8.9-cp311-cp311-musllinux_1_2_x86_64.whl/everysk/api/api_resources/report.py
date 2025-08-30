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
    UpdateableAPIResource
)
from everysk.api import utils

###############################################################################
#   Report Implementation
###############################################################################
class Report(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    UpdateableAPIResource
):

    def share(self, **kwargs):
        """
        Shares the current instance of the report by creating a shareable link. This method sends a POST request
        to the API, setting up the sharing configurations based on the provided arguments.

        Args:
            expires_after (str, optional):
                A key representing the time for the shareable link before it expires.
                Valid keys and their corresponding time values should be predefined and
                mapped correctly in the 'SHARED_URL_MAX_AGE_MAP'.

            skin_theme (str, optional):
                A key to determine the theme of the shared report. This should correspond to
                one of the predefined themes in the 'SKIN_THEME_MAP'.

            **kwargs:
                Additional keyword arguments that are passed to the API endpoint, allowing further customization
                of the share operation.

        Returns:
            Report: The updated report instance.

        Example:
            >>> report = Report.retrieve('report_id')
            >>> report.share(user_id='user_id')
            >>> Shared report_object
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f"{self.class_url()}/{self.get('id')}/share"
        response = api_req.post(url, kwargs)
        data = response[self.class_name()]
        self.update(data)
        self.clear_unsaved_values()
        return self
