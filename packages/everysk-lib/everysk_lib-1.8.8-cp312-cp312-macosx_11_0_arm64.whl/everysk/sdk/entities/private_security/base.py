###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.config import settings
from everysk.core.exceptions import SDKValueError
from everysk.core.fields import ListField, StrField, ChoiceField, DictField
from everysk.sdk.entities.base import BaseEntity, ScriptMetaClass
from everysk.sdk.entities.fields import CurrencyField, EntityNameField, EntityDescriptionField, EntityTagsField
from everysk.sdk.entities.query import Query
from everysk.sdk.entities.script import Script


###############################################################################
#   PrivateSecurity Class Implementation
###############################################################################
class PrivateSecurity(BaseEntity, metaclass=ScriptMetaClass):
    """
    This class represents a private security entity object.

    Attributes:
        script (Script): The script object associated to the entity.
        _orderable_attributes (ListField): The list of orderable attributes.
        symbol (StrField): The symbol of the private security.
        id (StrField): The id of the private security.
        data (ListField): The data of the private security.

        currency (CurrencyField): The currency of the private security.
        instrument_type (ChoiceField): The instrument type of the private security.

        description (EntityDescriptionField): The description of the private security.
        name (EntityNameField): The name of the private security.
        tags (EntityTagsField): The tags of the private security.

        created_on (DateTimeField): The creation date of the private security.
        updated_on (DateTimeField): The last update date of the private security.
        version (IntField): The version of the private security.

    Example:
        >>> from everysk.sdk.entities.private_security.base import PrivateSecurity
        >>> private_security = PrivateSecurity(
            symbol='PRIVATE:SECURITY',
            data={...},
            currency='USD',
            instrument_type='PrivateFixedIncome',
            description='Private Security description',
            name='Private Security name',
            tags=['tag1', 'tag2']
        )
        >>> private_security.save()
    """
    script: Script = None
    _orderable_attributes = ListField(default=['created_on', 'updated_on', 'name'], readonly=True)

    symbol = StrField(regex=settings.PRIVATE_SECURITY_SYMBOL_REGEX, min_size=settings.PRIVATE_SECURITY_SYMBOL_MIN_SIZE, max_size=settings.PRIVATE_SECURITY_SYMBOL_MAX_SIZE, required_lazy=True, empty_is_none=True)

    data = DictField(required_lazy=True)

    currency = CurrencyField()
    instrument_type = ChoiceField(default=None, choices=('PrivateFixedIncome', 'PrivateCustomIndex', None), required_lazy=True)

    description = EntityDescriptionField()
    name = EntityNameField()
    tags = EntityTagsField()

    @property
    def id(self) -> str:
        """
        Returns the id of the private security. The id is a alias for the symbol.

        Returns:
            str: The id of the private security.

        Example:
            >>> private_security = PrivateSecurity(symbol='PRIVATE:SECURITY')
            >>> private_security.id
            'PRIVATE:SECURITY'
        """
        return self.symbol

    @id.setter
    def id(self, value: str) -> None:
        """
        Sets the id of the private security. The id is a alias for the symbol.

        Args:
            value (str): The id of the private security.

        Example:
            >>> private_security = PrivateSecurity()
            >>> private_security.id = 'PRIVATE:SECURITY'
            >>> private_security.symbol
            'PRIVATE:SECURITY'
            >>> private_security.id
            'PRIVATE:SECURITY'
        """
        self.symbol = value

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
            >>> private_security = PrivateSecurity(symbol='PRIVATE:SECURITY', name='Private Security name', ...)
            >>> private_security.validate()
            True
        """
        return self.get_response(self_obj=self)

    def _pre_validate(self):
        pass

    def _pos_validate(self):
        self.created_on = None
        self.updated_on = None

    def _check_query(self, query: Query) -> bool:
        """
        Check the query object.

        Args:
            query (Query): The query object.

        Returns:
            Query: The query object.
        """
        return True

    def _check_entity_to_query(self) -> bool:
        """
        Check the entity object to query.

        Returns:
            bool: True if the entity object is valid.
        """
        if self.name and self.tags:
            raise SDKValueError("Can't filter by Name and Tags at the same time")

        return True

    def _mount_query(self, query: Query) -> Query:
        """
        Mount the query object.

        Args:
            query (Query): The query object.

        Returns:
            Query: The query object.
        """
        if self.name is not None:
            query = query.where('name', self.name)
        if self.tags:
            query = query.where('tags', self.tags)

        return query

    @staticmethod
    def get_id_prefix() -> str:
        """
        Returns the prefix of the private security id field value.

        Returns:
            str: The prefix of the private security id field value.

        Example:
            >>> PrivateSecurity.get_id_prefix()
            'PRIVATE:'
        """
        return settings.PRIVATE_SECURITY_SYMBOL_PREFIX

    @classmethod
    def modify_many(cls, entity_id_list: list[str], overwrites: dict | list[dict]) -> list:
        """
        The private security does not support the modify_many method.
        """
        raise NotImplementedError()

    @classmethod
    def clone_many(cls, entity_id_list: list[str], overwrites: dict | list[dict]) -> list:
        """
        The private security does not support the clone_many method.
        """
        raise NotImplementedError()

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
            dict: A dictionary representation of the entity.

        Raises:
            NotImplementedError: This method should be implemented in subclasses.
        """
        dct: dict = super().to_dict(add_class_path=add_class_path, recursion=recursion)

        if add_class_path is False:
            dct['type'] = dct.pop('instrument_type', None)

        return dct
