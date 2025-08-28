###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any, Callable, TypedDict
from inspect import isclass

from everysk.config import settings
from everysk.core.exceptions import FieldValueError, InvalidArgumentError
from everysk.core.object import BaseDict, BaseDictConfig
from everysk.core.string import import_from_string
from everysk.sdk.base import BaseSDK


###############################################################################
#   StorageSettings Class Implementation
###############################################################################
class StorageSettings(TypedDict):
    storage_mode: str
    consistency_check: bool
    skip_validation: bool
    create_fallback: bool


###############################################################################
#   Script Class Implementation
###############################################################################
class Script(BaseDict, BaseSDK):
    """
    A base class for scripted queries.
    This class provides a base implementation for scripted queries.

    Attributes:
        - _klass (callable): The class to instantiate when fetching an entity.

    Example:
        To fetch an entity:
        >>> script = Script(klass=MyEntity)
        >>> entity = script.fetch(user_input, variant, workspace)
    """
    class Config(BaseDictConfig):
        exclude_keys: frozenset[str] = frozenset(['_is_frozen', '_silent', '_errors', '_orderable_attributes'])

    _klass: Callable = None
    _config: Config = None

    def __init__(self, _klass: Callable) -> None:
        super().__init__(_klass=None)

        if _klass is not None and not isclass(_klass):
            try:
                _klass = import_from_string(settings.EVERYSK_SDK_ENTITIES_MODULES_PATH[_klass])
            except KeyError:
                raise FieldValueError(f"The _klass value '{_klass}' must be a class or a string with the class name.") from KeyError

        self._klass = _klass

    def _process__klass(self, value: Any) -> Any:
        """
        This method is used to process the '_klass' attribute.
        """
        return value.__name__

    def _process_entity_output(self, user_input: Any) -> Any:
        """
        Processes the user input and returns an instance of the class or the input itself.

        If the `user_input` is a dictionary or an instance of `BaseDict`, it will be passed as keyword arguments
        to the class constructor (`self._klass`) and an instance of that class will be returned. Otherwise,
        the `user_input` is returned as-is.

        Args:
            user_input (Any): The input data to be processed. This can be a dictionary, an instance of `BaseDict`,
                            or any other type.

        Returns:
            Any: An instance of the class if `user_input` is a dictionary or `BaseDict`; otherwise, the `user_input`
                itself is returned.
        """
        return self._klass(**user_input) if isinstance(user_input, (dict, BaseDict)) else user_input # pylint: disable=not-callable

    def inner_fetch(self, user_input: Any, variant: str, workspace: str = Undefined) -> Any:
        """
        Makes a call to the client to fetch an entity based on user input, variant, and workspace.

        Args:
            user_input (Any): The input provided by the user, which can be used for filtering or as a direct entity ID.
            variant (str): The type of scripted query to execute. Determines how the method processes the user input and constructs the query. Supported variants include 'previousWorkers', 'tagLatest', any string starting with 'select', and potentially others.
            workspace (str): The workspace context for the query. Used for scoping and verifying entity retrieval.

        Returns:
            Any: Depending on the variant and user input, the method might return an entity, or None.

        """
        response = self.get_response(self_obj=self, params={'user_input': user_input, 'variant': variant, 'workspace': workspace})

        return self._process_entity_output(response)

    def fetch(self, user_input: Any, variant: str, workspace: str = Undefined) -> Any:
        """
        Fetches an entity based on user input, variant, and workspace.

        This method provides a way to construct and execute different types of queries
        based on the specified variant. It's designed to handle a variety of scenarios
        and return the desired entity or entities based on the input parameters.

        Args:
            - user_input (Any): The input provided by the user, which can be used for filtering
            or as a direct entity ID.
            - variant (str): The type of scripted query to execute. Determines how the method
            processes the user input and constructs the query. Supported variants include
            'previousWorkers', 'tagLatest', any string starting with 'select', and potentially
            others.
            - workspace (str): The workspace context for the query. Used for scoping and
            verifying entity retrieval.

        Returns:
            - Any: Depending on the variant and user input, the method might return an entity,
            or None.

        Raises:
            - ValueError: If there's an attempted cross-workspace operation or other variant-specific
            error conditions are met.

        Note:
            The method behavior can vary greatly depending on the `variant` parameter, and it's
            important to ensure that the variant aligns with the expected user input structure.

        """
        if not user_input:
            return None

        if variant == 'previousWorkers' and isinstance(user_input, (dict, BaseDict, self._klass)) and (user_input.get('is_transient') or user_input.get('id') is None):
            return self._process_entity_output(user_input)

        entity: Any = self.inner_fetch(user_input, variant, workspace)

        return entity

    def inner_fetch_list(self, user_input: Any, variant: str, workspace: str = Undefined) -> list:
        """
        Fetches a list of entities based on user input, variant, and workspace.

        This method makes a call to the client to perform the necessary query actions.

        Args:
            user_input (Any): The input provided by the user, which can be used for filtering or as a direct entity ID.
            variant (str): The type of scripted query to execute.
            workspace (str): The workspace context for the query.

        Returns:
            list: The list of entities retrieved based on the input parameters.

        """
        return self.get_response(self_obj=self, params={'user_input': user_input, 'variant': variant, 'workspace': workspace})


    def fetch_list(self, user_input: Any, variant: str, workspace: str = Undefined) -> list:
        """
        Fetches an entity based on user input, variant, and workspace.

        This method provides a way to construct and execute different types of queries
        based on the specified variant. It's designed to handle a variety of scenarios
        and return the desired entity or entities based on the input parameters.

        Args:
            user_input (Any): The input provided by the user, which can be used for filtering or as a direct entity ID.
            variant (str): The type of scripted query to execute. Determines how the method processes the user input and constructs the query. Supported variants include 'previousWorkers', 'tagLatest', any string starting with 'select', and potentially others.
            workspace (str): The workspace context for the query. Used for scoping and verifying entity retrieval.

        Returns:
            list: The method will return a list of entities or an empty list.

        Raises:
            ValueError: If there's an attempted cross-workspace operation or other variant-specific error conditions are met.

        Note:
            The method behavior can vary greatly depending on the `variant` parameter, and it's important to ensure that the variant aligns with the expected user input structure.

        """
        if not user_input:
            return []

        entity_list: list = self.inner_fetch_list(user_input, variant, workspace)

        return [self._klass(**item) if item is not None else item for item in entity_list] # pylint: disable=not-callable

    def inner_fetch_multi(self, user_input_list: list[Any], variant_list: list[str], workspace_list: list[str] = Undefined) -> list:
        """
        Fetches a list of entities based on user inputs, query variants, and workspace contexts.

        This method sends a request to the client to execute the necessary query actions,
        dynamically constructed based on the provided parameters.

        Args:
            user_input_list (list[Any]): A list of inputs provided by the user.
            variant_list (list[str]): A list of query variants, each specifying the type of query to execute.
            workspace_list (list[str], optional): A list of workspace contexts, used for scoping and validating
                entity retrieval. Defaults to `Undefined`.

        Returns:
            list: A list of entities retrieved based on the provided parameters. Returns an empty list
            if no entities match the query.
        """
        return self.get_response(self_obj=self, params={'user_input_list': user_input_list, 'variant_list': variant_list, 'workspace_list': workspace_list})


    def fetch_multi(self, user_input_list: list[Any], variant_list: list[str], workspace_list: list[str] = Undefined) -> list:
        """
        Fetches entities based on user inputs, query variants, and workspace contexts.

        This method provides a higher-level interface for constructing and executing different
        types of queries, delegating the core functionality to `inner_fetch_multi`.

        Args:
            user_input_list (list[Any]): A list of inputs provided by the user.
            variant_list (list[str]): A list of query variants, each specifying the type of query to execute.
            workspace_list (list[str], optional): A list of workspace contexts, used for scoping and validating
                entity retrieval. Defaults to `Undefined`.

        Returns:
            list: A list of entities processed and instantiated using the class constructor (`self._klass`).
            Returns an empty list if no entities match the query.
        """
        if not user_input_list:
            return []

        entity_list: list = self.inner_fetch_multi(user_input_list, variant_list, workspace_list)

        return [self._klass(**item) for item in entity_list] # pylint: disable=not-callable

    def persist(self, entity: Any, persist: str, consistency_check: bool = False) -> Any:
        """
        This method provides a way to persist an entity based on the specified persist type.

        Args:
            - entity (Any): The entity to persist.
            - persist (str): The type of persist to execute. Determines how the method
            persists the entity. Supported persists include 'insert', 'update', and 'delete'.
            - consistency_check (bool): A flag to enable consistency checks before persisting.

        Returns:
            - Any: Depending on the persist type, the method might return an entity.

        """
        response = self.get_response(self_obj=self, params={'entity': entity, 'persist': persist, 'consistency_check': consistency_check})

        if isinstance(response, dict):
            response = self._klass(**response) # pylint: disable=not-callable

        return response

    def inner_storage(self, entity: Any, storage_settings: StorageSettings) -> Any:
        """
        Handles the storage actions for a given entity using specified storage settings.

        This method makes a call to the client to perform the necessary storage actions.

        Args:
            entity (Any): The entity to be stored.
            storage_settings (StorageSettings): The settings and configurations for storage.

        Returns:
            Any: The response from the client after performing the storage actions.

        """
        response = self.get_response(self_obj=self, params={'entity': entity, 'storage_settings': storage_settings})

        return self._process_entity_output(response)


    def storage(self, entity: Any, storage_settings: StorageSettings) -> Any:
        """
        Stores an entity based on the specified storage settings.

        This method determines the appropriate storage actions for an entity, including handling
        different storage modes, performing consistency checks, and optionally skipping validation.

        Args:
            entity (Any): The entity to be stored.
            storage_settings (StorageSettings): A configuration object containing:
                - storage_mode (str): The storage mode to use. Supported modes include 'transient', 'create', and 'update'.
                - consistency_check (bool): A flag indicating whether to perform a consistency check.
                - validate (bool): A flag indicating whether to validate the entity parameters or not.
                - create_fallback (bool): A flag indicating whether to create an entity if it does not exist.

        Returns:
            Any: Depending on the storage mode, the method might return the stored entity or a list of entities.

        Raises:
            InvalidArgumentError: If the entity is empty.

        """
        if not entity:
            raise InvalidArgumentError('Entity should not be empty.')

        if storage_settings['storage_mode'] == 'transient':
            entity.is_transient = True

            if not storage_settings['validate']:
                return self._process_entity_output(entity)

        entity: Any = self.inner_storage(entity, storage_settings)

        return entity
