###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any, Self

from everysk.config import settings
from everysk.core.datetime import DateTime
from everysk.core.fields import BoolField, DateTimeField, DictField, FloatField, IntField, ListField, StrField
from everysk.core.object import BaseDict
from everysk.sdk.entities.base import BaseEntity
from everysk.sdk.entities.query import Query


###############################################################################
#   Result Class Implementation
###############################################################################
class Result(BaseDict):
    status = StrField(default='ERROR', choices=('OK', 'ERROR', 'UNKNOW'))
    data: list | dict | None = None
    log = ListField()


###############################################################################
#   ResultField Class Implementation
###############################################################################
class ResultField(DictField):
    attr_type: Result | BaseDict | dict = Result | BaseDict | dict

    def clean_value(self, value: Any) -> Result | None:
        """
        This method cleans the value of the field.

        Args:s
            value (Any): The value to be cleaned.

        Returns:
            Securities: The cleaned value.
        """
        if isinstance(value, dict):
            value = Result(**value)

        return super().clean_value(value)


###############################################################################
#   ParallelInfo Class Implementation
###############################################################################
class ParallelInfo(BaseDict):
    index = IntField(default=settings.WORKER_EXECUTION_UNFORKED_PARALLEL_INDEX, required_lazy=True)
    length = IntField(default=settings.WORKER_EXECUTION_UNFORKED_PARALLEL_LENGTH, required_lazy=True)


###############################################################################
#   ParallelInfoField Class Implementation
###############################################################################
class ParallelInfoField(DictField):
    attr_type: ParallelInfo | BaseDict | dict = ParallelInfo | BaseDict | dict

    def __init__(
        self,
        default: Any = None,
        *,
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = True,
        empty_is_none: bool = False,
        **kwargs,
    ) -> None:
        if default is None:
            default = ParallelInfo()
        super().__init__(
            default=default,
            required=required,
            readonly=readonly,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Result | None:
        """
        This method cleans the value of the field.

        Args:s
            value (Any): The value to be cleaned.

        Returns:
            Securities: The cleaned value.
        """
        if isinstance(value, (dict, BaseDict)):
            value = ParallelInfo(**value)

        return super().clean_value(value)


###############################################################################
#   InputParams Class Implementation
###############################################################################
class InputParams(BaseDict):
    worker_id = StrField(empty_is_none=True)
    workflow_id = StrField(regex=settings.WORKFLOW_ID_REGEX, empty_is_none=True)

    worker_execution_id = StrField(regex=settings.WORKER_EXECUTION_ID_REGEX, empty_is_none=True)
    workflow_execution_id = StrField(regex=settings.WORKFLOW_EXECUTION_ID_REGEX, empty_is_none=True)

    workspace = StrField(empty_is_none=True)
    worker_type = StrField(default=Undefined, choices=settings.WORKER_TEMPLATE_TYPES)
    script_inputs = DictField()
    inputs_info = DictField()
    parallel_info = ParallelInfoField()

    def to_dict(self, add_class_path: bool = False, recursion: bool = False) -> dict:
        """
        This method is used to convert the object to a dictionary.
        """
        dct: dict = super().to_dict(add_class_path=add_class_path, recursion=recursion)

        if isinstance(dct['parallel_info'], ParallelInfo):
            dct['parallel_info'] = dct['parallel_info'].to_dict(add_class_path=add_class_path, recursion=recursion)

        return dct


###############################################################################
#   InputParamsField Class Implementation
###############################################################################
class InputParamsField(DictField):
    attr_type: InputParams | BaseDict | dict = InputParams | BaseDict | dict

    def clean_value(self, value: Any) -> InputParams | None:
        """
        This method cleans the value of the field.

        Args:s
            value (Any): The value to be cleaned.

        Returns:
            Securities: The cleaned value.
        """
        if isinstance(value, dict):
            value = InputParams(**value)

        return super().clean_value(value)


###############################################################################
#   WorkerExecution Class Implementation
###############################################################################
class WorkerExecution(BaseEntity):
    id = StrField(regex=settings.WORKER_EXECUTION_ID_REGEX, required_lazy=True, empty_is_none=True)

    result = ResultField()
    storage = BoolField(default=False)
    input_params = InputParamsField(required_lazy=True)
    storage_input_params = BoolField(default=False)

    parallel_info = ParallelInfoField()
    status = StrField(default=settings.WORKER_EXECUTION_STATUS_PREPARING, choices=settings.WORKER_EXECUTION_STATUS_LIST)
    execution_type = StrField(default=Undefined, choices=settings.WORKER_EXECUTION_TYPE_LIST, required_lazy=True)
    start_time = DateTimeField()
    end_time = DateTimeField()
    duration = FloatField(default=0.0)
    cpu_time = FloatField(default=0.0)
    process_cpu_time = FloatField(default=0.0)

    workflow_execution_id = StrField(regex=settings.WORKFLOW_EXECUTION_ID_REGEX, required_lazy=True, empty_is_none=True)
    workflow_id = StrField(regex=settings.WORKFLOW_ID_REGEX, required_lazy=True, empty_is_none=True)
    workflow_name = StrField(required_lazy=True, empty_is_none=True)
    worker_id = StrField(regex=settings.WORKER_ID_REGEX, required_lazy=True, empty_is_none=True)
    worker_name = StrField(required_lazy=True, empty_is_none=True)
    worker_type = StrField(default=Undefined, choices=settings.WORKER_TEMPLATE_TYPES)

    @staticmethod
    def get_id_prefix() -> str:
        """
        Returns the prefix of the Worker Execution id field value.

        Returns:
            str: The prefix of the Worker Execution id field value.

        Usage:
            >>> WorkerExecution.get_id_prefix()
            'wkex_'

        Notes:
            The prefix is typically used to distinguish Worker Execution IDs from other types of IDs.
        """
        return settings.WORKER_EXECUTION_ID_PREFIX

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

    def to_dict(self, add_class_path: bool = False, recursion: bool = False) -> dict:
        """
        This method is used to convert the object to a dictionary.
        """
        dct: dict = super().to_dict(add_class_path=add_class_path, recursion=recursion)

        if isinstance(dct['parallel_info'], ParallelInfo):
            dct['parallel_info'] = dct['parallel_info'].to_dict(add_class_path=add_class_path, recursion=recursion)

        if isinstance(dct['result'], Result):
            dct['result'] = dct['result'].to_dict(add_class_path=add_class_path, recursion=recursion)

        if isinstance(dct['input_params'], InputParams):
            dct['input_params'] = dct['input_params'].to_dict(add_class_path=add_class_path, recursion=recursion)

        if add_class_path is False:
            if self.duration is None:
                now = DateTime.now()
                start = self.start_time if self.start_time else now
                end = self.end_time if self.end_time else now
                dct['duration'] = (end - start).total_seconds()

            dct['started'] = self.start_time.timestamp() if self.start_time else None
            dct['trigger'] = self.execution_type

            if dct['result'] is not None:
                dct['result'] = dct.get('result', {}).get('data', None)

            dct.pop('execution_type')
            dct.pop('start_time')
            dct.pop('end_time')
            dct.pop('storage')
            dct.pop('storage_input_params')

        return dct

    def _check_entity_to_query(self) -> bool:
        """
        Check the entity object to query.

        Returns:
            bool: True if the entity object is valid.
        """
        return True

    def _check_query(self, query: Query) -> bool:
        """
        Check the query object.

        Args:
            query (Query): The query object.

        Returns:
            bool: True if the query object is valid.
        """
        return True

    def _mount_query(self, query: Query) -> Query:
        """
        Mount the query object.

        Args:
            query (Query): The query object.

        Returns:
            Query: The query object.
        """
        if self.workflow_execution_id is not None:
            query = query.where('workflow_execution_id', self.workflow_execution_id)

        return query

    @classmethod
    def get_input_params(cls, entity_id: str) -> InputParams:
        """
        Get the input_params of a Worker Execution with the given ID.

        Args:
            entity_id (str): The ID of the Worker Execution.

        Returns:
            InputParams: The input_params of the Worker Execution.

        Raises:
            ValueError: If the entity ID is invalid.
            ValueError: If the entity is not found.
        """
        if cls.validate_id(entity_id) is False:
            raise ValueError(f'Invalid Entity ID: {entity_id}')

        entity: Self | None = cls.retrieve(entity_id)

        if entity is None:
            raise ValueError(f'Entity not found. Entity ID: {entity_id}')

        if entity.input_params.worker_execution_id is None:
            entity.input_params.worker_execution_id = entity.id  # pylint: disable=attribute-defined-outside-init

        return entity.input_params
