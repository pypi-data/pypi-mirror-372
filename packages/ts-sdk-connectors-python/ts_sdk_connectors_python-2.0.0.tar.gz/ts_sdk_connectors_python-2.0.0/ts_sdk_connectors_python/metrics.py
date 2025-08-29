from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Awaitable, Callable, Generic, Optional, TypeAlias, TypeVar

import psutil
from pydantic import BaseModel, Field

from ts_sdk_connectors_python.logger import get_logger
from ts_sdk_connectors_python.utils import TaskManager, poll_forever

logger = get_logger(__name__)

T = TypeVar("T")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class DataPoint(BaseModel, Generic[T], extra="forbid"):
    value: T = Field(frozen=True)
    time: datetime = Field(default_factory=now_utc, frozen=True)


class MetricDataPoint(BaseModel, Generic[T], extra="forbid"):
    name: str = Field(frozen=True)
    unit: str = Field(frozen=True)
    point: DataPoint[T] = Field(frozen=True)


class RegisterMetricsOptions(BaseModel, extra="forbid"):

    interval: float = Field(30.0, frozen=True, description="Interval in seconds")


class MetricsCollectorOptions(BaseModel, extra="forbid"):

    batch_size: int = Field(10, frozen=True)


class MetricsProvider(ABC):
    def __init__(self, *, name: str, unit: str):
        """
        Provides a metric (cpu, mem usage, etc.).

        :param name: name of the metric
        :param unit: unit of the metric
        """
        self._name = name
        self._unit = unit

    @property
    def name(self) -> str:
        return self._name

    @property
    def unit(self) -> str:
        return self._unit

    def new_metric_data_point(self, value: T) -> MetricDataPoint[T]:
        return MetricDataPoint(
            name=self.name, unit=self.unit, point=DataPoint(value=value)
        )

    @abstractmethod
    def get_metric(self) -> MetricDataPoint:
        raise NotImplementedError()


class CpuMetricsProvider(MetricsProvider):
    def __init__(self, cpu_interval: None | float | int = 1.0):
        """
        Provides cpu percentage metric.

        :param cpu_interval: Interval at which the cpu percentage is evaluated. Measuring cpu percentage is a *blocking*
                             method. See :meth:`psutil.cpu_percent` for more information.
        """
        super().__init__(name="cpu_usage", unit="Percent")
        self._cpu_interval = cpu_interval

    def get_metric(self) -> MetricDataPoint[float]:
        cpu_perc = psutil.cpu_percent(interval=self._cpu_interval, percpu=False)
        return self.new_metric_data_point(cpu_perc)


class MemoryAvailableProvider(MetricsProvider):
    def __init__(self):
        """
        Provides memory available metric
        """
        super().__init__(name="memory_total", unit="Bytes")

    def get_metric(self) -> MetricDataPoint[int]:
        mem = psutil.virtual_memory()
        total_memory = mem.total
        return self.new_metric_data_point(total_memory)


class MemoryUsedProvider(MetricsProvider):
    def __init__(self):
        super().__init__(name="memory_used", unit="Bytes")

    def get_metric(self) -> MetricDataPoint[int]:
        mem = psutil.virtual_memory()
        free_memory = mem.free
        return self.new_metric_data_point(free_memory)


ExporterType: TypeAlias = Callable[[list[MetricDataPoint]], Awaitable[None]]


class MetricsCollector:
    def __init__(
        self, exporter: ExporterType, options: Optional[MetricsCollectorOptions] = None
    ):
        """
        A class that allows asynchronous collection of metrics (cpu, available mem, etc.) and batched export
        of collected metrics.

        :param exporter: The async exporter function for metrics. Consumes a list of :class:`MetricDataPoint`.
        :param options: Options for the metrics collection
        """
        self._providers: list[MetricsProvider] = []
        self._provider_options: list[RegisterMetricsOptions] = []
        self.exporter = exporter
        self.metrics: list[MetricDataPoint] = []
        self.task_manager = TaskManager()
        self.options: MetricsCollectorOptions = options or MetricsCollectorOptions()

    @property
    def providers(self) -> tuple[MetricsProvider, ...]:
        """
        Returns the metrics providers

        :return: Tuple of the metrics providers
        """
        return tuple(self._providers)

    @property
    def provider_options(self) -> tuple[RegisterMetricsOptions, ...]:
        """
        Returns the metrics provider options

        :return: Tuple of the metrics provider options
        """
        return tuple(self._provider_options)

    async def _get_metrics_and_export(self, provider: MetricsProvider):
        """
        An async function for collecting and exporting metrics on an interval.

        :param provider: The metrics provider
        :param options: The metrics provider options
        :return: None
        """
        try:
            self.metrics.append(provider.get_metric())
            if len(self.metrics) >= self.options.batch_size:
                await self.export()
        except Exception as exception:
            logger.error("Error while exporting metrics", exc_info=exception)

    def start(self):
        """
        Start metrics collection. In order to have the async metrics collections execute,
        this must be called in an async function.

        :return: None
        """
        for provider, provider_options in zip(self.providers, self.provider_options):
            task_name = f"{provider.name}_metrics_provider"
            logger.info(f"Starting metrics task: {task_name}")
            task = poll_forever(
                self._get_metrics_and_export,
                interval=provider_options.interval,
                poll_name=task_name,
                args=(provider,),
            )
            self.task_manager.add_task(task)

    async def export(self):
        """
        Call the exporter on the currently collected metrics and then clear metrics.
        :return:
        """
        await self.exporter(self.metrics[:])
        self.metrics.clear()

    def stop(self):
        """
        Cancel all async tasks

        :return:
        """
        self.task_manager.cancel_all()

    def register_provider(
        self,
        provider: MetricsProvider,
        options: Optional[RegisterMetricsOptions] = None,
    ):
        """
        Register a metrics provider.

        :param provider: The metrics provider
        :param options: The metrics provider options
        :return: None
        """
        options = options or RegisterMetricsOptions()
        self._provider_options.append(options)
        self._providers.append(provider)
