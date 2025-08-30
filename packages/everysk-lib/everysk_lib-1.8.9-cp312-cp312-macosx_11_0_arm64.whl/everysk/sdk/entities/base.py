###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Self, Any

from everysk.config import settings
from everysk.core.datetime import DateTime, Date
from everysk.core.exceptions import SDKValueError, FieldValueError
from everysk.core.fields import StrField, DateTimeField, ListField
from everysk.core.object import MetaClass as ObjMetaClass, BaseDictConfig
from everysk.core.string import is_string_object
from everysk.core.lists import split_in_slices
from everysk.sdk.base import BaseSDK, BaseDict
from everysk.sdk.engines.cryptography import generate_random_id
from everysk.sdk.entities.query import Query
from everysk.sdk.entities.script import Script
from everysk.sdk.entities.tags import Tags


###############################################################################
#   QueryMetaClass Class Implementation
###############################################################################
class QueryMetaClass(ObjMetaClass):
    """
    Metaclass for the Query class that allows for the query attribute to be accessed
    directly from the entity class.

    Example:
        To access the query attribute from the entity class:
        >>> MyClass.query
        Query()
    """
    def __getattribute__(cls, __name: str) -> Any:
        """
        Get the query attribute from the entity class.
        """
        if __name == 'query':
            return Query(cls)
        return super().__getattribute__(__name)


###############################################################################
#   ScriptMetaClass Class Implementation
###############################################################################
class ScriptMetaClass(QueryMetaClass):
    """
    Metaclass for the Script class that allows for the script attribute to be accessed
    directly from the entity class.

    Example:
        To access the script attribute from the entity class:
        >>> MyClass.script
        Script()

    Notes:
        This metaclass overrides the __getatrribute__ method to enable direct access
    """
    def __getattribute__(cls, __name: str) -> Any:
        """
        Get the script attribute from the entity class.
        """
        if __name == 'script':
            return Script(cls)
        return super().__getattribute__(__name)


###############################################################################
#   BaseEntityConfig Class Implementation
###############################################################################
class BaseEntityConfig(BaseDictConfig):
    exclude_keys: frozenset[str] = frozenset(['query', 'script', '_is_frozen', '_silent', '_errors', '_orderable_attributes'])
    keys_blacklist: frozenset[str] = frozenset(['query', 'script'])


###############################################################################
#   BaseEntity Class Implementation
###############################################################################
class BaseEntity(BaseSDK, BaseDict, metaclass=QueryMetaClass):
    """
    Base class for all entities in the SDK library that provides common functionality. This class
    should not be instantiated directly, but rather should be subclassed by other entity classes.

    Attributes:
        id (str): The unique identifier of the entity.
        version (str): The version of the entity.
        created_on (DateTime): The date and time the entity was created.
        updated_on (DateTime): The date and time the entity was last updated.

    Example:
        To create a new entity:
        >>> my_entity = MyEntity(id="my_id", workspace="my_workspace", name="my_name", description="my_description")
    """
    class Config(BaseEntityConfig):
        pass

    _config: Config = None
    _orderable_attributes = ListField(default=['id', 'created_on', 'updated_on'], readonly=True)
    _allowed_query_attributes_for_all_operators = ListField(default=settings.ENTITY_ALLOWED_QUERY_ATTRIBUTES_FOR_ALL_OPERATORS, readonly=True)

    id = StrField(default=None)

    query: Query = None

    created_on = DateTimeField(default=Undefined, empty_is_none=True, required_lazy=True)
    updated_on = DateTimeField(default=Undefined, empty_is_none=True, required_lazy=True)

    version = StrField(default=settings.ENTITY_DEFAULT_VERSION, required_lazy=True)

    def __after_init__(self) -> None:
        """
        Method that runs after the __init__ method.
        This method must return None.
        """
        super().__after_init__()
        if self.created_on is Undefined:
            self.created_on = DateTime.now()
        if self.updated_on is Undefined:
            self.updated_on = self.created_on

    def _process_date(self, value: DateTime | None) -> str | None:
        """
        Process the date value.

        Args:
            value (DateTime): The date value to process.

        Returns:
            str: The processed date value.
        """
        return Date.strftime_or_null(value)

    def _process_tags(self, value: Tags | None) -> list | None:
        """
        Convert the entity to a JSON-serializable dictionary.
        This method converts the entity object into a dictionary that can be easily
        serialized to JSON.

        Args:
            value (Tags): The tags value to process.

        Returns:
            list: The processed tags value.
        """
        return value.to_list() if isinstance(value, Tags) else value

    def to_dict(self, add_class_path: bool = False, recursion: bool = False) -> dict:
        """
        This method is used to convert the object to a dictionary.
        """
        dct: dict = super().to_dict(add_class_path=add_class_path, recursion=recursion)

        if add_class_path is False:
            if 'date' in self:
                dct['date_time'] = DateTime.strftime_or_null(self.date) # pylint: disable=no-member

            if 'created_on' in self:
                dct.pop('created_on')
                dct['created'] = self.created_on.timestamp() if self.created_on is not None else None

            if 'updated_on' in self:
                dct.pop('updated_on')
                dct['updated'] = self.updated_on.timestamp() if self.updated_on is not None else None

        dct.pop('query', None)
        dct.pop('script', None)

        return dct

    @staticmethod
    def get_id_prefix() -> str:
        """
        Get the prefix for the unique identifier for this entity.

        Returns:
            str: The prefix for the unique identifier.

        Raises:
            NotImplementedError: This method should be overridden in subclasses.
        """
        raise NotImplementedError()

    def generate_id(self) -> str:
        """
        Generate a unique ID for an entity instance.

        Returns:
            str: The generated unique ID.

        Example:
            To generate a unique ID for an entity instance:
            >>> unique_id = MyEntity().generate_id()
        """
        prefix: str = self.get_id_prefix()
        unique_id: str = generate_random_id(length=settings.ENTITY_ID_LENGTH)
        return f'{prefix}{unique_id}'

    @classmethod
    def validate_id(cls, entity_id: str) -> bool:
        """
        Validate an entity's ID.

        Args:
            entity_id str: The ID to be validated.

        Returns:
            bool: True if the ID is valid, False otherwise.

        Example:
            To validate an entity's ID:
            >>> is_valid = MyEntity.validate_id(my_id)
        """
        if entity_id:
            try:
                cls(id=entity_id)
                return True
            except Exception: # pylint: disable=broad-exception-caught
                pass
        return False

    def validate(self) -> bool:
        """
        Validate the entity's attributes.

        This method performs validation checks on the entity's attributes to ensure they meet
        the required criteria. If all required fields are present, the validation is considered
        successful and the method returns True. If any required field is missing, it raises a
        RequiredFieldError exception.

        Args:
            self (Self): The entity instance to validate.

        Returns:
            bool: True if the validation is successful.

        Raises:
            RequiredFieldError: If any required field is missing.

        Example:
            To validate an entity:

            >>> is_valid = my_entity.validate()
            >>> if is_valid:
            >>>     # Handle the valid entity
            >>> else:
            >>>     # Handle the invalid entity
        """
        self.validate_required_fields()
        return True

    def _pre_validate(self) -> None:
        self.id = self.generate_id() # pylint: disable=attribute-defined-outside-init

    def _pos_validate(self) -> None:
        self.id = None # pylint: disable=attribute-defined-outside-init
        self.created_on = None
        self.updated_on = None

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
        # Set the entity properties
        entity = cls(**entity_dict)
        entity._pre_validate()
        entity.validate()
        entity._pos_validate()

        return entity

    @classmethod
    def check(cls, entity_dict: dict) -> Self:
        """
        Check the entity properties.

        Args:
            entity_dict (dict): The entity properties.

        Returns:
            BaseEntity: The entity object.

        Raises:
            FieldValueError: If the entity properties are invalid.
            RequiredFieldError: If a required field is missing.
        """
        entity: Self = cls(**entity_dict)
        entity.validate()
        return entity

    def _check_query(self, query: Query) -> bool:
        """
        Check the query object.

        Args:
            query (Query): The query object.

        Returns:
            bool: True if the query object is valid.
        """
        # pylint: disable=no-member
        if self.name and 'date' in query.order:
            raise SDKValueError("Can't filter by Name and Date at the same time,  must order by updated_on")

        return True

    def _check_entity_to_query(self) -> bool:
        """
        Check the entity object to query.

        Returns:
            bool: True if the entity object is valid.
        """
        # pylint: disable=no-member
        if self.name and self.tags:
            raise SDKValueError("Can't filter by Name and Tags at the same time")
        if self.name and self.link_uid:
            raise SDKValueError("Can't filter by Name and Link UID at the same time")

        return True

    def _mount_query(self, query: Query) -> Query:
        """
        Mount the query object.

        Args:
            query (Query): The query object.

        Returns:
            Query: The query object.
        """
        # pylint: disable=no-member
        if self.workspace is not None:
            query = query.where('workspace', self.workspace)
        if self.link_uid is not None:
            query = query.where('link_uid', self.link_uid)
        if self.name is not None:
            query = query.where('name', self.name)
        if self.date is not None:
            query = query.where('date', self.date)
        if self.tags:
            query = query.where('tags', self.tags)

        return query

    def to_query(self, order: list | None = None, projection: list | None = None, distinct_on: list | None = None,
                 limit: int | None = None, offset: int | None = None, page_size: int | None = None, page_token: str | None = None) -> Query:
        """
        This method converts the entity object into a query object.

        Args:
            order (List[str], optional): The order to apply to the query. Defaults to None.
            projection (List[str], optional): The projection to apply to the query. Defaults to None.
            distinct_on (List[str], optional): The distinct_on to apply to the query. Defaults to None.
            limit (int, optional): The limit to apply to the query. Defaults to None.
            offset (int, optional): The offset to apply to the query. Defaults to None.
            page_size (int, optional): The page size to apply to the query. Defaults to None.
            page_token (str, optional): The page token to apply to the query. Defaults to None.

        Returns:
            Query: A query object representing the entity.

        Example:
            To convert an entity object into a query object:
            >>> entity = MyClass(property1="value1", property2="value2")
            >>> query = entity.to_query(order=['property1'], limit=10)
        """
        self._check_entity_to_query()

        query: Query = Query(
            self.__class__,
            order=order,
            projection=projection,
            distinct_on=distinct_on,
            limit=limit,
            offset=offset,
            page_size=page_size,
            page_token=page_token
        )

        self._check_query(query)
        return self._mount_query(query)

    @classmethod
    def _normalize_projection(cls, projection: str | list[str]) -> list[str]:
        """
        Validate the projection attributes for the query and return the instance.

        This method validate the desired properties that should be returned in entity.
        The properties can either be set to include (using the property name) or to exclude
        (prefixing the property name with '-'). Both inclusion and exclusion should not be set
        in the same projection.

        Args:
            - projection (Union[List, str]): A property name as a string or a list of property names
            indicating which properties to include or exclude in the entity.

        Returns:
            - Query: The instance of the current object.

        Raises:
            - ValueError: If both projection and inverse projection are set in the same projection or
            if the projection properties do not belong to the entity kind.

        Example:
            To create a projection with a projection condition:
            >>> projection = self._validate_projection('property_name')

            To create a query with an inverse projection condition:
            >>> projection = self._validate_projection('-property_name')

            To create a query with a projection condition using a list:
            >>> projection = self._validate_projection(['property_name_1', 'property_name_2'])
        """
        if projection is None:
            return []

        if is_string_object(projection):
            projection = [projection]

        count: int = sum(property_name.startswith('-') for property_name in projection)
        if not (count == 0 or count == len(projection)):
            raise ValueError('Projection and Inverse Projection should not be set in the same query')

        entity_properties: set = set(cls.__attributes__.keys()) # pylint: disable=protected-access
        projection_properties: set = set([property_name.replace('-', '') for property_name in projection])
        difference: set = projection_properties.difference(entity_properties)

        if difference:
            difference_: str = ', '.join(difference)
            raise ValueError(f'Projection properties does not belongs to {cls.__name__}: {difference_}')

        return projection

    @classmethod
    def retrieve(cls, entity_id: str, projection: list | str | None = None) -> Self | None:
        """
        Retrieve an entity by its ID.

        Args:
            entity_id (str): The unique identifier of the entity to retrieve.
            projection (Union[List, str], optional): A property name as a string or a list of property names

        Returns:
            Self: An instance of the class representing the retrieved entity.
            None: If not found

        Example:
            To retrieve an entity by its ID:

            >>> entity = MyClass.retrieve("entity_id_here")
            >>> if entity:
            >>>    # Handle the retrieved entity
            >>> else:
            >>>    # Entity not found
        """
        if projection is not None:
            projection = cls._normalize_projection(projection)

        entity_dict: dict | None = cls.get_response(
            params={'entity_id': entity_id, 'projection': projection})

        if entity_dict is None:
            return None

        return cls(**entity_dict)

    @classmethod
    def create(cls, entity_dict: dict) -> Self:
        """
        Create a new entity using provided attributes from a dictionary.

        Args:
            entity_dict (dict): A dictionary representing the entity's attributes.

        Returns:
            Self: An instance of the class representing the newly created entity.

        Example:
            To create a new entity with attributes from a dictionary and optional keyword arguments:

            >>> entity_data = {'property1': value1, 'property2': value2}
            >>> new_entity = MyClass.create(entity_data)
        """
        entity_dict_: dict = cls.get_response(params={'entity_dict': entity_dict})

        return cls(**entity_dict_)

    @classmethod
    def modify(cls, entity_id: str, overwrites: dict) -> Self | None:
        """
        Modify an existing entity by updating its attributes using the provided overwrites.

        Args:
            entity_id (str): The unique identifier of the entity to modify.
            overwrites (dict): A dictionary containing attribute updates to apply to the entity.

        Returns:
            Self: An instance of the class representing the modified entity.
            None: If not found

        Example:
            To modify an existing entity by updating its attributes with overwrites:

            >>> entity_id_to_modify = "entity_id_here"
            >>> attribute_updates = {'property1': new_value1, 'property2': new_value2}
            >>> modified_entity = MyClass.modify(entity_id_to_modify, attribute_updates)
        """
        entity_dict: dict | None = cls.get_response(params={'entity_id': entity_id, 'overwrites': overwrites})

        if entity_dict is None:
            return None

        return cls(**entity_dict)

    @classmethod
    def remove(cls, entity_id: str) -> Self | None:
        """
        Remove an entity by its unique identifier.

        Args:
            entity_id (str): The unique identifier of the entity to remove.

        Returns:
            Self: An instance of the class representing the removed entity.
            None: If not found

        Example:
            To remove an entity by its unique identifier:

            removed_entity = MyClass.remove("entity_id_here")
            >>> if removed_entity:
            >>>     # Handle the removed entity
            >>> else:
            >>>     # Entity not found
        """
        entity_dict: dict | None = cls.get_response(params={'entity_id': entity_id})

        if entity_dict is None:
            return None

        return cls(**entity_dict)

    @classmethod
    def clone(cls, entity_id: str, overwrites: dict) -> Self | None:
        """
        Clone an existing entity by creating a new one based on provided overwrites.

        Args:
            entity_id (str): The unique identifier of the entity to clone.
            overwrites (dict): A dictionary containing attribute updates to apply to the new cloned entity.

        Returns:
            Self: An instance of the class representing the newly cloned entity.
            None: If not found.

        Example:
            To clone an existing entity by creating a new one with attribute overwrites and optional keyword arguments:

            >>> entity_id_to_clone = "entity_id_here"
            >>> attribute_overwrites = {'property1': new_value1, 'property2': new_value2}
            >>> cloned_entity = MyClass.clone(entity_id_to_clone, attribute_overwrites)
        """
        entity_dict: dict | None = cls.get_response(params={'entity_id': entity_id, 'overwrites': overwrites})

        if entity_dict is None:
            return None

        return cls(**entity_dict)

    @classmethod
    def retrieve_many(cls, entity_id_list: list[str], projection: str | list[str] | None = None) -> list[Self | None]:
        """
        Retrieve multiple entities by their unique identifiers.

        Args:
            entity_id_list (List[str]): A list of unique identifiers for the entities to retrieve.
            projection (Union[List, str], optional): A property name as a string or a list of property names.

        Returns:
            List[Self | None]: A list of instances of the class representing the retrieved entities, or None for entities not found.

        Example:
            To retrieve multiple entities by their unique identifiers:

            >>> entity_ids_to_retrieve = ["entity_id1", "entity_id2"]
            >>> retrieved_entities = MyClass.retrieve_many(entity_ids_to_retrieve)
        """
        if not isinstance(entity_id_list, list):
            raise FieldValueError(f"The argument 'entity_id_list' most be a instance of 'list' and not {type(entity_id_list)}.")

        if projection is not None:
            projection = cls._normalize_projection(projection)

        chunks: list[slice] = split_in_slices(len(entity_id_list), settings.ENTITY_RETRIEVE_BATCH_SIZE)
        entities: list[Self | None] = []
        for chunk in chunks:
            entities.extend(cls.inner_retrieve_many(entity_id_list[chunk], projection))

        return entities

    @classmethod
    def inner_retrieve_many(cls, entity_id_list: list[str], projection: str | list[str] | None = None) -> list[Self | None]:
        """
        Retrieve multiple entities by their unique identifiers.

        Args:
            entity_id_list (List[str]): A list of unique identifiers for the entities to retrieve.
            projection (Union[List, str], optional): A property name as a string or a list of property names.

        Returns:
            List[Self | None]: A list of instances of the class representing the retrieved entities, or None for entities not found.
        """

        entities: list[dict | None] = cls.get_response(params={'entity_id_list': entity_id_list, 'projection': projection})

        return [cls(**entity_dict) if entity_dict is not None else None for entity_dict in entities]

    @classmethod
    def create_many(cls, entity_dict_list: list[dict]) -> list[Self | None]:
        """
        Create multiple new entities using provided dictionaries..

        Args:
            entity_dict_list (List[dict]): A list of dictionaries, each representing an entity's attributes.

        Returns:
            List[Self | None]: A list of instances of the class representing the newly created entities, or None for entities not found.

        Example:
            To create multiple entities using a list of dictionaries:

            >>> entity_data_list = [{'property1': value1}, {'property2': value2}]
            >>> created_entities = MyClass.create_many(entity_data_list)
        """
        entities: list[dict | None] = cls.get_response(params={'entity_dict_list': entity_dict_list})

        return [cls(**entity_dict) if entity_dict is not None else None for entity_dict in entities]

    @classmethod
    def modify_many(cls, entity_id_list: list[str], overwrites: dict | list[dict]) -> list[Self | None]:
        """
        Modify multiple existing entities by updating their attributes using the provided overwrites.

        Args:
            entity_id_list (List[str]): A list of unique identifiers for the entities to modify.
            overwrites (Union[dict, List[dict]]): A dictionary or a list of dictionaries containing attribute updates
                to apply to the entities.

        Returns:
            List[Self | None]: A list of instances of the class representing the modified entities, or None for entities not found.

        Example:
            To modify multiple existing entities by updating their attributes with overwrites:

            >>> entity_ids_to_modify = ["entity_id1", "entity_id2"]
            >>> attribute_overwrites = [{'property1': new_value1}, {'property2': new_value2}]
            >>> modified_entities = MyClass.modify_many(entity_ids_to_modify, attribute_overwrites)
        """
        entities: list[dict | None] = cls.get_response(params={'entity_id_list': entity_id_list, 'overwrites': overwrites})

        return [cls(**entity_dict) if entity_dict is not None else None for entity_dict in entities]

    @classmethod
    def remove_many(cls, entity_id_list: list[str]) -> list[str | None]:
        """
        Remove multiple entities by their unique identifiers.

        Args:
            entity_id_list (List[str]): A list of unique identifiers for the entities to remove.

        Returns:
            List[str | None]: A list of unique identifiers for the removed entities, or None for entities not deleted.

        Example:
            To remove multiple entities by their unique identifiers:

            >>> entity_ids_to_remove = ["entity_id1", "entity_id2"]
            >>> MyClass.remove_many(entity_ids_to_remove)
        """
        return cls.get_response(params={'entity_id_list': entity_id_list})

    @classmethod
    def clone_many(cls, entity_id_list: list[str], overwrites: dict | list[dict]) -> list[Self | None]:
        """
        Clone multiple existing entities by creating new ones based on provided overwrites.

        Args:
            entity_id_list (List[str]): A list of unique identifiers for the entities to clone.
            overwrites (Union[dict, List[dict]]): A dictionary or a list of dictionaries containing attribute updates
                to apply to the new cloned entities.

        Returns:
            List[Self | None]: A list of instances of the class representing the newly copied entities, or None for entities not found.

        Example:
            To clone multiple existing entities by creating new ones with attribute overwrites:

            >>> entity_ids_to_clone = ["entity_id1", "entity_id2"]
            >>> attribute_overwrites = [{'property1': new_value1}, {'property2': new_value2}]
            >>> copied_entities = MyClass.clone_many(entity_ids_to_clone, attribute_overwrites)
        """
        entities: list[dict | None] = cls.get_response(params={'entity_id_list': entity_id_list, 'overwrites': overwrites})

        return [cls(**entity_dict) if entity_dict is not None else None for entity_dict in entities]

    def load(self, offset: int = None) -> Self | None:
        """
        Load an entity from the database and return it as an instance of the class.

        Args:
            self (Self): The entity instance to load.
            offset (int, optional): The offset to use for pagination. Defaults to None.

        Returns:
            Self: An instance of the class representing the loaded entity.
            None: If not found.

        Example:
            >>> entity_to_load = MyClass(property1="value1", property2="value2")
            >>> loaded_entity = entity_to_load.load()
        """
        # pylint: disable=no-member
        if self.id:
            return type(self).retrieve(self.id)

        query = self.to_query()
        return query.load(offset=offset)

    def save(self) -> Self:
        """
        Save the entity to the database and return the saved entity as an instance of the class.

        Args:
            self (Self): The entity instance to save.

        Returns:
            Self: An instance of the class representing the saved entity.

        Example:
            To save an entity:

            >>> entity_to_save = MyClass(id="entity_id_here", property1="value1", property2="value2")
            >>> saved_entity = entity_to_save.save()
        """
        entity_dict: dict = self.get_response(self_obj=self)

        return self.__class__(**entity_dict)

    def delete(self) -> Self | None:
        """
        Delete the entity from the database and return the deleted entity as an instance of the class.

        Returns:
            Self: An instance of the class representing the deleted entity.
            None: If not found.

        Example:
            To delete an entity:

            >>> entity_to_delete = MyClass(id="entity_id_here")
            >>> deleted_entity = entity_to_delete.delete()
        """
        entity_dict: dict | None = self.get_response(self_obj=self)

        if entity_dict is None:
            return None

        return self.__class__(**entity_dict)
