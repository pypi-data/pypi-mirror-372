import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Optional, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from ts_sdk_connectors_python.utils import utc_time


class CommandAction(StrEnum):
    VALIDATE_CONFIG = "TetraScience.Connector.ValidateConfig"
    UPDATE_CONFIG = "TetraScience.Connector.UpdateConfig"
    START = "TetraScience.Connector.Start"
    STOP = "TetraScience.Connector.Stop"
    SHUTDOWN = "TetraScience.Connector.Shutdown"
    LIST_CUSTOM_COMMANDS = "TetraScience.Connector.ListCustomCommands"
    SET_LOG_LEVEL = "TetraScience.Connector.SetLogLevel"


class CommandStatus(StrEnum):
    SUCCESS = "SUCCESS"
    PROCESSING = "PROCESSING"
    FAILURE = "FAILURE"
    REJECTED = "REJECTED"


class HealthStatus(StrEnum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    NA = "N/A"


class PayloadDelivery(StrEnum):
    EMBEDDED = "embedded"
    REFERENCED = "referenced"


class OperatingStatus(StrEnum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    DISABLED = "DISABLED"


class JsonDictType:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, values):
        """Ensure the input is a dictionary or a valid JSON string."""
        if isinstance(value, dict):
            return value  # Already a valid dictionary

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed  # Valid JSON string
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Expected a JSON object string or dictionary, but got {type(value)}."
        )


CommandResponseBody: TypeAlias = Optional[JsonDictType]


class CommandResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    commandId: str = Field(description="The command id")
    targetId: Optional[str] = Field(None, description="The target ID (connector ID")
    status: Optional[CommandStatus] = Field(
        None, description="The status of the command."
    )
    responseBodyUploadUrl: Optional[str] = Field(
        None, description="The URL to upload the response body to."
    )
    body: CommandResponseBody = Field(description="The body of the command response")


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    commandId: str = Field(description="The command id")
    targetId: str = Field(description="The target ID (connector ID")
    action: CommandAction | str = Field(description="The action of the command.")
    createdAt: Optional[datetime] = Field(
        None, description="The created time of the command."
    )
    expiresAt: Optional[datetime] = Field(
        None, description="The expires time of the command."
    )
    bodyUrl: Optional[str] = Field(None, description="The body url of the command.")
    bodyDelivery: Optional[PayloadDelivery] = None
    responseBodyUploadUrl: Optional[str] = Field(
        None, description="The URL to upload the response body to."
    )
    body: Optional[Any] = Field(None, description="The body of the command request")

    @staticmethod
    def _validate_and_convert_body(body: Any) -> CommandResponseBody:
        if body is not None:
            try:
                JsonDictType.validate(body, {})
            except ValueError as e:
                body = {"requestBody": str(body)}
        # convert to JsonDictType if not already to conform to CommandResponseBody schema
        return body

    def create_response(self, update: Optional[dict] = None) -> CommandResponse:

        response_body = self._validate_and_convert_body(self.body)

        kwargs = {
            "commandId": self.commandId,
            "targetId": self.targetId,
            "responseBodyUploadUrl": self.responseBodyUploadUrl,
            "body": response_body,
        }
        if update:
            kwargs.update(update)
        resp = CommandResponse(**kwargs)
        return resp


class OutboundSqsCommandResponseBody(BaseModel):
    """
    A data transfer object for sending command responses to the outbound SQS queue.
    This model gets JSONified as a str and sent to the SQS queue.
    """

    commandId: str
    targetId: str
    status: CommandStatus
    body: Optional[CommandResponseBody] = None
    responseBodyDelivery: Optional[PayloadDelivery] = None
    createdAt: datetime = Field(
        default_factory=utc_time,
    )


# TODO: rename this to something more specific?


class RegisteredCommandInfo(BaseModel):
    """Model for custom command info"""

    action: str
    method_name: str
    documentation: str
    signature: str
