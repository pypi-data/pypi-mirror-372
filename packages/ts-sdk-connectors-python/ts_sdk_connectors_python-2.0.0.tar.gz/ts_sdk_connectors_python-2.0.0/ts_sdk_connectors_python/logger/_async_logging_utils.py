import asyncio
import inspect
import logging
import queue as queuelib
import threading
from abc import ABC, abstractmethod
from logging.handlers import QueueListener

logger = logging.getLogger("async_threaded_logger")
logger.setLevel(logging.DEBUG)


class AsyncHandlerABC(logging.Handler, ABC):
    """Async version of a logging.Handler with async implementations of `emit` and `handle`"""

    @abstractmethod
    async def emit(self, record: logging.LogRecord) -> None:
        pass

    async def handle(self, record: logging.LogRecord) -> logging.LogRecord:
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
                result = self.emit(record)
                if inspect.isawaitable(result):
                    await result
            finally:
                self.release()
        return rv


# number of consecutive log failures before giving up on the handler
DEFAULT_MAX_CRITICAL_LOG_FAILURES = 5


class ThreadedAsyncQueueListener(QueueListener):
    def __init__(
        self,
        queue: asyncio.Queue,
        *handlers: AsyncHandlerABC | logging.Handler,
        respect_handler_level=False,
        async_handler_timeout: int = 30,
        max_consecutive_errors_threshold: int = DEFAULT_MAX_CRITICAL_LOG_FAILURES,
    ):
        """
        Instance of the async log queue listener.

        :param queue: The log queue
        :param handlers: Log handlers to run when a log record is dequeued.
        :param respect_handler_level:
        :param async_handler_timeout: Timeout (in seconds) for async log handlers.
        :param max_consecutive_errors_threshold: Maximum number of consecutive listener failures before killing the
            listener.
        """
        super().__init__(queue, *handlers, respect_handler_level=respect_handler_level)
        self.async_handler_timeout = async_handler_timeout
        self.max_consecutive_errors_threshold = max_consecutive_errors_threshold

    @property
    def async_handlers(self) -> list[logging.Handler]:
        return [
            handler
            for handler in self.handlers
            if inspect.iscoroutinefunction(handler.handle)
        ]

    @property
    def sync_handlers(self) -> list[logging.Handler]:
        return [
            handler
            for handler in self.handlers
            if not inspect.iscoroutinefunction(handler.handle)
        ]

    def dequeue(self, block: bool):
        self.queue: queuelib.SimpleQueue
        # a small timeout throttles the log queue (>1000 logs a second would be alot of logs)
        # if the queue is empty, `Empty` is thrown and handled in the `monitor_queue` method
        return self.queue.get(block, timeout=0.001)

    def start(self):
        """
        Start the listener.

        This starts up a background thread to monitor the queue for
        LogRecords to process.
        """
        self._thread = t = threading.Thread(target=self._monitor)
        t.daemon = True
        t.start()

    def _monitor(self):
        """Overrides the QueueListener._monitor method to monitor to run the
        loop coroutine. This operates on its own thread and so does not interfere
        with main thread's event loop.

        See `start` for how this thread is initialized."""
        asyncio.run(self.loop())

    async def loop(self):
        self._task = asyncio.create_task(self.monitor_queue())
        while True:
            await asyncio.sleep(1)

    async def monitor_queue(self):
        """
        Monitors the queue for new log records.

        :return:
        """
        q = self.queue
        has_task_done = hasattr(q, "task_done")
        critical_failures = 0
        while True:
            # sleeping is required to yield the event loop to other coroutines/tasks
            # sleeping '0' is standard practice
            await asyncio.sleep(0)

            # collect the record from the queue and handle any errors
            # many consecutive errors indicates there is a critical issue with how
            # logs are being collected on the queue. After a threshold of errors
            record = None
            try:
                record = self.dequeue(True)
            except (queuelib.Empty, asyncio.QueueEmpty):
                # if queue is empty, continue polling
                continue
            except Exception as e:
                critical_failures += 1
                msg = f"There was a error with collecting logs on the log queue (failures: {critical_failures})"
                if e.args:
                    msg += e.args[0]
                else:
                    msg += str(e)
                logger.error(msg, exc_info=True)

                if critical_failures >= self.max_consecutive_errors_threshold:
                    logger.critical(
                        f"Too many consecutive log failures ({critical_failures}). Stopping logging handler.",
                        exc_info=True,
                    )
                    self.stop()
                await asyncio.sleep(critical_failures)

            # handle the log record
            if record is None:
                continue
            try:
                if inspect.isawaitable(record):
                    record = await record
                if record is self._sentinel:
                    if has_task_done:
                        q.task_done()
                    break
                await self.handle(record)
                critical_failures = 0
            except Exception as e:
                msg = "Error handling record: "
                if e.args:
                    msg += e.args[0]
                else:
                    msg += str(e)
                logger.error(msg, exc_info=True)

    async def handle(self, record: logging.LogRecord):
        """
        Handle a record.

        This just loops through the handlers offering them the record
        to handle. If the handler is async, create an async task. All
        tasks are awaited at the end.
        """
        record = self.prepare(record)

        sync_handlers = []
        async_handlers = []
        for handler in self.handlers:
            if not self.respect_handler_level:
                process = True
            else:
                process = record.levelno >= handler.level
            if process:
                if inspect.iscoroutinefunction(handler.handle):
                    async_handlers.append(handler)
                else:
                    sync_handlers.append(handler)

        tasks = []
        for handler in async_handlers:
            tasks.append(asyncio.create_task(handler.handle(record)))
        for handler in sync_handlers:
            handler.handle(record)

        # wait for task to complete, this should never take a very long time since we would
        # block log reporting, hence the 5-second timeout here
        for t in tasks:
            await asyncio.wait_for(t, self.async_handler_timeout)
