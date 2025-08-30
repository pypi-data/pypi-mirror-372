###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.sdk.base import BaseSDK


###############################################################################
#   Compliance Class Implementation
###############################################################################
class Compliance(BaseSDK):

    @classmethod
    def check(cls, rules: list, datastore: list, metadata: dict = None) -> dict:
        """
        Check compliance of data against rules.

        Args:
            rules (list): The rules to check against.
            datastore (list): The data to check.
            metadata (dict, optional): The metadata to use for checking. Default is None.

        Returns:
            dict: The compliance check result.

        Example:
            >>> Compliance.check(rules=[{'rule': 'rule1'}, {'rule': 'rule2'}], datastore=[{'data': 'data1'}, {'data': 'data2'}])
            {
                'compliance': True
            }
        """
        return cls.get_response(params={'rules': rules, 'datastore': datastore, 'metadata': metadata})
