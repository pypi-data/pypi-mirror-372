###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any

from everysk.config import settings
from everysk.core.exceptions import RequiredError, FieldValueError
from everysk.core.fields import ListField, StrField
from everysk.core.serialize import dumps

from everysk.sdk.entities.base import BaseEntity, ScriptMetaClass
from everysk.sdk.entities.fields import EntityNameField, EntityDescriptionField, EntityLinkUIDField, EntityWorkspaceField, EntityDateTimeField, EntityTagsField
from everysk.sdk.entities.script import Script


###############################################################################
#   Datastore Class Implementation
###############################################################################
class Datastore(BaseEntity, metaclass=ScriptMetaClass):
    """
    This class represents a datastore entity object and provides methods to validate
    and manage the entity object's data.

    Attributes:
        script (Script): The script object associated with the datastore.
        id (StrField): The unique identifier of the datastore.
        workspace (EntityWorkspaceField): The workspace of the datastore.
        name (EntityNameField): The name of the datastore.
        tags (EntityTagsField): The tags of the datastore.
        description (EntityDescriptionField): The description of the datastore.
        link_uid (EntityLinkUIDField): The link UID of the datastore.
        date (EntityDateTimeField): The date associated with the datastore.
        data (Any): The data associated with the datastore.
        level (StrField): The level of the datastore.

        version (StrField): The version of the datastore.
        created_on (DateTimeField): The created on date of the datastore.
        updated_on (DateTimeField): The updated on date of the datastore.

    Example:
        >>> from everysk.sdk.entities.datastore.base import Datastore
        >>> datastore = Datastore()
        >>> datastore.id = 'dats_12345678'
        >>> datastore.name = 'My Datastore'
        >>> datastore.tags = ['tag1', 'tag2']
        >>> datastore.description = 'This is a sample datastore.'
        >>> datastore.workspace = 'my_workspace'
        >>> datastore.date = DateTime.fromisoformat('20220101')
        >>> datastore.level = '1'
        >>> datastore.data = {'key1': 'value1', 'key2': 'value2'}
        >>> datastore.create()
        >>> print(datastore)
        {
            'id': 'dats_12345678',
            'name': 'My Datastore',
            'description': 'This is a sample datastore.',
            'tags': ['tag1', 'tag2'],
            'link_uid': None,
            'workspace': 'my_workspace',
            'date': '20220101',
            'level': '1',
            'data': {'key1': 'value1', 'key2': 'value2'},
            'version': 'v1',
            'created_on': '2021-01-01T00:00:00.000000Z',
            'updated_on': '2021-01-01T00:00:00.000000Z',
        }
    """
    script: Script = None
    _orderable_attributes = ListField(default=['date', 'created_on', 'updated_on', 'name'], readonly=True)

    id = StrField(regex=settings.DATASTORE_ID_REGEX, max_size=settings.DATASTORE_ID_MAX_SIZE, required_lazy=True, empty_is_none=True)

    name = EntityNameField()
    description = EntityDescriptionField()
    tags = EntityTagsField()
    link_uid = EntityLinkUIDField()
    workspace = EntityWorkspaceField()

    date = EntityDateTimeField()
    level = StrField(min_size=1, max_size=settings.DATASTORE_LEVEL_MAX_LENGTH)

    data: Any = None

    def __init__(self, data=None, **kwargs) -> None:
        super().__init__(data=data, **kwargs)

    @staticmethod
    def get_id_prefix() -> str:
        """
        Returns the prefix of the datastore id field value.

        Returns:
            str: The prefix of the datastore id field value.

        Example:
            >>> Datastore.get_id_prefix()
            'dats_'

        Notes:
            The prefix is typically used to distinguish datastore IDs from other types of IDs
        """
        return settings.DATASTORE_ID_PREFIX

    def validate_type_data(self) -> bool:
        """
        Validates the 'data' attribute of the Datastore entity to ensure it is not None and contains valid JSON data.

        Raises:
            RequiredError: If the 'data' attribute is None.
            FieldValueError: If the 'data' attribute is not valid JSON.

        Returns:
            bool: True if validation succeeds.

        Example:
            >>> datastore = Datastore()
            >>> datastore.data = {'key1': 'value1', 'key2': 'value2'}
            >>> datastore.validate_type_data()  # Validation succeeds
            True
        """

        if self.data is None:
            raise RequiredError('The data attribute is required')

        try:
            dumps(self.data)
        except Exception as exc: # pylint: disable=broad-except
            raise FieldValueError('Datastore data is not a valid json') from exc

        return True

    def validate(self) -> bool:
        """
        This method validates the entity object and raises an exception if it is not
        valid. The validation is performed by calling the `validate` method of each field
        of the entity.

        Args:
            self (Self): The entity object to be validated.

        Raises:
            FieldValueError: If the entity object is not valid.
            RequiredFieldError: If a required field is missing.

        Returns:
            bool: True if the entity object is valid, False otherwise.

        Example:
            >>> entity = Entity()
            >>> entity.validate()
            True
        """
        self.validate_type_data()
        return self.get_response(self_obj=self)
