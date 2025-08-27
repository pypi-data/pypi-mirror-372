from .domain.services.logs_service import LogsProcessorService
from .domain.services.metrics_service import MetricsProcessorService
from .domain.services.trace_service import TraceProcessorService


class Wrapper:
    def __init__(
        self,
        trace_service: TraceProcessorService,
        log_service: LogsProcessorService,
        metrics_service: MetricsProcessorService,
    ):
        self._trace_service = trace_service
        self._log_service = log_service
        self._metrics_service = metrics_service

    def traces(self):
        return self._trace_service

    def logs(self):
        return self._log_service

    def metrics(self):
        return self._metrics_service
