###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import traceback
from typing import Any
from uuid import uuid4

from google.api_core.exceptions import (
    AlreadyExists,
    DeadlineExceeded,
    ServiceUnavailable,
    TooManyRequests
)
from google.cloud.tasks_v2 import (
    CloudTasksClient,
    CreateTaskRequest,
    HttpMethod,
    PauseQueueRequest,
    ResumeQueueRequest,
    Task,
    Queue
)
from google.protobuf import duration_pb2

from everysk.core.compress import compress, decompress
from everysk.config import settings
from everysk.core.fields import IntField, StrField
from everysk.core.log import Logger
from everysk.core.object import BaseObject
from everysk.core.string import import_from_string


log = Logger('everysk-workers')


###############################################################################
#   BaseGoogle Class Implementation
###############################################################################
class BaseGoogle(BaseObject):
    ## Private attributes
    _gtask: CloudTasksClient = None

    ## Public attributes
    google_task_project = StrField(default=settings.EVERYSK_GOOGLE_CLOUD_PROJECT)
    google_task_location = StrField(default=settings.EVERYSK_GOOGLE_CLOUD_LOCATION)
    worker_id = StrField(required=True)

    @property
    def gtask(self) -> CloudTasksClient:
        # pylint: disable=protected-access
        if self.__class__._gtask is None:
            self.__class__._gtask = CloudTasksClient()

        return self.__class__._gtask


###############################################################################
#   TaskGoogle Class Implementation
###############################################################################
class TaskGoogle(BaseGoogle):
    ## Public attributes
    google_task_name = StrField() # Must be a unique name if None is used, auto create this
    timeout = IntField(default=600, min_size=15, max_size=1800) # https://cloud.google.com/tasks/docs/reference/rest/v2/projects.locations.queues.tasks
    worker_url = StrField(required=True)

    ## Private methods
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # This facilitate to init it over pickle
        self._received_kwargs = kwargs
        if self.google_task_name is None:
            self.google_task_name = f'{self.__class__.__name__}-{uuid4()}'

    ## GTask methods
    def gtask_queue_path(self) -> str:
        return self.gtask.queue_path(
            project=self.google_task_project,
            location=self.google_task_location,
            queue=self.worker_id
        )

    def gtask_task_path(self) -> str:
        return self.gtask.task_path(
            project=self.google_task_project,
            location=self.google_task_location,
            queue=self.worker_id,
            task=self.google_task_name
        )

    def gtask_create_task_request(self, body: dict) -> CreateTaskRequest:
        # https://cloud.google.com/tasks/docs/creating-http-target-tasks#createtask_method
        if self.timeout is not None:
            deadline = duration_pb2.Duration() # pylint: disable=no-member
            deadline.FromSeconds(self.timeout)

        task = {
            'name': self.gtask_task_path(),
            'dispatch_deadline': deadline,
            'http_request': {
                'http_method': HttpMethod.POST,
                'url': f'{self.worker_url}/worker/{self.worker_id}',
                'headers': self.get_headers(),
                'body': compress(body, serialize='pickle')
            }
        }
        return CreateTaskRequest(parent=self.gtask_queue_path(), task=task)

    ## Public methods
    def get_headers(self) -> dict:
        """
        Return the headers that must be used to receive the task.
        Remember that body must be always a byte object, then on child
        classes do like de example bellow.

        Example:
            >>> def get_headers(self) -> dict:
            ...     headers = super().get_headers()
            ...     headers['new_header'] = 'bla bla'
            ...     return headers
        """
        return {'Content-type': 'application/octet-stream'}

    def run(self) -> str:
        """ This must return a str object to be used on worker logs """
        pass

    def send_start(self) -> Queue:
        resume_queue_request = ResumeQueueRequest(name=self.gtask_queue_path())
        return self.gtask.resume_queue(request=resume_queue_request)

    def send_pause(self) -> Queue:
        pause_queue_request = PauseQueueRequest(name=self.gtask_queue_path())
        return self.gtask.pause_queue(request=pause_queue_request)

    def save(self, timeout: float = 30.0, retry_times: int = 0) -> Task:
        """
        Saves this task on Google Cloud Tasks to be executed.
        We will only retry if the Task Error is in (DeadlineExceeded, ServiceUnavailable, TooManyRequests).
        Be careful, if the task name is random retry could duplicate the task.
        # https://everysk.atlassian.net/browse/COD-1546

        Args:
            timeout (float, optional): Time to wait until the task is done. Defaults to 30.0.
            retry_times (int, optional): Retry times if the task fails. Defaults to 0.
        """
        # Timeout could not be greater than 30 seconds
        timeout = min(timeout, 30.0)

        body = {'cls': self.get_full_doted_class_path(), 'kwargs': self._received_kwargs}
        task = None
        try:
            task = self.gtask.create_task(request=self.gtask_create_task_request(body), timeout=timeout)

        except AlreadyExists:
            log.debug('Google task already exists: %s', self.gtask_task_path())

        except (DeadlineExceeded, ServiceUnavailable, TooManyRequests) as error:
            if retry_times > 0:
                retry_times = retry_times - 1
                task = self.save(timeout=timeout, retry_times=retry_times)
            else:
                raise error

        return task


###############################################################################
#   WorkerGoogle Class Implementation
###############################################################################
class WorkerGoogle(BaseGoogle):
    """
    Example:
        from flask import Flask, request
        from everysk.core.fields import StrField
        from everysk.core.workers import WorkerGoogle

        WORKER_ID = 'worker-id'

        class FirestoreSaveWorker(WorkerGoogle):
            google_task_location: StrField(default='location', readonly=True)
            google_task_project: StrField(default='project', readonly=True)
            worker_id: StrField(default=WORKER_ID, readonly=True)

        ## Flask app
        app = Flask(__name__)

        @app.route(f'/worker/{WORKER_ID}', methods=['POST'])
        def firestore_save():
            return FirestoreSaveWorker.worker_run(
                headers=request.headers,
                data=request.data
            )

        ## Main run function
        if __name__ == "__main__":
            app.run(host=settings.FLASK_HOST, port=settings.FLASK_PORT, debug=settings.DEBUG)
    """

    ## Public methods
    def check_google_task(self, headers: dict) -> bool:
        """ Check Google Task readers to ensure that the request come from then. """
        queue_name = headers.get('X-Cloudtasks-Queuename', None)
        user_agent = headers.get('User-Agent', None)
        return queue_name == self.worker_id and user_agent == 'Google-Cloud-Tasks'

    def run_task(self, cls: str, kwargs: dict) -> Any:
        """
        Run the task, if pause is activated from the Tread, stops
        until the self.worker_start message arrives.
        """
        cls = import_from_string(cls)
        task = cls(**kwargs)
        return task.run()

    @classmethod
    def worker_run(cls, headers: dict, data: bytes, worker_id: str = None) -> None:
        if worker_id is None:
            worker = cls()
        else:
            worker = cls(worker_id=worker_id)

        if not worker.check_google_task(headers):
            message = {'error': True, 'message': f"Couldn't validate Google headers - {headers}"}
            log.error(message['message'])
            return message

        try:
            post_data = decompress(data, serialize='pickle')
            result = worker.run_task(**post_data)
            return {'error': False, 'result': result}

        except Exception as error: #pylint: disable=broad-exception-caught
            message = f'Worker {cls.worker_id} error: {str(error)}'
            log.error('Worker %s error: %s', cls.worker_id, traceback.format_exc())
            return {'error': True, 'message': message}
