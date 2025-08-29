import asyncio
import copy
import gzip
import json
from typing import Optional

import httpx
from httpx._types import ResponseContent
from pydantic import BaseModel, ValidationError
from types_aiobotocore_sqs.type_defs import MessageTypeDef

from ts_sdk_connectors_python.aws_factory import AWSFactory
from ts_sdk_connectors_python.constants import (
    DEFAULT_SQS_QUEUE_WAIT_TIME_SECONDS,
    DEFAULT_SQS_TIMEOUT_SECONDS,
    MAX_EMBEDDED_MESSAGE_SIZE,
    EnvVars,
)
from ts_sdk_connectors_python.event_emitter import EventsEmitter
from ts_sdk_connectors_python.logger import get_logger
from ts_sdk_connectors_python.models import (
    CommandAction,
    CommandRequest,
    CommandResponse,
    CommandResponseBody,
    CommandStatus,
    OutboundSqsCommandResponseBody,
    PayloadDelivery,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import (
    ConnectorDetailsDto,
)
from ts_sdk_connectors_python.tdp_api import TdpApi
from ts_sdk_connectors_python.tdp_api_base import TdpApiError
from ts_sdk_connectors_python.utils import TaskManager, utc_time

logger = get_logger(__name__)


def utf8len(string: str) -> int:
    """Return bytes of an utf-8 str"""
    return len(string.encode("utf-8"))


def new_client_without_auth(old_async_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Create a new AsyncClient instance with the 'Authorization' header removed while preserving other headers."""
    # Perform a shallow copy of the original client to retain settings, connections, and state.
    # copy.deepcopy() is avoided to prevent issues with unpicklable async components (e.g., '_asyncio.Future').
    new_async_client = copy.copy(old_async_client)

    if old_async_client.headers:
        # Create a new headers dictionary to avoid modification of the original
        # Use "authorization" instead of "Authorization" because the underlying httpx client normalizes header keys to lowercase.
        new_async_client.headers = {
            k: v
            for k, v in old_async_client.headers.items()
            if k.lower() != "authorization"
        }

    return new_async_client


class CommandListenerOptions(BaseModel):
    """Command listener options"""

    sqs_wait_time_seconds: int = DEFAULT_SQS_QUEUE_WAIT_TIME_SECONDS


class CommandListener:
    def __init__(
        self,
        api_inst: TdpApi,
        options: Optional[CommandListenerOptions] = None,
    ):
        self.api_inst = api_inst
        self.task_manager = TaskManager()
        self.listening_for_commands: bool = False
        self.options = options or CommandListenerOptions()
        self.events_emitter: EventsEmitter[CommandRequest] = EventsEmitter()
        self._aws_factory = AWSFactory()
        assert self.outbound_command_queue
        assert self.connector_id

    @property
    def outbound_command_queue(self) -> str:
        queue_url = self.api_inst.config.outbound_command_queue
        if not queue_url:
            raise TdpApiError(
                f"outbound_command_queue must be defined on the {self.api_inst.__class__.__name__} config in order to use the "
                f"command listener. This can be provided by the the {EnvVars.OUTBOUND_COMMAND_QUEUE} env var"
            )
        return queue_url

    @property
    def connector_id(self) -> str:
        connector_id = self.api_inst.config.connector_id
        if not connector_id:
            raise TdpApiError(
                f"connector_id must be defined on the {self.api_inst.__class__.__name__} config in order to use the "
                f"command listener. This can be provided by the the {EnvVars.CONNECTOR_ID} env var"
            )
        return connector_id

    async def get_connector(self) -> ConnectorDetailsDto | None:
        resp = await self.api_inst.get_connector_by_id(self.connector_id)
        return resp.parsed

    async def commands_listener_loop(self):
        self.listening_for_commands = True

        while self.listening_for_commands:
            message = None
            try:
                message = await self.wait_for_command_message()
            except Exception as exc:
                logger.error(f"Error receiving command: {exc}")
            try:
                if message:
                    await self.handle_command_sqs_message(message)
            except Exception as exc:
                logger.error(f"Error handling command: {exc}")

            # Note: This sleep appears to necessary for python asyncio coroutines to 'tick forward'.
            #       This allows the async loop to yield control so other async tasks can run
            await asyncio.sleep(0.1)

    @property
    def _command_listener_task_name(self) -> str:
        return f"commands_listener_{self.connector_id}"

    def start(self):
        """
        Starts the command listener loop.

        :return: None
        """
        logger.info("Starting commands listener")
        self.task_manager.create_task(
            self.commands_listener_loop(), self._command_listener_task_name
        )
        self.events_emitter.start()

    def stop(self):
        """
        Stops the command listener loop.

        :return: None
        """
        logger.info("Stopping commands listener")
        self.listening_for_commands = False
        self.task_manager.cancel(self._command_listener_task_name)
        self.events_emitter.stop()

    async def upload_command_response_body(
        self, upload_url: str, response_body: CommandResponseBody
    ):
        json_str = json.dumps(response_body)
        compressed_body_str = gzip.compress(json_str.encode())

        # Note:
        # The async HTTPX client (`self.api_inst.client.get_async_httpx_client()`) is initialized
        # with an "Authorization" header: {"Authorization": f"Bearer {token}"} (see client_creator.py).
        #
        # However, when making a request to an S3 pre-signed URL, the URL already contains
        # authentication query parameters such as "X-Amz-Algorithm".
        #
        # If both the pre-signed URL's query parameters and the "Authorization" header are used,
        # AWS returns a 400 Bad Request error with the message:
        # "InvalidArgument: Only one auth mechanism allowed; only the X-Amz-Algorithm query parameter,
        # Signature query string parameter, or the Authorization header should be specified."
        #
        # To prevent this conflict, we create a new HTTPX async client without the "Authorization" header
        # to upload the content.

        client = self.api_inst.client.get_async_httpx_client()

        new_client = new_client_without_auth(client)
        resp = await new_client.put(
            url=upload_url,
            content=compressed_body_str,
            headers={
                "Content-Type": "application/json",
                "Content-Encoding": "gzip",
            },
        )
        if not (200 <= resp.status_code < 300):
            raise RuntimeError(
                f"Upload command response failed with status code {resp.status_code}"
            )

    async def send_command_response(self, command: CommandResponse):
        """
        Send a command response to the outbound SQS queue.

        :param command: The incoming command
        :return: None
        """
        logger.info("Sending command response", extra=command.model_dump())

        outbound_message_body = OutboundSqsCommandResponseBody(
            commandId=command.commandId,
            targetId=command.targetId,
            status=command.status,
            body=command.body,
            responseBodyDelivery=PayloadDelivery.EMBEDDED,
        )

        if self.should_deliver_via_upload(command, outbound_message_body):
            logger.info(
                "Uploading command response body",
                extra={"commandId": command.commandId},
            )
            try:
                await self.upload_command_response_body(
                    command.responseBodyUploadUrl, command.body
                )
            except Exception as exc:
                logger.error("Error uploading command response body", exc_info=exc)
                raise exc
            outbound_message_body.responseBodyDelivery = PayloadDelivery.REFERENCED
            outbound_message_body.body = None

        aws = await self._aws_factory.get_aws_instance(
            connector_id=self.connector_id,
            org_slug=self.api_inst.config.org_slug,
            http_client=self.api_inst.client,
        )

        async with await aws.create_client("sqs") as sqs_client:
            async with asyncio.timeout(DEFAULT_SQS_TIMEOUT_SECONDS):
                await sqs_client.send_message(
                    QueueUrl=self.outbound_command_queue,
                    MessageBody=outbound_message_body.model_dump_json(),
                )
            logger.info("Sent command response", extra={"commandId": command.commandId})

    @staticmethod
    def should_deliver_via_upload(
        command: CommandResponse, outbound_response: OutboundSqsCommandResponseBody
    ) -> bool:
        if not command.responseBodyUploadUrl or not command.body:
            return False
        message_size = utf8len(outbound_response.model_dump_json())
        return message_size > MAX_EMBEDDED_MESSAGE_SIZE

    async def send_reject_command(
        self, command_response: CommandResponse, message_id: str
    ):

        logger.info(
            "Command expiry date passed, rejecting",
            extra={
                "messageId": message_id,
                "action": command_response.action,
                "expiry": command_response.expiresAt.isoformat(),
            },
        )
        await self.send_command_response(
            command_response.model_copy(
                update={
                    "body": {
                        "reason": f"Command expiry date {command_response.expiresAt.isoformat()} is passed"
                    },
                    "status": CommandStatus.REJECTED,
                }
            )
        )

    async def send_processing_command(self, command_response: CommandResponse):
        """
        Send a processing command response to the outbound queue.

        :param command_response: Incoming command response
        :return: None
        """
        response = command_response.model_copy(
            update={"status": CommandStatus.PROCESSING}
        )
        await self.send_command_response(response)

    async def download_content(self, url: str) -> ResponseContent:
        """
        Download content from a provided url

        :param url: The url of the content to download
        :return: The response content
        """
        # Note:
        # The async HTTPX client (`self.api_inst.client.get_async_httpx_client()`) is initialized
        # with an "Authorization" header: {"Authorization": f"Bearer {token}"} (see client_creator.py).
        #
        # However, when making a request to an S3 pre-signed URL, the URL already contains
        # authentication query parameters such as "X-Amz-Algorithm".
        #
        # If both the pre-signed URL's query parameters and the "Authorization" header are used,
        # AWS returns a 400 Bad Request error with the message:
        # "InvalidArgument: Only one auth mechanism allowed; only the X-Amz-Algorithm query parameter,
        # Signature query string parameter, or the Authorization header should be specified."
        #
        # To prevent this conflict, we create a new HTTPX async client without the "Authorization" header
        # to download the content.

        client = self.api_inst.client.get_async_httpx_client()
        new_client = new_client_without_auth(client)
        resp: httpx.Response = await new_client.get(url=url)
        return resp.content

    async def handle_command_sqs_message(self, message: MessageTypeDef):
        """
        Handle a received SQS message, emit command request events, and then delete the message from the SQS queue.
        :param message:
        :return:
        """
        body = message["Body"]
        message_id = message["MessageId"]
        receipt_handle = message["ReceiptHandle"]

        cmd_request = None
        try:
            cmd_request = CommandRequest.model_validate_json(body)
        except ValidationError as e:
            logger.error("Message body is not a valid command request", exc_info=e)

        if cmd_request is not None:
            if cmd_request.expiresAt < utc_time():
                await self.send_reject_command(
                    cmd_request, message_id=message["MessageId"]
                )
            else:
                await self.send_processing_command(cmd_request.create_response())

                if (
                    cmd_request.bodyDelivery == PayloadDelivery.REFERENCED
                    and cmd_request.bodyUrl
                ):
                    logger.info(
                        "Command body is referenced, downloading",
                        extra={"messageId": message["MessageId"]},
                    )
                    cmd_request.body = await self.download_content(cmd_request.bodyUrl)

                # emit events to be picked up by the connector
                await self.emit_events(cmd_request.action, cmd_request)

        await self.delete_command_message(
            message_id=message_id, receipt_handle=receipt_handle
        )

    async def emit_events(
        self, action: CommandAction | str, command_request: CommandRequest
    ):
        """
        Emit command request events to be picked up by a Connector listening to the events emitter.

        :param action: The command action str
        :param command_request: The command request to emit as an event.
        :return: None
        """
        await self.events_emitter.emit("command", command_request)

    async def delete_command_message(self, *, message_id: str, receipt_handle: str):
        """
        Delete an SQS message from the queue.
        :param message_id: The message id
        :param receipt_handle: The receipt handle
        :return: None
        """
        connector = await self.get_connector()

        # Get an AWS instance for the current thread and event loop
        aws = await self._aws_factory.get_aws_instance(
            connector_id=self.connector_id,
            org_slug=self.api_inst.config.org_slug,
            http_client=self.api_inst.client,
        )

        async with await aws.create_client("sqs") as sqs_client:
            # delete sqs message
            logger.info(
                "Deleting SQS message",
                extra={"messageId": message_id},
            )
            async with asyncio.timeout(DEFAULT_SQS_TIMEOUT_SECONDS):
                await sqs_client.delete_message(
                    QueueUrl=connector.command_queue, ReceiptHandle=receipt_handle
                )
            logger.info("Deleted SQS message", extra={"messageId": message_id}),

    async def wait_for_command_message(self) -> MessageTypeDef | None:
        """
        Wait for SQS messages on the command queue. This will wait for a specified number of seconds
        (`options.sqs_wait_time_seconds`) before return either the received message or None.

        :return: message as MessageTypeDef or None if no message received within the specified wait time.
        """
        connector = await self.get_connector()
        if connector is None:
            logger.error("No connector found.")
        else:
            aws = await self._aws_factory.get_aws_instance(
                connector_id=self.connector_id,
                org_slug=self.api_inst.config.org_slug,
                http_client=self.api_inst.client,
            )

            async with await aws.create_client("sqs") as sqs_client:
                async with asyncio.timeout(
                    DEFAULT_SQS_TIMEOUT_SECONDS + self.options.sqs_wait_time_seconds
                ):
                    response = await sqs_client.receive_message(
                        QueueUrl=connector.command_queue,
                        MaxNumberOfMessages=1,
                        WaitTimeSeconds=self.options.sqs_wait_time_seconds,
                    )
                messages = response.get("Messages", [])
                if len(messages) > 0:
                    return messages[0]
                return None
