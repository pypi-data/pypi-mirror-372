import os
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, DEPLOYMENT_ENVIRONMENT
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import get_meter
from ...infrastructure.ports.outbound_metrics_exporter import iMetricsExporter
from ...domain.dto.application_attributes import ApplicationAttributes


class MetricsExporterAdapter(iMetricsExporter):
    DEFAULT_ENDPOINT: str = "https://o11y-proxy.ivanildobarauna.dev/"
    _instance = None

    def __new__(cls, application_name: str):
        if cls._instance is None:
            cls._instance = super(MetricsExporterAdapter, cls).__new__(cls)
            cls._instance._initialize(application_name)
        return cls._instance

    def _initialize(self, application_name: str):
        try:
            # Initialize application attributes with custom configuration
            self.application_attributes = ApplicationAttributes(
                application_name=application_name
            )

            # Get the metrics-specific endpoint
            self.exporter_endpoint = os.getenv(
                "OTEL_EXPORTER_OTLP_ENDPOINT", self.DEFAULT_ENDPOINT
            )

            # Create resource with application attributes
            self.resource = Resource.create(
                attributes={
                    SERVICE_NAME: self.application_attributes.application_name,
                    DEPLOYMENT_ENVIRONMENT: self.application_attributes.environment,
                }
            )

            # Create metrics exporter with endpoint
            try:
                metric_exporter = OTLPMetricExporter(
                    endpoint=self.exporter_endpoint, timeout=10
                )
                self.reader = PeriodicExportingMetricReader(exporter=metric_exporter)

                # Create meter provider with resource and reader
                self.provider = MeterProvider(
                    resource=self.resource, metric_readers=[self.reader]
                )

                # Get meter instance
                self.meter = get_meter(
                    f"meter-{self.application_attributes.application_name}",
                    meter_provider=self.provider,
                )
            except Exception as e:
                print(f"Warning: Failed to initialize OTLP metrics exporter: {str(e)}")
                # Fallback to basic meter provider
                self.provider = MeterProvider(resource=self.resource)
                self.meter = get_meter(
                    f"fallback-{self.application_attributes.application_name}",
                    meter_provider=self.provider,
                )
        except Exception as e:
            print(f"Error initializing metrics exporter: {str(e)}")
            # Ensure we at least have a meter
            self.provider = MeterProvider()
            self.meter = get_meter("default")

    def metric_increment(self, name: str, tags: dict, value: float):
        """Increment a counter metric by the specified value."""
        try:
            counter = self.meter.create_counter(
                name=name, description=f"Counter metric: {name}", unit="1"
            )
            counter.add(amount=value, attributes=tags)
        except Exception as e:
            # Log error but don't crash application
            print(f"Error incrementing counter metric {name}: {str(e)}")

    def record_gauge(self, name: str, tags: dict, value: float):
        """Record a specific value for a gauge metric."""
        try:
            # In OTel, gauges are implemented using an observable gauge
            observable_gauge = self.meter.create_observable_gauge(
                name=name,
                description=f"Gauge metric: {name}",
                unit="1",
                callbacks=[lambda observer: observer.observe(value, tags)],
            )
        except Exception as e:
            print(f"Error recording gauge metric {name}: {str(e)}")

    def record_histogram(self, name: str, tags: dict, value: float):
        """Record a value to be aggregated in a histogram metric."""
        try:
            histogram = self.meter.create_histogram(
                name=name, description=f"Histogram metric: {name}", unit="1"
            )
            histogram.record(value, attributes=tags)
        except Exception as e:
            print(f"Error recording histogram metric {name}: {str(e)}")
