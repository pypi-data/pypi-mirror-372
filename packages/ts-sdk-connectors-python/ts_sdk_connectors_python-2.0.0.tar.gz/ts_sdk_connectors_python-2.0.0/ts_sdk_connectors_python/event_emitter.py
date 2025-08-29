import asyncio
import inspect
from asyncio import Task
from typing import Any, Callable, Generic, TypeAlias, TypeVar

from ts_sdk_connectors_python.logger import get_logger
from ts_sdk_connectors_python.utils import TaskManager

logger = get_logger(__name__)


T = TypeVar("T")

_EVENTS_EMITTER_TASK_NAME = "events_emitter_task"


class Event(Generic[T]):
    def __init__(self, *, event_type: str, data: T):
        self._event_type = event_type
        self._data = data

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def data(self) -> T:
        return self._data

    def __repr__(self):
        return f"Event({self.event_type}, {self.data})"

    def __str__(self):
        return self.__repr__()


T = TypeVar("T")
EventCallback: TypeAlias = Callable[[T], Any]


class EventsEmitter(Generic[T]):
    def __init__(self):
        self.queue = asyncio.Queue()
        self._listeners: dict[str, list[Callable[[T], Any]]] = {}
        self.task_manager = TaskManager()

    def add_listener(self, event_type: str, callback: Callable[[T], Any]):
        logger.info('Adding listener for "%s" events', event_type)
        self._listeners.setdefault(event_type, []).append(callback)

    async def listen_to_events_loop(self, queue: asyncio.Queue):
        while True:
            event: Event[T] = await queue.get()
            logger.info('Handling event "%s"', event)
            if event.event_type in self._listeners:
                for callback in self._listeners[event.event_type]:
                    try:
                        result = callback(event.data)
                        if inspect.isawaitable(result):
                            await result
                    except Exception as exc:
                        logger.error(
                            "error running event callback on %s", event, exc_info=exc
                        )
            else:

                logger.info("No listeners found for %s", event)

    def start(self) -> Task:
        logger.debug("Starting events listener")
        return self.task_manager.create_task(
            self.listen_to_events_loop(queue=self.queue), _EVENTS_EMITTER_TASK_NAME
        )

    def stop(self):
        self.task_manager.cancel(_EVENTS_EMITTER_TASK_NAME)

    async def emit(self, event_type: str, data: T):
        logger.info("Emitting event %s", data)
        await self.queue.put(Event(event_type=event_type, data=data))
