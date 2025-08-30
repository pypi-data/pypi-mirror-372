###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['Logger', 'LoggerManager']

import json
import logging
import traceback as python_traceback
import sys
from contextlib import AbstractContextManager
from contextvars import ContextVar
from datetime import datetime as DateTime
from types import TracebackType
from typing import Any
from threading import Thread
from zoneinfo import ZoneInfo

from everysk.config import settings


DEFAULT_APP_SERVER = settings.LOGGING_APP_SERVER
DEFAULT_TRACE_PARTS = {'version': '', 'trace_id': '', 'span_id': '', 'trace_sample': False}
HEADER_TRACEPARENT = 'traceparent'
HEADER_X_CLOUD_TRACE_CONTEXT = 'x-cloud-trace-context'
LOGGER_MANAGER_CONTEXT_VAR_NAME = 'everysk-lib-log-extra-context-var'


###############################################################################
#   Private functions Implementation
###############################################################################
def _default(obj: Any) -> str | None:
    """
    This function is used to convert the object to a string inside the json.dumps.

    Args:
        obj (Any): The object to be converted to a string.
    """
    if isinstance(obj, bytes):
        return obj.decode(json.detect_encoding(obj))

    return None

def _get_gcp_headers(headers: dict = None) -> dict:
    """
    Get the headers to be added to the log.
    The order is if the headers are sent in the log function, set in context or get from the default function.

    Args:
        headers (dict, optional): The headers generated outside the log. Defaults to None.

    Returns:
        dict: Only the headers that are in the list HEADER_TRACEPARENT and HEADER_X_CLOUD_TRACE_CONTEXT.
    """
    # pylint: disable=protected-access
    if not headers:
        headers = LoggerManager._extra.get().get('http_headers', {})

    return {key: value for key, value in headers.items() if key in (HEADER_TRACEPARENT, HEADER_X_CLOUD_TRACE_CONTEXT)}

def _get_trace_data(headers: dict) -> dict:
    """
    Get the trace_id, span_id and trace_sample from the headers.
    https://cloud.google.com/trace/docs/trace-context

    Args:
        headers (dict): The headers dictionary.
    """
    trace_parts = DEFAULT_TRACE_PARTS.copy()
    trace = headers.get(HEADER_TRACEPARENT, '')
    if trace:
        _parse_traceparent(trace, trace_parts)
    else:
        trace = headers.get(HEADER_X_CLOUD_TRACE_CONTEXT, '')
        if trace:
            _parse_x_cloud_trace_context(trace, trace_parts)

    if trace_parts['trace_id']:
        trace_parts['trace_id'] = f"{settings.LOGGING_GOOGLE_CLOUD_TRACE_ID}/{trace_parts['trace_id']}"

    return trace_parts

def _get_traceback() -> str:
    """
    Get the traceback of the current exception.
    """
    result = python_traceback.format_exc()
    # When there is no traceback the result is 'NoneType: None\n'
    # Like this is the most common case we check for equality and return an empty string
    if result == 'NoneType: None\n':
        return ''

    return result

def _parse_traceparent(traceparent: str, trace_parts: dict) -> None:
    """
    Parse the traceparent header and return a dictionary with the version, trace_id, span_id and trace_flags.
    Header example -> traceparent: "00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01"
    https://www.w3.org/TR/trace-context/
    From W3C documentation: traceparent: "<version>-<trace-id>-<parent-id>-<trace-flags>"

    Args:
        traceparent (str): The traceparent header value.
    """
    try:
        trace_parts['version'], trace_parts['trace_id'], trace_parts['span_id'], trace_parts['trace_sample'] = traceparent.split('-')
        trace_parts['trace_sample'] = bool(int(trace_parts['trace_sample']))
    except ValueError:
        pass

def _parse_x_cloud_trace_context(trace_context: str, trace_parts: dict) -> None:
    """
    Parse the x-cloud-trace-context header and return a dictionary with the trace_id and span_id.
    Header example -> x-cloud-trace-context: "4bfa9e049143840bef864a7859f2e5df/2048109991600514043;o=1"
    From Google documentation: X-Cloud-Trace-Context: TRACE_ID/SPAN_ID;o=OPTIONS

    Args:
        trace_context (str): The x-cloud-trace-context header value.
    """
    try:
        trace_parts['trace_id'], trace_parts['span_id'] = trace_context.split('/')
        trace_parts['span_id'], trace_parts['trace_sample'] = trace_parts['span_id'].split(';')
        trace_parts['trace_sample'] = trace_parts['trace_sample'].endswith('1') # pylint: disable=no-member
    except ValueError:
        pass


###############################################################################
#   Formatter Class Implementation
###############################################################################
class Formatter(logging.Formatter):

    def _get_default_dict(self, message: str, severity: str) -> dict:
        """
        Python logging default values.
        Severity levels: CRITICAL , ERROR , WARNING , INFO , DEBUG

        Args:
            message (str): The message to be logged.
            severity (str): The severity of the message.
        """
        return {'message': message, 'severity': severity}

    def _get_default_extra_dict(self, name: str, headers: dict, payload: dict, response: dict, traceback: str, labels: dict) -> dict:
        """
        Get the default extra data dictionary to be added to the log.
        Until now we only have the logName, traceback, http headers and http payload.

        Args:
            name (str): The name used to create the log.
            headers (dict): A dictionary with the HTTP headers.
            payload (dict): A dictionary with the HTTP payload.
        """
        return {
            'logName': name,
            'labels': labels,
            'traceback': traceback,
            'http': {
                'headers': headers,
                'payload': payload,
                'response': response,
            }
        }

    def _get_default_gcp_dict(self, headers: dict, filename: str, line: int, func_name: str) -> dict:
        """
        Default Google Cloud Platform dictionary to be added to the log.
        This dictionary has the trace_id, span_id, trace_sample used to chain the logs in the Google Cloud Logging.

        Args:
            headers (dict): A dictionary with the HTTP headers.
            filename (str): Filename where the log was placed.
            line (int): The line where the log was placed.
            func_name (str): The function name where the log was placed.
        """
        trace = _get_trace_data(headers)
        return {
            'logging.googleapis.com/trace': trace['trace_id'],
            'logging.googleapis.com/spanId': trace['span_id'],
            'logging.googleapis.com/trace_sampled': trace['trace_sample'],
            'logging.googleapis.com/sourceLocation': {
                'file': filename,
                'line': line,
                'function': func_name,
            },
        }

    def _get_result_dict(self, record: logging.LogRecord) -> dict:
        """
        Convert the log record to a dictionary.

        Args:
            record (logging.LogRecord): Record object with all the information about the log.
        """
        result = self._get_default_dict(message=record.getMessage(), severity=record.levelname)
        result.update(self._get_default_extra_dict(
            name=record.name,
            headers=getattr(record, 'http_headers', {}),
            payload=getattr(record, 'http_payload', {}),
            response=getattr(record, 'http_response', {}),
            traceback=getattr(record, 'traceback', ''),
            labels=getattr(record, 'labels', {})
        ))
        result.update(self._get_default_gcp_dict(
            headers=result['http']['headers'],
            filename=record.pathname,
            line=record.lineno,
            func_name=record.funcName)
        )
        return result

    def formatMessage(self, record: logging.LogRecord) -> str:
        """
        Format the message to be displayed in the terminal or Google Log Explorer.

        Args:
            record (logging.LogRecord): Record object with all the information about the log.
        """
        result = self._get_result_dict(record)
        return json.dumps(result, default=_default)

###############################################################################
#   LoggerManager Class Implementation
###############################################################################
class LoggerManager(AbstractContextManager):
    ## Private attributes
    _extra: ContextVar = ContextVar(LOGGER_MANAGER_CONTEXT_VAR_NAME, default={})
    _old_value: dict = None

    def __init__(
            self,
            http_headers: dict = None,
            http_payload: dict = None,
            http_response: dict = None,
            labels: dict = None,
            stacklevel: int = None,
            traceback: str = None,
        ) -> None:
        """
        Context class to create a context manager for the Logger object.
        This class is used to add extra information to the log.
        This manager together with everysk.core.threads will keep the context inside the thread.
        If you use python threads you need to pass the context inside the thread.

        Args:
            http_headers (dict, optional): The HTTP headers to be added to the log. Defaults to None.
            http_payload (dict, optional): The HTTP payload to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to None.
        """
        self.http_headers = http_headers
        self.http_payload = http_payload
        self.http_response = http_response
        self.labels = labels
        self.stacklevel = stacklevel
        self.traceback = traceback

        # Save this value to be used in the __exit__ method to restore the context
        self._old_value = self._extra.get().copy()

    def __enter__(self) -> 'LoggerManager':
        """
        Method to be executed when the context manager is created and always return self.
        This method is always executed even if "LoggerManager as some_var:" is not used.
        """
        # First we get the original context
        context: dict = self._extra.get()

        if self.http_headers is not None:
            context['http_headers'] = self.http_headers

        if self.http_payload is not None:
            context['http_payload'] = self.http_payload

        if self.http_response is not None:
            context['http_response'] = self.http_response

        if self.labels is not None:
            context['labels'] = self.labels

        if self.stacklevel is not None:
            context['stacklevel'] = self.stacklevel

        if self.traceback is not None:
            context['traceback'] = self.traceback

        # Finally we store the new context
        self._extra.set(context)

        return self

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        """
        https://docs.python.org/3/library/stdtypes.html#contextmanager.__exit__

        Returns:
            bool | None: If return is False any exception will be raised.
        """
        # Restore the context to the original value
        self._extra.set(self._old_value)

        return False

    @classmethod
    def reset(cls) -> None:
        """
        Reset the context to the default value.
        This method is used to avoid shared values between requests in server.endpoints module.
        """
        cls._extra = ContextVar(LOGGER_MANAGER_CONTEXT_VAR_NAME, default={})

###############################################################################
#   Logger Class Implementation
###############################################################################
class Logger:

    ## Private attributes
    _deprecated_hash: set[str] = set() # This needs to be initialized with an empty set because it will be a global list
    _default_stacklevel: int = 3 # 3 -> The place where the log.method was placed; 2 -> This file; 1 -> Python logger
    _log: logging.Logger = None
    _slack_timer: DateTime = None

    ## Public attributes
    name: str = None
    stacklevel: int = None

    ## Private methods
    def __init__(self, name: str, stacklevel: int = None) -> None:
        """
        Logger class used to send messages to STDOUT or Google CLoud Logging.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            name (str, optional): The name of the log. Defaults to "root".
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.

        Example:
            >>> from everysk.core.log import Logger
            >>> log = Logger(name='log-test')
            >>> log.debug('Test')
            2024-02-07 12:49:10,640 - DEBUG - {} - Test
        """
        if name == 'root':
            raise ValueError('The name of the log could not be "root".')
        self.name = name
        if stacklevel is not None and stacklevel > 0:
            self.stacklevel = stacklevel

        self._log = self._get_python_logger()

    def _get_extra_data(self, extra: dict, level: int = None) -> dict:
        """
        Get the extra data to be added to the log.
        We check if the extra was sent in the function, if not we check if it
        was set in the LoggerManager context, if not we check if we have a
        default function to get the data.
        We only set the payload

        Args:
            extra (dict): The extra data sent in the function.
            level (int): The level of the log.
        """
        http_headers = self._get_http_headers(extra.pop('http_headers', {}))
        if http_headers:
            extra['http_headers'] = http_headers

        http_payload = self._get_http_payload(extra.pop('http_payload', {}), level)
        if http_payload:
            extra['http_payload'] = http_payload

        http_response = self._get_http_response(extra.pop('http_response', {}))
        if http_response:
            extra['http_response'] = http_response

        # https://everysk.atlassian.net/browse/COD-6151
        # Because we use labels in the format for the normal log, this key always will be present
        labels = extra.pop('labels', {})
        if not labels:
            # If we don't receive labels as param in log functions we get from the context
            labels = LoggerManager._extra.get().get('labels', {}) # pylint: disable=protected-access

        # Labels are always present in the log even if it is an empty dictionary
        extra['labels'] = labels

        traceback = extra.pop('traceback', '')
        if not traceback:
            # If we don't receive traceback as param in log functions we get from the context
            # or from the result of traceback module
            traceback = LoggerManager._extra.get().get('traceback', '') or _get_traceback() # pylint: disable=protected-access
        if traceback:
            extra['traceback'] = traceback

        return extra

    def _get_http_headers(self, http_headers: dict) -> dict:
        """
        Get the http headers to be added to the log.
        The order is if the headers are sent in the log function, set in context or get from the default function.
        We only search for the payload if the level is ERROR or CRITICAL.

        Args:
            http_headers (dict): The HTTP headers sent in the log function.
            level (int): The level of the log.
        """
        return _get_gcp_headers(http_headers)

    def _get_http_payload(self, http_payload: dict, level: int = None) -> dict:
        """
        Get the http payload to be added to the log.
        The order is if the payload are sent in the log function, set in context or get from the default function.
        We only search for the payload if the level is ERROR or CRITICAL.

        Args:
            http_payload (dict): The HTTP payload sent in the log function.
            level (int): The level of the log.
        """
        if not http_payload and level in (logging.ERROR, logging.CRITICAL):
            http_payload = LoggerManager._extra.get().get('http_payload', {}) # pylint: disable=protected-access

        return http_payload

    def _get_http_response(self, http_response: dict) -> dict:
        """
        Get the http response to be added to the log.
        The order is if the response are sent in the log function, set in context or get from the default function.

        Args:
            http_response (dict): The HTTP response sent in the log function.
        """
        if not http_response:
            http_response = LoggerManager._extra.get().get('http_response', {}) # pylint: disable=protected-access

        return http_response

    def _get_python_logger(self) -> logging.Logger:
        """
        Method that creates/get the Python Logger object and attach the correct handler.
        The default handler will be the stdout.
        """
        if self._log is not None:
            return self._log

        # Create the log
        log = logging.getLogger(self.name)
        log.setLevel(logging.DEBUG)
        log.propagate = False # Don't pass message to others loggers

        # We should only have one handler per log name
        if not hasattr(log, 'handler'):
            log.handler = logging.StreamHandler(stream=sys.stdout)

            # Set the format that the message is displayed
            if settings.LOGGING_JSON:
                log.handler.setFormatter(Formatter())
            else:
                log.handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(labels)s - %(message)s'))

            # Add the handler inside the log
            log.addHandler(log.handler)

        # Set the level that the handler will be using.
        log.handler.setLevel(logging.DEBUG)

        return log

    def _get_stacklevel(self, stacklevel: int) -> int:
        """
        Get the stacklevel that was set in the function
        or in the LoggerManager context
        or set in the Logger object
        or use the default stacklevel.

        Args:
            stacklevel (int): The stacklevel to be used on the log.
        """
        if not stacklevel:
            stacklevel = LoggerManager._extra.get().get('stacklevel', {}) # pylint: disable=protected-access
            if not stacklevel:
                stacklevel = self.stacklevel or self._default_stacklevel

        return stacklevel

    def _send_to_log(self, level: int, msg: str, *args: tuple, extra: dict = None, stacklevel: int = None) -> None:
        """
        Send the message to the python logger using the correct level.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            level (int): The level of the message.
            msg (str): The message to log.
            *args (tuple): The arguments to be used on the message.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        stacklevel = self._get_stacklevel(stacklevel)
        extra = self._get_extra_data(extra or {}, level)
        self._log.log(level, msg, *args, extra=extra, stacklevel=stacklevel)

    def _show_deprecated(self, _id: str, show_once: bool) -> bool:
        """
        If show_once is False this always return True, otherwise
        checks if this _id is in the self._deprecated_hash set.

        Args:
            _id (str): String that will be stored to be checked later
            show_once (bool): Flag to store or not the id.
        """
        if show_once:
            if _id in self._deprecated_hash:
                return False

            self._deprecated_hash.add(_id)

        return True

    ## Public methods
    def critical(self, msg: str, *args: tuple, extra: dict = None, stacklevel: int = None)-> None:
        """
        Log a message with severity CRITICAL on this logger.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            msg (str): The message to log.
            *args (tuple): The arguments to be used on the message.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        self._send_to_log(logging.CRITICAL, msg, *args, extra=extra, stacklevel=stacklevel)

    def debug(self, msg: str, *args: tuple, extra: dict = None, stacklevel: int = None)-> None:
        """
        Log a message with severity DEBUG on this logger.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            msg (str): The message to log.
            *args (tuple): The arguments to be used on the message.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        self._send_to_log(logging.DEBUG, msg, *args, extra=extra, stacklevel=stacklevel)

    def deprecated(self, msg: str, *args, show_once: bool = True, extra: dict = None, stacklevel: int = None) -> None:
        """
        Shows a DeprecationWarning message with severity 'WARNING'.
        If show_once is True, then the message will be showed only once.

        Args:
            msg (str): The message that must be showed.
            show_once (bool, optional): If the message must be showed only once. Defaults to True.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        _id = hash(f'{msg}, {args}')
        if self._show_deprecated(_id=_id, show_once=show_once):
            msg = f'DeprecationWarning: {msg}'
            self.warning(msg, *args, extra=extra, stacklevel=stacklevel)

    def error(self, msg: str, *args: tuple, extra: dict = None, stacklevel: int = None)-> None:
        """
        Log a message with severity ERROR on this logger.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            msg (str): The message to log.
            *args (tuple): The arguments to be used on the message.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        self._send_to_log(logging.ERROR, msg, *args, extra=extra, stacklevel=stacklevel)

    def exception(self, msg: str, *args: tuple, extra: dict = None, stacklevel: int = None)-> None:
        """
        Log a message with severity ERROR on this logger.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            msg (str): The message to log.
            *args (tuple): The arguments to be used on the message.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        self.error(msg, *args, extra=extra, stacklevel=stacklevel)

    def info(self, msg: str, *args: tuple, extra: dict = None, stacklevel: int = None)-> None:
        """
        Log a message with severity INFO on this logger.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            msg (str): The message to log.
            *args (tuple): The arguments to be used on the message.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        self._send_to_log(logging.INFO, msg, *args, extra=extra, stacklevel=stacklevel)

    def _can_send_slack(self) -> bool:
        """
        Check if the slack message can be sent.
        We keep a track of the last message sent to avoid sending too many messages in less than 3 seconds.
        """
        now = DateTime.now(ZoneInfo('UTC')) # pylint: disable=no-member
        if self._slack_timer and (now - self._slack_timer).seconds < 2:
            return False

        self._slack_timer = now
        return True

    def slack(self, title: str, message: str, color: str, url: str = None, extra: dict = None, stacklevel: int = None) -> None:
        """
        Send a message to a Slack channel using Slack WebHooks.
        https://api.slack.com/messaging/webhooks
        The same message will be sent to the default log too:
            danger -> error
            success -> info
            warning -> warning

        Args:
            title (str): The title of the message.
            message (str): The body of the message.
            color (str): 'danger' | 'success' | 'warning'
            url (str, optional): The slack webhook url. Defaults to settings.SLACK_URL.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        if url is None:
            url = settings.SLACK_URL

        # We send the message only if url is set and we are in PROD and not in unittest
        if url and settings.PROFILE == 'PROD' and 'unittest' not in sys.modules:
            # We check if the last message was sent in less than 3 seconds to avoid sending too many messages
            if self._can_send_slack():
                # The import must be here to avoid circular import inside http module
                from everysk.core.slack import Slack # pylint: disable=import-outside-toplevel
                client = Slack(title=title, message=message, color=color, url=url)
                # This will send the message to Slack without block the request
                Thread(target=client.send).start()

        log_message = f'Slack message: {title} -> {message}'
        if color == 'danger':
            self.error(log_message, extra=extra, stacklevel=stacklevel)

        elif color == 'success':
            self.info(log_message, extra=extra, stacklevel=stacklevel)

        elif color == 'warning':
            self.warning(log_message, extra=extra, stacklevel=stacklevel)

    def warning(self, msg: str, *args: tuple, extra: dict = None, stacklevel: int = None)-> None:
        """
        Log a message with severity WARNING on this logger.
        Use stacklevel to show correctly the file and the line of the log, lvl 0 means the python
        logger, lvl 1 means this file, lvl 2 means the place where the log. was placed, if you use
        another file for the log object maybe you need to change to lvl 3.

        Args:
            msg (str): The message to log.
            *args (tuple): The arguments to be used on the message.
            extra (dict, optional): Extra information to be added to the log. Defaults to None.
            stacklevel (int, optional): The stacklevel to be used on the log. Defaults to 2.
        """
        self._send_to_log(logging.WARNING, msg, *args, extra=extra, stacklevel=stacklevel)
