# -*- coding: utf_8 -*-
###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.config import settings
from everysk.core.fields import StrField

from everysk.sdk.entities.base import BaseEntity
from everysk.sdk.entities.fields import EntityDescriptionField, EntityWorkspaceField

###############################################################################
#   Securities Field Implementation
###############################################################################

###############################################################################
#   Portfolio Implementation
###############################################################################
class Workspace(BaseEntity):

    name = EntityWorkspaceField()
    description = EntityDescriptionField(max_size=settings.WORKSPACE_DESCRIPTION_MAX_LENGTH)
    group = StrField(default=None, max_size=settings.WORKSPACE_GROUP_MAX_LENGTH, min_size=settings.WORKSPACE_GROUP_MIN_LENGTH, empty_is_none=True)

    @property
    def id(self) -> str:
        """
        Returns the id of the workspace. The id is a alias for the name.

        Returns:
            str: The id of the workspace.

        Example:
            >>> workspace = Workspace(name='custom')
            >>> workspace.id
            'custom'
        """
        return self.name

    @id.setter
    def id(self, value: str) -> None:
        """
        Sets the id of the workspace. The id is a alias for the name.

        Args:
            value (str): The id of the workspace.

        Example:
            >>> workspace = Workspace()
            >>> workspace.id = 'custom'
            >>> workspace.name
            'custom'
            >>> workspace.id
            'custom'
        """
        self.name = value

    @staticmethod
    def get_id_prefix():
        """
        Returns the id prefix for the workspace.

        Returns:
            str: The id prefix for the workspace.
        """
        return settings.WORKSPACE_ID_PREFIX

    def generate_id(self) -> str:
        """
        Generate a unique ID for an entity instance.

        Returns:
            str: The generated unique ID.

        Example:
            To generate a unique ID for an entity instance:
            >>> unique_id = MyEntity().generate_id()
        """
        raise NotImplementedError

    def to_dict(self, add_class_path = False, recursion = False) -> dict:
        """
        This method is used to convert the object to a dictionary.
        """
        dct: dict = super().to_dict(add_class_path, recursion)

        if not self.description:
            dct['description'] = ''

        return dct
