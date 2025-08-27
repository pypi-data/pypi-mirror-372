from .builder import Wrapper
from .domain.services.trace_service import TraceProcessorService
from .domain.services.logs_service import LogsProcessorService
from .domain.services.metrics_service import MetricsProcessorService
from .infrastructure.adapters.log_exporter import LogExporterAdapter
from .infrastructure.adapters.metrics_exporter import MetricsExporterAdapter
from .infrastructure.adapters.trace_exporter import TraceExporterAdapter


def wrapper_builder(application_name: str) -> Wrapper:
    _trace_exporter = TraceExporterAdapter(application_name=application_name)
    _log_exporter = LogExporterAdapter(application_name=application_name)
    _metrics_exporter = MetricsExporterAdapter(application_name=application_name)

    _trace_service = TraceProcessorService(trace_exporter=_trace_exporter)
    _log_service = LogsProcessorService(log_exporter=_log_exporter)
    _metrics_service = MetricsProcessorService(metric_exporter=_metrics_exporter)

    wrapper = Wrapper(
        trace_service=_trace_service,
        log_service=_log_service,
        metrics_service=_metrics_service,
    )

    return wrapper
