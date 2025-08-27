from ...infrastructure.ports.outbound_metrics_exporter import iMetricsExporter


class MetricsProcessorService:
    def __init__(self, metric_exporter: iMetricsExporter):
        self._exporter = metric_exporter

    def metric_increment(self, name: str, tags: dict, value: float = 1.0):
        """Increment a counter metric by the specified value (defaults to 1.0)."""
        self._exporter.metric_increment(name=name, tags=tags, value=value)

    def record_gauge(self, name: str, tags: dict, value: float):
        """Record a specific value for a gauge metric."""
        self._exporter.record_gauge(name=name, tags=tags, value=value)

    def record_histogram(self, name: str, tags: dict, value: float):
        """Record a value to be aggregated in a histogram metric."""
        self._exporter.record_histogram(name=name, tags=tags, value=value)
