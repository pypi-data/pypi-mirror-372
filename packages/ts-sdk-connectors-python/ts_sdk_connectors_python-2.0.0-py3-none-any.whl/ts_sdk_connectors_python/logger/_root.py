import logging
from logging import StreamHandler

from ts_sdk_connectors_python.client_creator import is_standalone
from ts_sdk_connectors_python.logger._base import get_logger, get_root_module_name
from ts_sdk_connectors_python.logger._buffer import EarlyLogBuffer
from ts_sdk_connectors_python.logger._cloudwatch_utils import CloudWatchLogFormatter

# Internal logger for the module
internal_logger = get_logger(__name__)

# Default log level for the connector SDK
DEFAULT_CONNECTOR_LOG_LEVEL: str = logging.getLevelName(logging.DEBUG)


def init_stream_handler():
    """Initialize a stream handler with CloudWatch formatter"""
    stream_handler = StreamHandler()
    stream_handler.setFormatter(CloudWatchLogFormatter())
    return stream_handler


# Create a logger for the connector SDK
root_connector_logger = logging.getLogger(get_root_module_name())


def init_root_connector_logger():
    """Initialize the root connector logger"""
    logging.basicConfig(handlers=[init_stream_handler()], force=True)
    root_connector_logger.handlers.clear()
    root_connector_logger.setLevel(DEFAULT_CONNECTOR_LOG_LEVEL)

    # Initialize early log buffer to capture logs before CloudWatch is ready
    _init_early_log_buffer()


def _init_early_log_buffer():
    """Initialize early log buffer handler only for standalone connectors"""
    try:
        if not is_standalone():
            internal_logger.debug(
                "Skipping early log buffer - connector does not appear to be running in standalone mode"
            )
            return

        EarlyLogBuffer.init_buffer(root_connector_logger)
        internal_logger.debug("Early log buffer initialized for standalone connector")
    except Exception as e:
        internal_logger.warning(f"Failed to initialize early log buffer: {e}")


# Initialize root logger
init_root_connector_logger()


def get_root_connector_sdk_logger() -> logging.Logger:
    """
    Get the root logger for the TetraScience Connector SDK.

    This function returns the root logger instance for the TetraScience Connector SDK. The root logger
    is configured to use the `CloudWatchLogFormatter` and logs messages to the console.

    .. code-block:: python

        logger = get_root_connector_sdk_logger()
        logger.info("This is an info message")

    :return: The root logger instance for the TetraScience Connector SDK.
    """
    return root_connector_logger


def set_root_connector_sdk_log_level(level: str | int):
    """
    Set the log level for the root connector SDK logger.

    This function sets the log level for the root connector SDK logger to the specified level.
    The log level can be one of the standard logging levels: 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.

    Example usage:

    .. code-block:: python

        set_root_connector_sdk_log_level("DEBUG")


    :param level: The name of the log level to set (e.g., 'DEBUG', 'INFO').
    :return: The root connector SDK logger instance.
    """
    logger = get_root_connector_sdk_logger()
    if isinstance(level, str):
        level = level.upper()
    logger.setLevel(level)


def reset_root_connector_sdk_log_level() -> None:
    """Reset the root connector SDK logger level to the default level."""
    set_root_connector_sdk_log_level(DEFAULT_CONNECTOR_LOG_LEVEL)
