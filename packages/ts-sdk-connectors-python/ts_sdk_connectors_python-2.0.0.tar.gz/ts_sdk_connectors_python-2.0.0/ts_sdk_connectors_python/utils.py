import asyncio
import http.client
import inspect
import json
import logging
import time
from asyncio import Task
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from logging import LoggerAdapter
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
)
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)


def utc_time(*, days=0, hours=0, minutes=0, seconds=0) -> datetime:
    """
    Return utc datetime. If kwargs provided, add timedelta to the datetime.

    :param days: Days from now to return
    :param hours: Hours from now to return
    :param minutes: Minutes from now to return
    :param seconds: Seconds from now to return
    :return: Datetime in utc timezone
    """
    return datetime.now(timezone.utc) + timedelta(
        days=days, hours=hours, minutes=minutes, seconds=seconds
    )


class TaskManager:
    def __init__(self):
        """
        Manages async tasks. Maintains a reference set to tasks created/added and automatically
        adds a done callback function that removes the task from the reference set.

        Using the task manager ensures that python's garbage collection does not
        erroneously remove the async task if the task reference is lost. You *must* maintain a
        reference to a task somewhere in the program in order to keep the task alive.
        """
        self._tasks: set[Task] = set()

    def create_task(self, coroutine: Coroutine, name: str) -> Task:
        """
        Create a task from a coroutine.

        :param coroutine: The coroutine to create.
        :param name: The name of the task.
        :return:
        """
        task = asyncio.create_task(coroutine, name=name)
        return self.add_task(task)

    def cancel(self, task_name: str):
        for task in self._tasks:
            if task.get_name() == task_name:
                if not task.cancelled():
                    task.cancel()
                break

    def add_task(self, task: Task) -> Task:
        """
        Add a task to the manager.

        :param task: The task to add.
        :return: The added task.
        """
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def cancel_all(self):
        """
        Cancel all tasks

        :return:
        """
        for task in self._tasks:
            task.cancel()

    def __len__(self):
        return len(self._tasks)


async def async_interval_iter(interval: float, min_sleep: float = 0):
    """
    Async generator that yields on a timed interval.

    Example usage:

    .. code-block::

        async def run_interval():
            start = time.time()
            async for i in forever_interval(0.8):
                print(i, time.time() - start)

        async def main():
            asyncio.create_task(run_interval())
            await asyncio.sleep(3)

        asyncio.run(main())

    :param interval: interval in seconds
    :param min_sleep: minimum sleep time in seconds
    :return:
    """
    curr_loop_index = 0

    start_time: float = time.monotonic()
    while True:
        yield curr_loop_index
        end_time: float = time.monotonic()
        delay = max(min_sleep, interval - (end_time - start_time))
        await asyncio.sleep(delay)
        curr_loop_index += 1
        start_time = time.monotonic()


def asyncio_has_task(task_name: str) -> bool:
    """
    Returns whether an asyncio task with the provided name exists

    :param task_name: The task name
    :return: True if an asyncio task exists
    """
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            return True
    return False


def get_public_cls_attrs(class_: Type) -> list[str]:
    """Get the class attributes of a class."""
    return [
        a
        for a in dir(class_)
        if not a.startswith("_") and not callable(getattr(class_, a))
    ]


class Unset:
    """Object representing an unset attribute."""

    def __bool__(self) -> Literal[False]:
        return False


UNSET = Unset()
T = TypeVar("T")


class PollStopReason(StrEnum):

    NOT_STOPPED = ""
    UNTIL_CONDITION_MET = "until_condition_met"
    TIMEOUT = "timeout"
    NUM_LOOPS_EXCEEDED = "num_loops_exceeded"
    MANUALLY_STOPPED = "manually_stopped"
    TASK_CANCELED = "task_canceled"
    EXCEPTION_RAISED = "exception_raised"


class PollStatus(StrEnum):

    NEVER_STARTED = "never_started"
    STARTED = "started"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


class Poll(Generic[T]):
    def __init__(
        self,
        target: Callable[..., T],
        interval: int | float,
        *,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        until: Optional[Callable[[T], bool]] = None,
        poll_time_limit: Optional[int | float] = None,
        n_times: Optional[int] = None,
        initial_delay: Optional[float | int | bool] = None,
        on_error: Optional[Callable[[Exception], Any]] = None,
        on_timeout_raise: bool = False,
        name: Optional[str] = None,
    ):
        """
        Create an interval poll for a target method.

        :param target: Target function
        :param interval: Interval in seconds
        :param args: Positional arguments for the target function
        :param kwargs: Keyword arguments for the target function
        :param until: Callback function to poll until, if provided. Takes in one argument, the result of the target
            and if it returns True, polling will stop.
        :param poll_time_limit: Max length for the poll to run in seconds. Optional.
        :param n_times: Max number of times to poll. Optional.
        :param initial_delay: Initial delay in seconds for the poll. If true, uses the interval. Optional.
        :param name: Name of the poll. If a task name is not provided on `start` call, the poll name will be used
            as the task name.
        :param on_error: Callback function in case target raises an exception. Takes one argument, the exception. If
            not provided or is `None`, this defaults logging the exception. If it is desired to stop the poll on an
            exception provide `on_error` callback that raises an exception.
        :param on_timeout_raise: If True, raise TimeoutError within the inner asyncio poll loop.
        """
        self.last_result: Unset | T = UNSET
        self.target = target
        self.args = args or tuple()
        self.kwargs = kwargs or {}
        self.interval = interval
        self.poll_time_limit = poll_time_limit
        self.n_times = n_times
        self.until = until
        if initial_delay is True:
            initial_delay = self.interval
        self.initial_delay = initial_delay
        self.name = name
        self.logger = self._create_logger()
        if on_error is None:
            on_error = lambda exc: self.logger.error(str(exc), exc_info=True)
        self.on_error = on_error
        self.on_timeout_raise = on_timeout_raise
        self.status: PollStatus = PollStatus.NEVER_STARTED
        self.reason: PollStopReason = PollStopReason.NOT_STOPPED
        self._task: Optional[asyncio.Task] = None

    def _create_logger(self) -> LoggerAdapter:
        """Create a new polling logger."""
        logger_name = self.name or str(uuid4())[:6]
        inst_logger = logger.getChild(f"Poll.{logger_name}")
        adapter = LoggerAdapter(
            inst_logger,
            {
                "extra_info": {
                    "context": inst_logger.name,
                }
            },
        )
        return adapter

    async def _poll_loop(self):
        """The inner polling loop"""
        self.status = PollStatus.RUNNING
        self.reason = PollStopReason.NOT_STOPPED
        if self.initial_delay:
            await asyncio.sleep(self.initial_delay)
        t1 = time.time()
        async for i in async_interval_iter(self.interval):
            if self.status != PollStatus.RUNNING:
                break
            if (
                self.poll_time_limit is not None
                and time.time() - t1 > self.poll_time_limit
            ):
                self._stop(PollStopReason.TIMEOUT)
                if self.on_timeout_raise:
                    raise TimeoutError(f"Poll terminated due to timeout: {self}")
                break
            if self.n_times is not None and i >= self.n_times:
                self._stop(PollStopReason.NUM_LOOPS_EXCEEDED)
                break
            try:
                result = self.target(*self.args, **self.kwargs)
                if inspect.isawaitable(result):
                    result = await result
            except Exception as e:
                if self.on_error:
                    try:
                        error_result = self.on_error(e)
                    except Exception as inner_exc:
                        self._stop_and_fail()
                        raise inner_exc
                    if inspect.isawaitable(error_result):
                        await error_result
                    continue
            self.last_result = result
            if self.until is not None and self.until(result):
                self._stop(PollStopReason.UNTIL_CONDITION_MET)
                break

    def start(self, name: Optional[str] = None) -> Task:
        """
        Start the poll by creating an asyncio.Task. Return the task.

        :param name: Optional name of the task. If not provided, uses the name of the Poll object.
        :return: The asyncio task
        """
        if self.status != PollStatus.NEVER_STARTED:
            raise RuntimeError("Cannot start poll that has already started")
        self.status = PollStatus.STARTED
        self._task = asyncio.create_task(self._poll_loop(), name=self.name or name)
        self._task.add_done_callback(lambda _: self._cancel_task_cb())
        return self._task

    async def wait(self):
        """
        Start and wait for the poll to terminate.

        :return: The last result of the target function.
        """
        if self.status == PollStatus.NEVER_STARTED:
            self.start()
        await self._task
        return self.last_result

    def _cancel_task_cb(self):
        """Callback for when the polling asyncio task is canceled manuall. If
        the status isn't already"""
        if self.status not in [PollStatus.STOPPED, PollStatus.FAILED]:
            self._stop(PollStopReason.TASK_CANCELED)

    def _stop(self, reason: PollStopReason):
        self.status = PollStatus.STOPPED
        self.reason = reason
        self.logger.debug("Stopping Poll", extra={"extra_info": {"reason": reason}})

    def _stop_and_fail(self):
        self._stop(PollStopReason.EXCEPTION_RAISED)
        self.status = PollStatus.FAILED

    def stop(self):
        """
        Stop the poll manually.

        This will:
        1. Set the poll's status to STOPPED
        2. Set the stop reason to MANUALLY_STOPPED
        3. Cancel the underlying asyncio task
        4. Clean up the task reference
        """
        self._stop(PollStopReason.MANUALLY_STOPPED)
        self._task.cancel()
        self._task = None

    @property
    def started(self) -> bool:
        """
        Returns True if the poll has been initiated (status is either STARTED or RUNNING).

        This means the poll has been started but may not yet be executing its first iteration.
        """
        return self.status in [PollStatus.STARTED, PollStatus.RUNNING]

    @property
    def stopped(self) -> bool:
        """
        Returns True if the poll has been explicitly stopped (status is STOPPED).
        """
        return self.status == PollStatus.STOPPED

    @property
    def failed(self) -> bool:
        """
        Returns True if the poll has failed due to an unhandled exception (status is FAILED).
        """
        return self.status == PollStatus.FAILED

    @property
    def running(self) -> bool:
        """
        Returns True if the poll is actively executing its polling loop (status is RUNNING).
        """
        return self.status == PollStatus.RUNNING

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}>("
            f"name='{self.name}', interval='{self.interval}', target='{self.target.__name__}' "
            f"status='{self.status}', reason='{self.reason}')>)"
        )


def poll_forever(
    target: Callable[..., T],
    interval: int | float,
    *,
    args: tuple[Any, ...] = None,
    kwargs: dict[str, Any] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    poll_name: Optional[str] = None,
) -> Task:
    """
    Poll a target forever on an interval.

    :param target: Target function
    :param interval: Interval in seconds
    :param args: Positional arguments for the target function
    :param kwargs: Keyword arguments for the target function
    :param poll_name: Optional name of the poll. Will be used as the asyncio task name.
    :param on_error: Callback function in case target raises an exception. Takes one argument, the exception.
        If not provided, defaults to logging the exception.
    """
    return Poll(
        target, interval, args=args, kwargs=kwargs, on_error=on_error, name=poll_name
    ).start()


def unique_list(items: list[T]) -> list[T]:
    """Make a list of unique items and maintain order."""
    return list(OrderedDict.fromkeys(items))


def json_dump_condensed(data: Any) -> str:
    return json.dumps(data, separators=(",", ":"))


def calculate_size_in_bytes(value: None | str | float | int | list | dict) -> int:
    if value is None:
        return 0
    if not isinstance(value, str):
        value_str = json_dump_condensed(value)
    else:
        value_str = value
    return len(value_str.encode("utf-8"))


def text_shorten(text: str, max_size: int, placeholder: str = "[...]"):
    """Shorten a long text adding a placeholder in the middle if it surpasses the specified max size.

    `some really long[...]and we are done`
    """
    if len(text) > max_size:
        first_part_length = int(max_size / 2) - len(placeholder)
        remaining_length = max_size - first_part_length
        return text[:first_part_length] + placeholder + text[-remaining_length:]
    return text


def to_js_isoformat(date: Optional[datetime] = None) -> str:
    """Utility function to match javascript's Date.toIsoString, which outputs
    a string format similar to '2025-02-18T18:05:11.899Z'
    """
    if date is None:
        date = datetime.now(tz=timezone.utc)
    date = date.astimezone(timezone.utc)
    return date.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def extract_request_id(
    obj: Union[Exception, httpx.Response, http.client.HTTPResponse]
) -> Optional[str]:
    """
    Extract ts-request-id from an exception or httpx.Response if available.

    Checks for the ts-request-id in:
    1. The exception's headers attribute (UnexpectedStatus)
    2. The exception's response headers (httpx.HTTPStatusError)
    3. Directly from httpx.Response or http.client.HTTPResponse headers

    Args:
        obj: The exception or response to extract the request ID from

    Returns:
        str or None: The ts-request-id if found, None otherwise

    # NOTE: This function has been simplified based on actual usage patterns.
    # We've kept only the code paths that are known to be used or likely to be used.
    #
    # We considered checking for ts-request-id in exception.__cause__, but decided
    # against it for simplicity. If this becomes necessary in the future, it can be re-added.
    # The test cases have been updated to directly use the exception types that this
    # function is designed to handle.
    """
    if isinstance(obj, httpx.Response):
        return obj.headers.get("ts-request-id")

    if isinstance(obj, http.client.HTTPResponse):
        return obj.getheader("ts-request-id")

    # Try to get from exception's headers (UnexpectedStatus)
    if hasattr(obj, "headers"):
        try:
            request_id = obj.headers.get("ts-request-id")
            if request_id:
                return request_id
        except (AttributeError, TypeError):
            pass

    # Try to get from exception's response headers (httpx.HTTPStatusError)
    if hasattr(obj, "response") and hasattr(obj.response, "headers"):
        try:
            request_id = obj.response.headers.get("ts-request-id")
            if request_id:
                return request_id
        except (AttributeError, TypeError):
            pass

    # No ts-request-id found
    return None
