import os
import logging
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, DEPLOYMENT_ENVIRONMENT
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from ...infrastructure.ports.outbound_logs_exporter import iLogsExporter
from ...domain.dto.application_attributes import ApplicationAttributes


class LogExporterAdapter(iLogsExporter):
    DEFAULT_ENDPOINT: str = "https://o11y-proxy.ivanildobarauna.dev/"
    _instance = None

    def __new__(cls, application_name: str):
        if cls._instance is None:
            cls._instance = super(LogExporterAdapter, cls).__new__(cls)
            cls._instance._initialize(application_name)
        return cls._instance

    def _initialize(self, application_name: str):
        try:
            # Initialize application attributes with custom configuration
            self.application_attributes = ApplicationAttributes(
                application_name=application_name
            )

            # Get the logs-specific endpoint
            self.exporter_endpoint = os.getenv(
                "OTEL_EXPORTER_OTLP_ENDPOINT", self.DEFAULT_ENDPOINT
            )

            self.resource = Resource.create(
                attributes={
                    SERVICE_NAME: self.application_attributes.application_name,
                    DEPLOYMENT_ENVIRONMENT: self.application_attributes.environment,
                }
            )

            # Create logger provider with resource
            self.provider = LoggerProvider(resource=self.resource)

            # Create OTLP exporter with configurable endpoint
            try:
                self.processor = BatchLogRecordProcessor(
                    OTLPLogExporter(endpoint=self.exporter_endpoint, timeout=10)
                )
                self.provider.add_log_record_processor(self.processor)
                set_logger_provider(self.provider)
            except Exception as e:
                print(f"Warning: Failed to initialize OTLP log exporter: {str(e)}")
                # Fallback to console logging
                self.provider = LoggerProvider(resource=self.resource)
                set_logger_provider(self.provider)

            # Create logging handler with configured level
            log_level = self._get_log_level()
            self.handler = LoggingHandler(
                level=log_level, logger_provider=self.provider
            )

            # Configure logger
            self.logger = logging.getLogger()
            self.logger.addHandler(self.handler)
            self.logger.setLevel(log_level)
        except Exception as e:
            print(f"Error initializing log exporter: {str(e)}")
            # Ensure we at least have a logger
            self.logger = logging.getLogger()

    def _get_log_level(self) -> int:
        """Get log level from environment or use default"""
        log_level_str = os.getenv("OTEL_LOG_LEVEL", "INFO").upper()
        log_level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return log_level_map.get(log_level_str, logging.INFO)

    def get_logger(self):
        return self.logger
