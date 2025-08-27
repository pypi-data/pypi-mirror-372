import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from ...infrastructure.ports.outbound_trace_exporter import iTracesExporter
from ...domain.dto.application_attributes import ApplicationAttributes


class TraceExporterAdapter(iTracesExporter):
    DEFAULT_ENDPOINT: str = "https://o11y-proxy.ivanildobarauna.dev/"
    _instance = None

    def __new__(cls, application_name: str):
        if cls._instance is None:
            cls._instance = super(TraceExporterAdapter, cls).__new__(cls)
            cls._instance._initialize(application_name)
        return cls._instance

    def _initialize(self, application_name: str):
        try:
            # Initialize application attributes with custom configuration
            self.application_attributes = ApplicationAttributes(
                application_name=application_name
            )

            # Get the traces-specific endpoint
            self.exporter_endpoint = os.getenv(
                "OTEL_EXPORTER_OTLP_ENDPOINT", self.DEFAULT_ENDPOINT
            )

            # Initialize tracer provider if not already set
            if not isinstance(trace.get_tracer_provider(), TracerProvider):
                # Create resource with application attributes
                self.resource = Resource.create(
                    attributes={
                        SERVICE_NAME: self.application_attributes.application_name,
                        DEPLOYMENT_ENVIRONMENT: self.application_attributes.environment,
                    }
                )

                # Create tracer provider with resource
                self.provider = TracerProvider(resource=self.resource)

                # Create and add span processor with OTLP exporter
                try:
                    exporter = OTLPSpanExporter(
                        endpoint=self.exporter_endpoint, timeout=10
                    )
                    self.processor = BatchSpanProcessor(exporter)
                    self.provider.add_span_processor(self.processor)
                    trace.set_tracer_provider(self.provider)
                except Exception as e:
                    print(
                        f"Warning: Failed to initialize OTLP trace exporter: {str(e)}"
                    )
                    # Set tracer provider even without exporter
                    trace.set_tracer_provider(self.provider)
            else:
                # Use existing tracer provider
                self.provider = trace.get_tracer_provider()

            # Get tracer with application name
            self._tracer = self.provider.get_tracer(
                f"host-{self.application_attributes.application_name}"
            )
        except Exception as e:
            print(f"Error initializing trace exporter: {str(e)}")
            # Fallback to default tracer
            self._tracer = trace.get_tracer(f"fallback-{application_name}")

    def get_tracer(self):
        return self._tracer
