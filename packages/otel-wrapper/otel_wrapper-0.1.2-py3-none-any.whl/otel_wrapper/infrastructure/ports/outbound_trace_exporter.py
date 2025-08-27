from abc import ABC, abstractmethod
from opentelemetry.sdk.trace import Tracer


class iTracesExporter(ABC):
    @abstractmethod
    def get_tracer(self) -> Tracer:
        pass
