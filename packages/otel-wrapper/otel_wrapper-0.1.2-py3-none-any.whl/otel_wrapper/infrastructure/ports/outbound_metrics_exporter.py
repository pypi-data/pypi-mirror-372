from abc import ABC, abstractmethod
from typing import Optional, Dict, List


class iMetricsExporter(ABC):
    @abstractmethod
    def metric_increment(self, name: str, tags: dict, value: float):
        """Increment a counter metric by the specified value."""
        pass

    @abstractmethod
    def record_gauge(self, name: str, tags: dict, value: float):
        """Record a specific value for a gauge metric."""
        pass

    @abstractmethod
    def record_histogram(self, name: str, tags: dict, value: float):
        """Record a value to be aggregated in a histogram metric."""
        pass
