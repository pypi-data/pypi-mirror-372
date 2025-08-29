import logging
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import PurePath
from typing import Any, Dict, Final, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel
from types_aiobotocore_logs.type_defs import (
    InputLogEventTypeDef as CloudWatchEventTypeDef,
)

_ExtraInfo: Final[str] = "extra_info"


class ConsoleLogEvent(BaseModel):

    level: str
    message: str
    extra: Optional[dict] = None
    error: Optional[dict] = None


class LogEvent(BaseModel):
    """
    Represents a log event with structured data.

    Attributes:
        level (str): The log level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        message (str): The log message.
        extra (Optional[dict]): Additional contextual information for the log event.
        error (Any): Error information, if any, associated with the log event.
    """

    date: datetime
    level: str
    message: str
    extra: Optional[dict] = None
    error: Optional[dict] = None

    def format_for_console(self) -> str:
        return ConsoleLogEvent(
            level=self.level.lower(),
            message=self.message,
            extra=self.extra,
            error=self.error,
        ).model_dump_json(exclude_unset=True, exclude_none=True)


class CloudWatchLogFormatter(logging.Formatter):
    """
    Formats logs for cloudwatch.

    Examples of logs::

        {"level":"info","message":"An info message","extra":{"orgSlug":"Fake-Org","connectorId":"1a452c27-8a3b-4f58-a871-49f8f0eaad2c"}}
        {"level":"error","message":"An error message","extra":{"orgSlug":"Fake-Org","connectorId":"1a452c27-8a3b-4f58-a871-49f8f0eaad2c"}}

    """

    def get_log_error(self, record) -> dict | None:
        """Create the 'error' portion of the log json"""
        exc_info = record.exc_info
        log_data = None
        if exc_info:
            log_data = {}
            if isinstance(exc_info, tuple):
                exception = exc_info[1]
                if isinstance(exception, BaseException):
                    log_data["error"] = exception.__class__.__name__
                    if exception.args:
                        message = exception.args[0]
                    else:
                        message = str(exception)
                    log_data["message"] = message
            if record.lineno is not None:
                log_data["lineno"] = record.lineno
            traceback = self.formatException(exc_info)
            traceback = traceback.replace("\n", " ")
            log_data["traceback"] = traceback
        return log_data

    def formatStack(self, stack_info: str) -> str:
        return stack_info.replace("\n", " ")

    def to_log_event(self, record: logging.LogRecord) -> LogEvent:
        extra_info = None
        if hasattr(record, _ExtraInfo):
            extra_info = getattr(record, _ExtraInfo)
            extra_info = _try_serialize(extra_info)

        error_info = self.get_log_error(record)
        if error_info:
            error_info = _try_serialize(error_info)

        log_event = LogEvent(
            level=record.levelname.upper(),
            message=record.getMessage(),
            extra=extra_info,
            error=error_info,
            date=datetime.fromtimestamp(record.created),
        )
        return log_event

    def format(self, record: logging.LogRecord) -> str:
        """
        Format an incoming LogRecord into a JSON consistent with the Node Connector SDK and CloudWatch formats.
        """
        log_event = self.to_log_event(record)
        return log_event.format_for_console()


def cloudwatch_byte_size(event: CloudWatchEventTypeDef) -> int:
    """See https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/client/cloudwatch-logs/command/PutLogEventsCommand/
    Note this is called on a CloudWatchEvent, not a LogEvent; as such, `message` is a JSON dump of a LogEvent"""
    return len(event["message"].encode("utf-8")) + 26


def to_cloudwatch_log_event(log_event: LogEvent) -> CloudWatchEventTypeDef:
    epoch_ms = int(log_event.date.timestamp() * 1000)
    return {
        "message": log_event.model_dump_json(
            exclude_unset=True, exclude_none=True, exclude={"date"}
        ),
        "timestamp": epoch_ms,
    }


SerializableValue = Union[
    str,
    int,
    bool,
    None,
    Dict[str, "SerializableValue"],
    List["SerializableValue"],
]


def _try_serialize(value: Any) -> SerializableValue:
    """Try to serialize a value into a dictionary for logging. dicts, lists, and tuples are recursively serialized.
    Objects are attempted to be serialized using their `__str__` method.

    If it fails, return the string representation of the value."""
    # Normal path is to serialize a simple dict
    if isinstance(value, dict):
        return {k: _try_serialize(v) for k, v in value.items()}
    elif isinstance(value, (str, int, bool, type(None))):
        return value
    elif isinstance(value, float):
        # preserves precision
        return str(value)

    # At this point, something unusual has happened. Perhaps the user has passed a predictable common object into the extra?
    elif isinstance(value, BaseModel):
        return _try_serialize(value.model_dump(exclude_unset=True, exclude_none=True))
    elif isinstance(value, (list, tuple, set)):
        return [_try_serialize(item) for item in value]
    elif is_dataclass(value) and not isinstance(value, type):
        return _try_serialize(asdict(value))
    elif isinstance(value, UUID):
        return _try_serialize(str(value))
    elif isinstance(value, Decimal):
        return _try_serialize(str(value))
    elif isinstance(value, PurePath):
        return _try_serialize(str(value))
    elif hasattr(value, "isoformat") and callable(
        value.isoformat
    ):  # datetime-like objects
        return _try_serialize(value.isoformat())
    elif isinstance(value, Enum):
        enum = {
            "_enum": value.__class__.__name__,
            "name": value.name,
            "value": value.value,
        }
        return _try_serialize(enum)

    # At this point, the SDK may be passed a custom class or object.
    else:
        try:
            return {"_name": type(value).__name__, "_as_string": str(value)}
        except Exception:
            return {
                "_unserializable": f"<unserializable object of type {type(value).__name__}>"
            }
