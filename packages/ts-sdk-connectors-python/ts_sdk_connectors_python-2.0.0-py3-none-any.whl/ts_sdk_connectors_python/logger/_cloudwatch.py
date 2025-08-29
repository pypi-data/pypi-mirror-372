from __future__ import annotations

import inspect
import logging
import os
import queue
from logging.handlers import QueueHandler, QueueListener
from typing import TYPE_CHECKING, Final, NamedTuple

from types_aiobotocore_logs import CloudWatchLogsClient
from types_aiobotocore_logs.type_defs import (
    InputLogEventTypeDef as CloudWatchEventTypeDef,
)

from ts_sdk_connectors_python.aws_factory import AWSFactory
from ts_sdk_connectors_python.constants import (
    DEFAULT_CLOUDWATCH_BUFFER_LIMIT,
    DEFAULT_CLOUDWATCH_FLUSH_INTERVAL,
    DEFAULT_CLOUDWATCH_FLUSH_LIMIT,
    MAX_CLOUDWATCH_BATCH_SIZE_BYTES,
    MAX_CLOUDWATCH_BATCH_SIZE_EVENTS,
    MAX_CLOUDWATCH_EVENT_SIZE_BYTES,
    ByteSizes,
    EnvVars,
)
from ts_sdk_connectors_python.logger._async_logging_utils import (
    AsyncHandlerABC,
    ThreadedAsyncQueueListener,
)
from ts_sdk_connectors_python.logger._base import get_logger
from ts_sdk_connectors_python.logger._cloudwatch_utils import (
    CloudWatchLogFormatter,
    LogEvent,
    cloudwatch_byte_size,
    to_cloudwatch_log_event,
)
from ts_sdk_connectors_python.logger._root import get_root_connector_sdk_logger
from ts_sdk_connectors_python.models import HealthStatus

if TYPE_CHECKING:
    from ts_sdk_connectors_python.tdp_api_base import _TdpApiBase
from ts_sdk_connectors_python.utils import Poll, to_js_isoformat

# Use the get_logger from _basic_logger
internal_logger = get_logger(__name__)

######################
# CloudWatch HandlerS
######################


class CloudWatchReporterOptions:
    @property
    def cloudwatch_buffer_limit(self) -> int:
        return int(
            os.environ.get(EnvVars.CLOUDWATCH_BUFFER_LIMIT)
            or DEFAULT_CLOUDWATCH_BUFFER_LIMIT
        )

    @property
    def cloudwatch_flush_limit(self) -> int:
        return int(
            os.environ.get(EnvVars.CLOUDWATCH_FLUSH_LIMIT)
            or DEFAULT_CLOUDWATCH_FLUSH_LIMIT
        )

    @property
    def cloudwatch_flush_interval_ms(self) -> int:
        return int(
            os.environ.get(EnvVars.CLOUDWATCH_FLUSH_INTERVAL)
            or DEFAULT_CLOUDWATCH_FLUSH_INTERVAL
        )


class CloudWatchReporter:
    def __init__(
        self,
        *,
        connector_id: str,
        tdp_api: _TdpApiBase,
        org_slug: str,
        aws_factory: AWSFactory,
    ):
        """
        Initializes the CloudWatchReporter.

        Manages the buffering and flushing of log events to AWS CloudWatch.

        Flushing log events to AWS CloudWatch occurs for a number of reasons:
            * The buffer reaches its size limit.
            * The flush interval is reached.
            * The flush limit is reached.
            * The connector is started.
            * The connector is stopped.
            * An explicit flush is triggered.


        :param connector_id: connector ID
        :param org_slug: the organization slug
        :param aws_factory: AWSFactory instance for thread-safe AWS operations
        """
        self.connector_id = connector_id
        self.tdp_api = tdp_api
        self.org_slug = org_slug
        self.aws_factory = aws_factory
        self._cloudwatch_buffer: list[LogEvent] = []
        now_isoformat = to_js_isoformat().replace(":", "-")
        self._log_stream_name: str = (
            f"connector-{connector_id}/standalone/{now_isoformat}"
        )
        # self.logger = get_logger('cloudwatch', extra={"context": "cloudwatch_log_reporter"})
        self.logger = get_logger("CloudWatchReporter")
        self._log_group_name: str = f"/connector/{org_slug}/{connector_id}"
        self._has_logger_buffer_full = False
        self._has_hit_flush_limit = False
        self._buffer_flush_lock = False
        self._options = CloudWatchReporterOptions()
        self._flush_poll: None | Poll = None
        self._has_started: bool = False
        self._reporter_health_status: HealthStatus = HealthStatus.HEALTHY

    def _start_polling(self):
        interval = int(self._options.cloudwatch_flush_interval_ms / 1000)
        self._flush_poll = Poll(
            target=self.flush_cloudwatch_buffer,
            interval=interval,
            args=("interval",),
            initial_delay=True,
        )
        self._flush_poll.start("cloudwatch_polling")

    def _stop_polling(self):
        if self._flush_poll is not None:
            self._flush_poll.stop()
            self._flush_poll = None

    @property
    def log_stream_name(self) -> str:
        """
        CloudWatch log stream name
        """
        return self._log_stream_name

    @property
    def log_group_name(self) -> str:
        """
        CloudWatch log group name
        """
        return self._log_group_name

    @property
    def buffer(self) -> list[LogEvent]:
        return self._cloudwatch_buffer[:]

    async def start_cloudwatch(self):
        self.logger.debug("Starting cloudwatch reporter")
        self._has_started = True
        await self.flush_cloudwatch_buffer("setup")

    async def stop_cloudwatch(self):
        self.logger.debug("Stopping cloudwatch reporter")
        self._has_started = False
        await self.flush_cloudwatch_buffer("shutdown")
        self._stop_polling()

    def _send_to_buffer(self, log_event: LogEvent):
        self._cloudwatch_buffer.append(log_event)

    @property
    def buffer_remaining(self) -> int:
        buffer_limit: Final[int] = self._options.cloudwatch_buffer_limit
        return buffer_limit - len(self._cloudwatch_buffer)

    async def send_to_cloudwatch_buffer(self, log_event: LogEvent):
        if not self._has_started:
            await self.start_cloudwatch()
        buffer_limit: Final[int] = self._options.cloudwatch_buffer_limit
        if self.buffer_remaining <= 1 and not self._has_logger_buffer_full:
            buffer_full_event = LogEvent(
                date=log_event.date,
                level=logging.getLevelName(logging.ERROR),
                message=f"Cloudwatch log buffer is full (limit {buffer_limit}). Subsequent messages will be "
                f"lost even if CloudWatch access is restored.",
            )
            self.send_to_internal_logger(buffer_full_event)
            self._send_to_buffer(buffer_full_event)
            self._has_logger_buffer_full = True
            self._reporter_health_status = HealthStatus.CRITICAL
            await self.update_health("CloudwatchBufferFull")
            return

        if not self._has_logger_buffer_full:
            self._send_to_buffer(log_event)

        if (
            len(self._cloudwatch_buffer) >= self._options.cloudwatch_flush_limit
            and not self._has_hit_flush_limit
        ):
            self._has_hit_flush_limit = True
            await self.flush_cloudwatch_buffer("flush limit")

    def send_to_internal_logger(self, log_event: LogEvent):
        self.logger.log(
            level=logging.getLevelName(log_event.level.upper()),
            extra=log_event.extra,
            msg=log_event.message,
        )

    async def update_health(self, error_code: str = ""):
        update_connector_health_request = {"status": self._reporter_health_status}
        if error_code:
            update_connector_health_request["errorCode"] = error_code
        health_request = self.tdp_api.update_health(
            connector_id=self.connector_id,
            update_connector_health_request=update_connector_health_request,
        )
        # TdpApi could be either sync or async
        if inspect.isawaitable(health_request):
            await health_request

    async def flush_cloudwatch_buffer(self, trigger: str):
        if self._buffer_flush_lock:
            self.logger.debug(f"Buffer flush already in progress, skipping {trigger}")
            return
        self._buffer_flush_lock = True

        try:
            if not self._cloudwatch_buffer:
                self.logger.debug(
                    f"{trigger} - No logs to send to Cloudwatch. Skipping flush.",
                    extra={"SKIP_CLOUDWATCH": True},
                )
            else:
                events_to_write: list[CloudWatchEventTypeDef] = []
                buffer_size_at_start_of_flush: int = len(self._cloudwatch_buffer)
                events_written_this_flush: int = 0
                while events_written_this_flush < buffer_size_at_start_of_flush:
                    buffer_index = 0
                    bytes_so_far = 0

                    while buffer_index < len(self._cloudwatch_buffer):
                        log_event = self._cloudwatch_buffer[buffer_index]
                        input_log_event = to_cloudwatch_log_event(log_event)
                        log_event_size = cloudwatch_byte_size(input_log_event)
                        if log_event_size > MAX_CLOUDWATCH_EVENT_SIZE_BYTES:
                            self.logger.warning(
                                "Message exceeded Cloudwatch message limit of 256kb, truncating",
                                extra={
                                    "logEventSize": log_event_size,
                                    "truncatedMessage": log_event.message[:100],
                                    "inputLogEvent": {
                                        # max char size in utf-8 is 4 bytes, so this truncates to half the byte limit
                                        # which is an imprecise approximation
                                        # taken from the Node Connector SDK
                                        **input_log_event,
                                        "message": input_log_event["message"][
                                            : int(MAX_CLOUDWATCH_EVENT_SIZE_BYTES / 8)
                                        ],
                                    },
                                },
                            )

                        if (
                            bytes_so_far + log_event_size
                            > MAX_CLOUDWATCH_BATCH_SIZE_BYTES
                            or len(events_to_write) >= MAX_CLOUDWATCH_BATCH_SIZE_EVENTS
                        ):
                            break
                        events_to_write.append(input_log_event)
                        bytes_so_far += log_event_size
                        buffer_index += 1

                    log_extra = {
                        "logCount": len(events_to_write),
                        "batchSize": str(int(bytes_so_far / ByteSizes.KB)) + " KB",
                        "SKIP_CLOUDWATCH": True,
                    }
                    num_logs = len(events_to_write)
                    self.logger.debug(
                        f"{trigger}: Sending {num_logs} buffered logs to CloudWatch",
                        extra=log_extra,
                    )
                    # Cloudwatch expects sorted log events
                    sorted_events = sorted(
                        events_to_write, key=lambda event: event["timestamp"]
                    )
                    await self.put_log_events(sorted_events)

                    self._cloudwatch_buffer = self._cloudwatch_buffer[buffer_index:]
                    events_written_this_flush += num_logs
                    events_to_write.clear()
                    self.logger.debug(
                        f"{trigger}: {num_logs} logs written to CloudWatch",
                        extra=log_extra,
                    )
                self._has_hit_flush_limit = False
                if self._reporter_health_status != HealthStatus.HEALTHY:
                    self._reporter_health_status = HealthStatus.HEALTHY
                    await self.update_health()
        except Exception as exc:
            if "The specified log stream does not exist." in exc.args[0]:
                self.logger.debug(
                    f"{trigger}: Log stream does not exist. Creating log stream and retrying",
                    extra={
                        "logStreamName": self.log_stream_name,
                        "logGroupName": self.log_group_name,
                    },
                )
                await self.create_log_stream()
                self._buffer_flush_lock = False
                await self.flush_cloudwatch_buffer("log stream created")
            else:
                self.logger.error(
                    "Error sending buffered logs to Cloudwatch", exc_info=exc
                )
                self._reporter_health_status = HealthStatus.WARNING
                await self.update_health("CloudwatchFlushError")

        finally:
            if self.buffer_remaining > 0:
                self._has_logger_buffer_full = False
            self._stop_polling()
            self._start_polling()
            self._buffer_flush_lock = False

    async def create_log_stream(self):
        try:
            self.logger.debug(
                "Creating log stream",
                extra={
                    "logStreamName": self.log_stream_name,
                    "logGroupName": self.log_group_name,
                },
            )
            # Get an AWS instance for the current thread and event loop
            aws = await self.aws_factory.get_aws_instance(
                connector_id=self.connector_id,
                org_slug=self.org_slug,
            )

            async with await aws.create_client("logs") as client:
                client: CloudWatchLogsClient
                await client.create_log_stream(
                    logGroupName=self.log_group_name, logStreamName=self.log_stream_name
                )

        except Exception as exc:
            if exc.__class__.__name__ == "ResourceAlreadyExistsException":
                self.logger.info("Log stream already exists, skipping creating")
            self.logger.error("Error creating log stream", exc_info=exc)
            raise exc

    async def put_log_events(self, events_to_write: list[CloudWatchEventTypeDef]):
        # Get an AWS instance for the current thread and event loop
        aws = await self.aws_factory.get_aws_instance(
            connector_id=self.connector_id,
            org_slug=self.org_slug,
        )

        async with await aws.create_client("logs") as client:
            client: CloudWatchLogsClient
            await client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=events_to_write,
            )


class SkipCloudWatchFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        extra: dict = {}
        if hasattr(record, "extra_info"):
            extra = record.extra_info
        if extra.get("SKIP_CLOUDWATCH", None) is True:
            return False
        return True


class CloudWatchLogHandler(AsyncHandlerABC):
    def __init__(
        self,
        *,
        connector_id: str,
        tdp_api: _TdpApiBase,
        org_slug: str,
        level: int | str = 0,
        aws_factory: AWSFactory,
    ):
        """
        Initializes a cloudwatch log handler that sends log records to the cloudwatch reporter.
        The reporter will batch log records and upload to CloudWatch periodically.

        :param connector_id: The connector id
        :param org_slug: The org slug
        :param level: Level of the logging
        :param aws_factory: AWSFactory instance for thread-safe AWS operations
        """
        super().__init__(level=level)
        self.formatter: CloudWatchLogFormatter = CloudWatchLogFormatter()
        self.cloudwatch_reporter = CloudWatchReporter(
            connector_id=connector_id,
            tdp_api=tdp_api,
            org_slug=org_slug,
            aws_factory=aws_factory,
        )

    async def emit(self, record: logging.LogRecord):
        log_event = self.formatter.to_log_event(record)
        await self.cloudwatch_reporter.send_to_cloudwatch_buffer(log_event)

    async def handle(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record with acquisition/release of
        the I/O thread lock. Returns whether the filter passed the record for
        emission.
        """
        rv = self.filter(record)
        if rv:
            self.acquire()
            try:
                await self.emit(record)
            finally:
                self.release()
        return rv


class CloudWatchLogReporterKey(NamedTuple):
    connector_id: str
    org_slug: str


class CloudWatchLogReporterEntry(NamedTuple):
    listener: QueueListener
    handler: QueueHandler
    reporter: CloudWatchReporter
    queue: queue.SimpleQueue


class CloudWatchLoggingManager:
    """A class that manages attaching cloudwatch handlers to the root connector logger to ensure
    the same handlers for a connector_id/org_slug are not added multiple times."""

    registry: dict[
        CloudWatchLogReporterKey,
        CloudWatchLogReporterEntry,
    ] = {}

    @classmethod
    async def init_reporter(
        cls,
        *,
        connector_id: str,
        tdp_api: _TdpApiBase,
        org_slug: str,
        aws_factory: AWSFactory,
        http_client=None,
    ):
        connector_id = connector_id
        org_slug = org_slug
        key = CloudWatchLogReporterKey(connector_id=connector_id, org_slug=org_slug)

        if key not in cls.registry:
            log_queue = queue.SimpleQueue()
            queue_handler = QueueHandler(log_queue)

            cw_handler = CloudWatchLogHandler(
                connector_id=connector_id,
                tdp_api=tdp_api,
                org_slug=org_slug,
                aws_factory=aws_factory,
            )
            cw_handler.addFilter(SkipCloudWatchFilter())
            queue_listener = ThreadedAsyncQueueListener(
                log_queue,
                cw_handler,
            )
            queue_listener.start()
            get_root_connector_sdk_logger().addHandler(queue_handler)
            listener = queue_listener
            reporter = cw_handler.cloudwatch_reporter
            cls.registry[key] = CloudWatchLogReporterEntry(
                listener=listener,
                handler=queue_handler,
                reporter=reporter,
                queue=log_queue,
            )

    @classmethod
    def get_listener(cls, connector_id: str, org_slug: str) -> QueueListener:
        key = CloudWatchLogReporterKey(connector_id=connector_id, org_slug=org_slug)
        return cls.registry[key].listener

    @classmethod
    def get_handler(cls, connector_id: str, org_slug: str) -> QueueHandler:
        key = CloudWatchLogReporterKey(connector_id=connector_id, org_slug=org_slug)
        return cls.registry[key].handler

    @classmethod
    def get_reporter(cls, connector_id: str, org_slug: str) -> CloudWatchReporter:
        key = CloudWatchLogReporterKey(connector_id=connector_id, org_slug=org_slug)
        return cls.registry[key].reporter

    @classmethod
    async def stop_cloudwatch(cls, connector_id: str, org_slug: str):
        key = CloudWatchLogReporterKey(connector_id=connector_id, org_slug=org_slug)
        if key in cls.registry:
            entry = cls.registry[key]
            await entry.reporter.stop_cloudwatch()
            if entry.handler in get_root_connector_sdk_logger().handlers:
                get_root_connector_sdk_logger().removeHandler(entry.handler)
            del cls.registry[key]
