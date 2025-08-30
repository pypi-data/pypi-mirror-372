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
from everysk.core.fields import ListField, StrField, FloatField, ChoiceField
from everysk.core.exceptions import SDKValueError
from everysk.sdk.entities.base import BaseEntity, ScriptMetaClass
from everysk.sdk.entities.query import Query
from everysk.sdk.entities.script import Script
from everysk.sdk.entities.fields import CurrencyField, EntityNameField, EntityDescriptionField, EntityTagsField


###############################################################################
#   CustomIndex Class Implementation
###############################################################################
class CustomIndex(BaseEntity, metaclass=ScriptMetaClass):
    """
    This class represents a custom index entity object.

    Attributes:
        script (Script): The script object associated to the entity.
        _orderable_attributes (ListField): The list of orderable attributes.
        symbol (StrField): The symbol of the custom index.
        id (StrField): The id of the custom index.
        data (ListField): The data of the custom index.

        periodicity (ChoiceField): The periodicity of the custom index.
        data_type (ChoiceField): The data type of the custom index.
        currency (CurrencyField): The currency of the custom index.
        base_price (FloatField): The base price of the custom index.

        description (EntityDescriptionField): The description of the custom index.
        name (EntityNameField): The name of the custom index.
        tags (EntityTagsField): The tags of the custom index.

        created_on (DateTimeField): The creation date of the custom index.
        updated_on (DateTimeField): The last update date of the custom index.
        version (IntField): The version of the custom index.

    Example:
        >>> from everysk.sdk.entities.custom_index.base import CustomIndex
        >>> custom_index = CustomIndex(
            symbol='CUSTOM:INDEX',
            data=[...],
            periodicity='M',
            data_type='PRICE',
            currency='USD',
            base_price=100,
            description='Custom index description',
            name='Custom index name',
            tags=['tag1', 'tag2']
        )
        >>> custom_index.save()
    """

    script: Script
    _orderable_attributes = ListField(default=['created_on', 'updated_on', 'name'], readonly=True)

    symbol = StrField(regex=settings.CUSTOM_INDEX_SYMBOL_REGEX, min_size=settings.CUSTOM_INDEX_SYMBOL_MIN_SIZE, max_size=settings.CUSTOM_INDEX_SYMBOL_MAX_SIZE, required_lazy=True, empty_is_none=True)

    data = ListField(min_size=settings.CUSTOM_INDEX_MIN_DATA_BLOB, required_lazy=True)

    periodicity = ChoiceField(default=None, choices=(settings.CUSTOM_INDEX_PERIODICITY_MONTHLY, settings.CUSTOM_INDEX_PERIODICITY_DAILY, None), required_lazy=True)
    data_type = ChoiceField(default=None, choices=(settings.CUSTOM_INDEX_DATA_TYPE_PRICE, settings.CUSTOM_INDEX_DATA_TYPE_RETURN, settings.CUSTOM_INDEX_DATA_TYPE_RETURN_100, None), required_lazy=True)
    currency = CurrencyField()
    base_price = FloatField(min_size=settings.CUSTOM_INDEX_BASE_PRICE_MIN_VAL, max_size=settings.CUSTOM_INDEX_BASE_PRICE_MAX_VAL)

    description = EntityDescriptionField()
    name = EntityNameField()
    tags = EntityTagsField()

    @property
    def id(self) -> str:
        """
        Returns the id of the custom index. The id is a alias for the symbol.

        Returns:
            str: The id of the custom index.

        Example:
            >>> custom_index = CustomIndex(symbol='CUSTOM:INDEX')
            >>> custom_index.id
            'CUSTOM:INDEX'
        """
        return self.symbol

    @id.setter
    def id(self, value: str) -> None:
        """
        Sets the id of the custom index. The id is a alias for the symbol.

        Args:
            value (str): The id of the custom index.

        Example:
            >>> custom_index = CustomIndex()
            >>> custom_index.id = 'CUSTOM:INDEX'
            >>> custom_index.symbol
            'CUSTOM:INDEX'
            >>> custom_index.id
            'CUSTOM:INDEX'
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
            >>> custom_index = CustomIndex(symbol='CUSTOM:INDEX', name='Custom index name', ...)
            >>> custom_index.validate()
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
        Returns the prefix of the custom index id field value.

        Returns:
            str: The prefix of the custom index id field value.

        Example:
            >>> from everysk.sdk.custom_index.base import CustomIndex
            >>> CustomIndex.get_id_prefix()
            'CUSTOM:'
        """
        return settings.CUSTOM_INDEX_SYMBOL_PREFIX

    @classmethod
    def modify_many(cls, entity_id_list: list[str], overwrites: dict | list[dict]) -> list:
        """
        The custom index does not support the modify_many method.
        """
        raise NotImplementedError()

    @classmethod
    def clone_many(cls, entity_id_list: list[str], overwrites: dict | list[dict]) -> list:
        """
        The custom index does not support the clone_many method.
        """
        raise NotImplementedError()
