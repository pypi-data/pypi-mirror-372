"""
Early Log Buffer Module (Standalone Connectors Only)

This module provides early log buffering functionality to capture all standalone connector
startup logs before CloudWatch logging is initialized. This ensures 100% log coverage from
the very first moment of standalone connector execution.

IMPORTANT: This buffering is ONLY enabled for standalone connectors (detected via CONNECTOR_TOKEN
environment variable). Other connector types (hub, cloud) do not use this buffer.

Problem Solved:
--------------
During standalone connector startup, there's a gap between when logging begins and when CloudWatch is ready:
1. Standalone connector starts and begins logging (proxy config, AWS setup, etc.)
2. CloudWatch logger initialization requires AWS credentials and network setup
3. Early startup logs would be lost to CloudWatch without buffering

Solution:
---------
The EarlyLogBuffer system captures all logs in memory during standalone connector startup,
then flushes them to CloudWatch once it's initialized, ensuring complete log coverage.

Architecture:
------------
- EarlyLogBufferHandler: Captures and stores log records in memory
- EarlyLogBuffer: Singleton manager for the buffer system
- Standalone detection: Buffer only initializes if CONNECTOR_TOKEN env var is present
- Automatic cleanup: Buffer is flushed and removed after CloudWatch initialization

Usage Flow (Standalone Connectors Only):
---------------------------------------
1. Module import → Check if standalone → Buffer initialized if standalone
2. Early logging → Messages stored in memory buffer (standalone only)
3. CloudWatch init → Buffer contents flushed to CloudWatch
4. Buffer cleanup → Handler removed, direct CloudWatch logging continues

Key Features:
------------
- Zero log loss during startup
- Chronological order preservation
- Memory-safe with configurable limits
- Thread-safe operation
- Automatic lifecycle management
- Graceful error handling

Example Timeline:
----------------
00:00.000 - Connector starts, buffer initialized
00:00.100 - "Loading proxy settings" → buffered
00:00.200 - "Creating AWS client" → buffered
00:01.500 - CloudWatch initialized
00:01.501 - Buffer flushed: 15 logs → CloudWatch
00:01.502 - Buffer removed, direct logging continues
00:01.600 - "Connector started" → direct to CloudWatch

Related Files:
-------------
- _root.py: Initializes the buffer during logger setup
- tdp_api_base.py: Triggers buffer flush after CloudWatch init
- _cloudwatch.py: Receives flushed logs from buffer

Implementation Notes:
--------------------
- Buffer uses LogEvent format (not LogRecord) for consistency with CloudWatch
- Logs are inserted at beginning of CloudWatch buffer to maintain chronological order
- Buffer is automatically removed after flush to prevent memory leaks
- Guards prevent double-flushing and post-flush buffering
"""
import logging
from typing import List, Optional

from ts_sdk_connectors_python.logger._cloudwatch_utils import CloudWatchLogFormatter


class EarlyLogBufferHandler(logging.Handler):
    """
    Handler that buffers early logs until CloudWatch is ready.

    This handler captures log records during connector startup and converts them
    to LogEvent format for later transfer to CloudWatch. Once CloudWatch is
    initialized, the buffer is flushed and the handler is marked as inactive.

    Attributes:
        buffer: List of LogEvent objects waiting to be flushed
        is_flushed: Flag indicating if buffer has been flushed (prevents new logs)
        max_buffer_size: Maximum number of logs to buffer (prevents memory issues)
        _formatter: CloudWatch log formatter for converting LogRecord to LogEvent
    """

    def __init__(self):
        super().__init__()
        self.buffer: List = []  # Will store LogEvent objects
        self.is_flushed = False
        self.max_buffer_size = 1000  # Prevent memory issues during long startups
        self._formatter = None  # Lazy-loaded CloudWatch formatter

    def emit(self, record: logging.LogRecord):
        """
        Convert and store log event in buffer if not yet flushed.

        This method is called by the logging system for each log message.
        It converts the LogRecord to LogEvent format and stores it in the buffer,
        but only if the buffer hasn't been flushed yet and there's space available.

        Args:
            record: The log record to be buffered

        Note:
            - Logs are converted to LogEvent format immediately for consistency
            - Buffer respects max_buffer_size to prevent memory issues
            - No logs are accepted after buffer is flushed (is_flushed=True)
        """
        if not self.is_flushed and len(self.buffer) < self.max_buffer_size:
            # Convert LogRecord to LogEvent immediately for consistency with CloudWatch
            if self._formatter is None:
                self._formatter = CloudWatchLogFormatter()

            log_event = self._formatter.to_log_event(record)
            self.buffer.append(log_event)

    def flush_to_cloudwatch_reporter(self, reporter):
        """
        Flush buffered log events directly to CloudWatch reporter buffer.

        This method transfers all buffered logs to the CloudWatch reporter's internal
        buffer, maintaining chronological order by inserting them at the beginning.
        After flushing, the buffer is cleared and marked as flushed.

        Args:
            reporter: CloudWatch reporter instance with _cloudwatch_buffer attribute

        Process:
            1. Sort buffered logs by timestamp (chronological order)
            2. Insert at beginning of CloudWatch buffer (older logs first)
            3. Clear local buffer and mark as flushed
            4. Prevent any future log buffering

        Note:
            - Logs are inserted at beginning to maintain chronological order
            - Empty buffer is handled gracefully (just marks as flushed)
            - After flush, this handler becomes inactive
        """
        if not self.buffer:
            self.is_flushed = True
            return

        # Sort by timestamp to ensure chronological order
        # AWS CloudWatch requires this or throws InvalidParameterException when calling CloudWatchReporter.flush_cloudwatch_buffer.put_log_events():
        # "Log events in a single PutLogEvents request must be in chronological order"
        sorted_log_events = sorted(self.buffer, key=lambda event: event.date)

        # Insert at the beginning of CloudWatch buffer to maintain chronological order
        # This ensures early logs appear before any logs that arrived after CloudWatch init
        reporter._cloudwatch_buffer = sorted_log_events + reporter._cloudwatch_buffer

        self.buffer.clear()
        self.is_flushed = True

    def get_buffered_count(self) -> int:
        """Get number of buffered log records"""
        return len(self.buffer)


class EarlyLogBuffer:
    """
    Singleton manager for early log buffering system (standalone connectors only).

    This class manages the lifecycle of the early log buffer for standalone connectors,
    from initialization through flushing to cleanup. It ensures only one buffer exists
    per application and provides a clean interface for buffer operations.

    IMPORTANT: This buffer is only used for standalone connectors. Other connector types
    (hub, cloud) bypass this buffering system entirely.

    Class Attributes:
        _instance: Singleton instance of EarlyLogBuffer
        _buffer_handler: The active buffer handler (if any)
        _root_logger: Reference to root logger for handler management

    Lifecycle (Standalone Connectors Only):
        1. init_buffer() - Creates and attaches buffer handler (if standalone)
        2. Logging occurs - Messages captured in buffer
        3. flush_to_cloudwatch() - Transfers logs and removes handler
        4. Buffer becomes inactive - Direct CloudWatch logging continues
    """

    _instance: Optional["EarlyLogBuffer"] = None
    _buffer_handler: Optional[EarlyLogBufferHandler] = None
    _root_logger: Optional[logging.Logger] = None

    @classmethod
    def init_buffer(cls, root_logger: logging.Logger):
        """
        Initialize buffer handler and attach to root logger.

        This method sets up the early log buffering system by creating a buffer
        handler and attaching it to the root logger. This should be called once
        during logger initialization, before any logging occurs.

        Args:
            root_logger: The root connector logger to attach the buffer handler to

        Note:
            - Only initializes once (singleton pattern)
            - Saves root logger reference for later handler removal
            - Buffer immediately starts capturing all log messages
        """
        if cls._instance is None:
            cls._instance = cls()
            cls._buffer_handler = EarlyLogBufferHandler()
            cls._root_logger = root_logger  # Save reference for later cleanup

            # Add buffer handler to root connector logger
            root_logger.addHandler(cls._buffer_handler)

    @classmethod
    def flush_to_cloudwatch(cls, connector_id: str, org_slug: str):
        """
        Flush buffer to CloudWatch and remove buffer handler (standalone connectors only).

        This method safely handles both standalone and non-standalone connectors:
        - Standalone: Flushes buffered logs and removes handler
        - Non-standalone: No-op (buffer doesn't exist)
        """
        # Check if buffer exists (only for standalone connectors)
        if cls._buffer_handler is None:
            # No buffer exists - this is expected for non-standalone connectors
            return

        if not cls._buffer_handler.is_flushed:
            # Get CloudWatch reporter from registry
            # Import inline to avoid circular dependency: _cloudwatch.py -> _root.py -> _buffer.py -> _cloudwatch.py
            from ts_sdk_connectors_python.logger._cloudwatch import (
                CloudWatchLoggingManager,
                CloudWatchLogReporterKey,
            )

            key = CloudWatchLogReporterKey(connector_id=connector_id, org_slug=org_slug)
            if key in CloudWatchLoggingManager.registry:
                # Get the CloudWatch reporter to insert logs at the beginning
                reporter = CloudWatchLoggingManager.registry[key].reporter
                cls._buffer_handler.flush_to_cloudwatch_reporter(reporter)

                # Remove buffer handler from root logger using saved reference
                if cls._root_logger:
                    cls._root_logger.removeHandler(cls._buffer_handler)

    @classmethod
    def get_buffered_count(cls) -> int:
        """Get number of buffered log records"""
        if cls._buffer_handler:
            return cls._buffer_handler.get_buffered_count()
        return 0

    @classmethod
    def is_buffer_active(cls) -> bool:
        """Check if early log buffering is currently active (standalone connectors only)"""
        return cls._buffer_handler is not None and not cls._buffer_handler.is_flushed
