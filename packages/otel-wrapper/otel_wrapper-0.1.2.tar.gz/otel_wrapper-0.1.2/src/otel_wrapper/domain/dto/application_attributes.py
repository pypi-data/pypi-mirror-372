import os
from typing import Optional
from pydantic import BaseModel, field_validator


class TelemetryEndpoints(BaseModel):
    """Configuration for OpenTelemetry exporter endpoints."""

    default: str = "https://o11y-proxy.ivanildobarauna.dev/"
    traces: Optional[str] = None
    metrics: Optional[str] = None
    logs: Optional[str] = None

    @field_validator("traces", "metrics", "logs", mode="before")
    def set_endpoint_defaults(cls, v, info):
        """Use default endpoint if specific signal endpoint is not provided."""
        if v is None:
            # Get default from environment or use class default
            return os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", cls.default)
        return v

    def get_traces_endpoint(self) -> str:
        """Get endpoint for traces, with environment override."""
        return os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", self.traces)

    def get_metrics_endpoint(self) -> str:
        """Get endpoint for metrics, with environment override."""
        return os.getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT", self.metrics)

    def get_logs_endpoint(self) -> str:
        """Get endpoint for logs, with environment override."""
        return os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT", self.logs)


class ApplicationAttributes(BaseModel):
    """Attributes that identify the application in telemetry data."""

    application_name: str
    environment: str = os.getenv("__SCOPE__", "Production")
    from_wrapper: bool = True
    endpoints: TelemetryEndpoints = TelemetryEndpoints()

    def to_dict(self):
        """Convert model to dictionary."""
        return self.model_dump()
