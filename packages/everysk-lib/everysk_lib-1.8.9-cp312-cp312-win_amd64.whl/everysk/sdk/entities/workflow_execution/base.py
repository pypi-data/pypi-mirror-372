###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.config import settings
from everysk.core.fields import StrField, DateTimeField, ListField, FloatField
from everysk.sdk.entities.base import BaseEntity
from everysk.sdk.entities.query import Query


###############################################################################
#   WorkflowExecution Class Implementation
###############################################################################
class WorkflowExecution(BaseEntity):

    id = StrField(regex=settings.WORKFLOW_EXECUTION_ID_REGEX, required_lazy=True, empty_is_none=True)

    # This is a legacy status used in the old version of the API library.
    status = StrField(default=settings.WORKFLOW_EXECUTION_STATUS_OK, choices=settings.WORKFLOW_EXECUTION_STATUS, required_lazy=True)
    run_status = StrField(default=settings.WORKFLOW_EXECUTION_STATUS_PREPARING, choices=settings.WORKFLOW_EXECUTION_STATUS, required_lazy=True)

    execution_type = StrField(default=Undefined, choices=settings.WORKER_EXECUTION_TYPE_LIST, required_lazy=True)
    start_time = DateTimeField()
    end_time = DateTimeField()
    duration = FloatField()
    real_execution_time = FloatField()
    total_execution_time = FloatField()

    workflow_id = StrField(regex=settings.WORKFLOW_ID_REGEX, required_lazy=True, empty_is_none=True)
    workflow_name = StrField(required_lazy=True)
    workspace = StrField(required_lazy=False, empty_is_none=True)

    started_worker_id = StrField(regex=settings.WORKER_ID_REGEX, required_lazy=True, empty_is_none=True)
    ender_worker_id = StrField(regex=settings.WORKER_ID_REGEX, empty_is_none=True)
    ender_worker_execution_id = StrField(regex=settings.WORKER_EXECUTION_ID_REGEX, empty_is_none=True)

    worker_ids = ListField()
    resume = ListField()

    @staticmethod
    def get_id_prefix() -> str:
        """
        Returns the prefix of the Worker Execution id field value.

        Returns:
            str: The prefix of the Worker Execution id field value.

        Usage:
            >>> WorkflowExecution.get_id_prefix()
            'wfex_'

        Notes:
            The prefix is typically used to distinguish Worker Execution IDs from other types of IDs.
        """
        return settings.WORKFLOW_EXECUTION_ID_PREFIX

    def to_dict(self, add_class_path: bool = False, recursion: bool = False) -> dict:
        """
        This method is used to convert the object to a dictionary.
        """
        dct: dict = super().to_dict(add_class_path=add_class_path, recursion=recursion)

        if add_class_path is False:
            dct['started'] = self.start_time.timestamp() if self.start_time else None
            dct['trigger'] = self.execution_type

            dct.pop('worker_ids')
            dct.pop('execution_type')
            dct.pop('start_time')
            dct.pop('end_time')

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
        if self.workflow_id is not None:
            query = query.where('workflow_id', self.workflow_id)

        return query
