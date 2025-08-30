###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Self

from everysk.config import settings
from everysk.core.exceptions import SDKValueError
from everysk.core.fields import ListField, StrField, ChoiceField
from everysk.sdk.engines.cryptography import generate_unique_id
from everysk.sdk.entities.base import BaseEntity, ScriptMetaClass
from everysk.sdk.entities.fields import EntityNameField, EntityDescriptionField, EntityLinkUIDField, EntityWorkspaceField, EntityDateTimeField, EntityTagsField
from everysk.sdk.entities.query import Query
from everysk.sdk.entities.script import Script


###############################################################################
#   File Class Implementation
###############################################################################
class File(BaseEntity, metaclass=ScriptMetaClass):
    """
    This class represents a file entity object and provides methods to validate and manage the entity's data.

    Attributes:
        script (Script): The script object associated with the file.
        id (StrField): The unique identifier of the file.
        workspace (EntityWorkspaceField): The workspace of the file.
        name (EntityNameField): The name of the file.
        tags (EntityTagsField): The tags of the file.
        description (EntityDescriptionField): The description of the file.
        link_uid (EntityLinkUIDField): The link UID of the file.
        date (EntityDateTimeField): The date associated with the file.
        data (StrField): The file data in base64 format.
        url (StrField): The URL of the file.
        content_type (ChoiceField): The content type of the file.

        version (StrField): The version of the datastore.
        created_on (DateTimeField): The created on date of the datastore.
        updated_on (DateTimeField): The updated on date of the datastore.

    Example:
        >>> from everysk.sdk.entities.file.base import File
        >>> file = File()
        >>> file.script = 'my_script'
        >>> file.id = 'file_12345678'
        >>> file.name = 'My File'
        >>> file.tags = ['tag1', 'tag2']
        >>> file.description = 'This is a sample file.'
        >>> file.workspace = 'my_workspace'
        >>> file.date = DateTime.fromisoformat('20220101')
        >>> file.data = 'base64_encoded_data_here'
        >>> file.content_type = 'application/pdf'
        >>> file.url = '/1234567891011211234567890'
        >>> file.create()
        >>> print(file)
        {
            'id': 'file_12345678',
            'script': 'my_script',
            'name': 'My File',
            'description': 'This is a sample file.',
            'tags': ['tag1', 'tag2'],
            'link_uid': None,
            'workspace': 'my_workspace',
            'date': '20220101',
            'data': 'base64_encoded_data_here',
            'content_type': 'application/pdf',
            'url': '/1234567891011211234567890'
            'created': '2021-01-01T00:00:00.000000Z',
            'updated': '2021-01-01T00:00:00.000000Z',
        }
    """
    script: Script
    _orderable_attributes = ListField(default=['date', 'created_on', 'updated_on', 'name'], readonly=True)
    _allowed_query_attributes_for_all_operators = ListField(default=settings.ENTITY_ALLOWED_QUERY_ATTRIBUTES_FOR_ALL_OPERATORS + ['content_type'], readonly=True)

    id = StrField(regex=settings.FILE_ID_REGEX, max_size=settings.FILE_ID_MAX_SIZE, required_lazy=True, empty_is_none=True)

    name = EntityNameField()
    description = EntityDescriptionField()
    tags = EntityTagsField()
    link_uid = EntityLinkUIDField()
    workspace = EntityWorkspaceField()

    date = EntityDateTimeField()

    hash = StrField(default=None, max_size=settings.FILE_HASH_LENGTH, required_lazy=True)
    data = StrField(default=None, max_size=settings.FILE_DATA_MAX_SIZE_IN_BASE64, required_lazy=True)
    content_type = ChoiceField(default=None, choices=settings.FILE_CONTENT_TYPES, required_lazy=True)
    url = StrField(required_lazy=True)

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
            >>> file = File()
            >>> file.validate()
            True
        """
        return self.get_response(self_obj=self)

    @classmethod
    def validate_transient(cls, entity_dict: dict) -> Self:
        """
        Validate the entity properties.

        Args:
            entity_dict (dict): The entity properties.

        Returns:
            BaseEntity: The entity object.

        Example:
            >>> entity_dict = {'name': 'My Entity'}
            >>> BaseEntity.validate_transient(entity_dict)
        """
        return cls.get_response(params={'entity_dict': entity_dict})

    def _check_entity_to_query(self) -> bool:
        """
        Check the entity object to query.

        Returns:
            bool: True if the entity object is valid.
        """
        super()._check_entity_to_query()
        if self.url and (self.name or self.tags or self.link_uid):
            raise SDKValueError("Can't filter by URL and Name, Tags or Link UID at the same time")

        return True

    def _mount_query(self, query: Query) -> Query:
        """
        Mount the query object.

        Args:
            query (Query): The query object.

        Returns:
            Query: The query object.
        """
        query = super()._mount_query(query)

        if self.url is not None:
            query = query.where('url', self.url)

        return query

    @staticmethod
    def get_id_prefix() -> str:
        """
        Returns the prefix of the file id field value.

        Returns:
            str: The prefix of the file id field value.

        Example:
            >>> File.get_id_prefix()
            'file_'
        """
        return settings.FILE_ID_PREFIX

    @staticmethod
    def generate_url() -> str:
        """
        Generate a unique url for the file.

        Returns:
            str: A unique url for the file.

        Example:
            >>> File.generate_url()
            '/1234567891011211234567890'
        """
        return f'/{generate_unique_id()}'

    def to_dict(self, add_class_path: bool = False, recursion: bool = False) -> dict:
        """
        Convert the entity to a JSON-serializable dictionary.
        This method converts the entity object into a dictionary that can be easily
        serialized to JSON.

        Args:
            self (Self): The entity instance to convert.
            with_internals (bool, optional): Whether to include internal parameters. Defaults to True.
            recursion (bool, optional): Whether to include nested entities. Defaults to False.

        Returns:
            dict: A dictionary representation of the File entity.
        Raises:
            NotImplementedError: This method should be implemented in subclasses.
        """
        dct: dict = super().to_dict(add_class_path=add_class_path, recursion=recursion)

        if add_class_path is False:
            dct['url'] = f"{settings.FILE_URL_PATH}{self.url}" if self.url else None

        return dct
