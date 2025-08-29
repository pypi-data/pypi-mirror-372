import logging
from typing import Any, Optional

# the root module name of the connector sdk, e.g. "ts_sdk_connectors_python"
_root_module_name = __name__.split(".")[0]


class CloudWatchLoggingAdapter(logging.LoggerAdapter):
    """
    A logging adapter that processes log messages to include additional contextual information.

    This adapter moves the `extra` dictionary to the `extra_info` attribute, which is used by the
    `CloudWatchLogFormatter` to format the log record.

    See https://docs.python.org/3/library/logging.html#loggeradapter-objects for more information on LoggingAdapters.

    Attributes:
        logger (logging.Logger): The logger instance to which this adapter is attached.
        extra (dict[str, Any]): Additional contextual information to include in log records.
    """

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """
        Processes the log message and keyword arguments to include the `extra_info` attribute.

        Moves the `extra` dictionary to the `extra_info` attribute, which is used by the
        `CloudWatchLogFormatter` to format the log record.

        For example, calling `log.info("my message", extra={"foo": "bar"})` will result in the LogRecord
        with `record.extra_info == {"foo": "bar"}`. The `extra_info` attribute is used by the `CloudWatchLogFormatter`
        to format the log record.

        :param msg: The log message.
        :param kwargs: The keyword arguments provided to the logger.log, logger.info, logger.debug, etc.
        :return: A tuple containing the processed log message and keyword arguments.
        """

        extra = {"context": self.logger.name}
        extra.update(self.extra or {})
        extra.update(kwargs.get("extra", None) or {})

        if not extra:
            extra = None
        kwargs["extra"] = {"extra_info": extra}

        return msg, kwargs

    def get_child(
        self, suffix: str, extra: Optional[dict[str, Any]] = None
    ) -> "CloudWatchLoggingAdapter":
        """
        Create a child logging adapter.

        Creates a child logging adapter by adding the specified suffix to the logger's name.
        The child adapter inherits the extra contextual information from the parent adapter.

        Example usage:
        ```python
        parent_logger = get_logger("parent_logger", extra={'foo': 'bar'})
        child_logger = parent_logger.get_child("child", extra={'foo': 'baz'})
        child_logger.info("This is a message from the child logger")
        ```

        :param suffix: The suffix to add to the logger's name.
        :return: A new CloudWatchLoggingAdapter instance with the updated logger name.
        """
        merged_extra = {}
        merged_extra.update(self.extra or {})
        merged_extra.update(extra or {})
        return self.__class__(
            logger=self.logger.getChild(suffix=suffix), extra=merged_extra
        )


def get_root_module_name() -> str:
    """Return the root module name of the connector sdk"""
    return _root_module_name


def get_logger_name(name: str, name_prefix=None) -> str:
    """
    Get a logger name with the proper prefix.

    :param name: The name of the logger
    :param name_prefix: Optional prefix to add to the logger name
    :return: The prefixed logger name
    """
    if name_prefix is None:
        name_prefix = get_root_module_name()
    if not name.startswith(name_prefix):
        name = f"{name_prefix}.{name}"
    return name


def get_logger(
    name: str,
    extra: Optional[dict[str, str]] = None,
    name_prefix: Optional[str] = None,
) -> CloudWatchLoggingAdapter:
    """
    Get a new child logger for the connector or its components. The returned logger
    will always be a child of the root connector sdk logger "ts_sdk_connectors_python".

    .. code-block::

        logger = get_logger("my_logger")
        logger.info("This is an info message")

        logger.error("This is an error message with extra information", extra={"extra": "values"})
    """
    logger_name = get_logger_name(name, name_prefix=name_prefix)
    logger = logging.getLogger(logger_name)
    adapter = CloudWatchLoggingAdapter(logger, extra=extra)
    return adapter
