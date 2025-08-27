# OpenTelemetry Wrapper

[![Python Tests](https://github.com/ivanildobarauna-dev/open-o11y-wrapper/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ivanildobarauna-dev/open-o11y-wrapper/actions/workflows/python-tests.yml)

A comprehensive Python wrapper for OpenTelemetry that simplifies sending traces, metrics, and logs using the OTLP protocol.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/ivanildobarauna-dev/open-o11y-wrapper)

## Features

- **Unified API** for traces, metrics, and logs
- **Simple configuration** with reasonable defaults
- **Configurable endpoints** for each signal type (traces, metrics, logs)
- **Distributed tracing** with context propagation helpers
- **Multiple metric types** (counters, gauges, histograms)
- **Error handling** with graceful fallbacks
- **Singleton pattern** ensures consistent resources across your application

## Installation

```bash
pip install otel-wrapper
```

Or with Poetry:

```bash
poetry add otel-wrapper
```

## Quick Start

```python
from otel_wrapper.deps_injector import wrapper_builder

# Initialize the wrapper with your application name
telemetry = wrapper_builder("my-application")

# Create a trace
with telemetry.traces().span_in_context("my-operation") as (span, context):
    # Add span attributes
    span.set_attribute("operation.type", "example")
    
    # Create a log
    telemetry.logs().new_log(
        msg="Operation in progress", 
        tags={"operation": "my-operation"}, 
        level=20  # INFO level
    )
    
    # Record a metric
    telemetry.metrics().metric_increment(
        name="operations.count", 
        tags={"operation": "my-operation"}, 
        value=1.0
    )
```

## Configuration

The wrapper can be configured using environment variables:

- `OTEL_EXPORTER_OTLP_ENDPOINT`: Default endpoint for all signals
- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`: Endpoint for traces
- `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`: Endpoint for metrics
- `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`: Endpoint for logs
- `OTEL_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `__SCOPE__`: Application environment (defaults to "Production")

## API Reference

### Traces

```python
# Create a simple span
span = telemetry.traces().new_span("my-span")
span.set_attribute("attribute.name", "value")
span.end()

# Use span as a context manager
with telemetry.traces().span_in_context("my-span") as (span, context):
    # Do something with the span
    pass

# Context propagation
headers = {}
telemetry.traces().inject_context_into_headers(headers)

# Extract context from headers
context = telemetry.traces().extract_context_from_headers(headers)
```

### Metrics

```python
# Increment a counter
telemetry.metrics().metric_increment(
    name="requests.count", 
    tags={"endpoint": "/api/users"}, 
    value=1.0
)

# Record a gauge value
telemetry.metrics().record_gauge(
    name="system.memory.usage", 
    tags={"host": "server-01"}, 
    value=1024.5
)

# Record a histogram value
telemetry.metrics().record_histogram(
    name="request.duration", 
    tags={"endpoint": "/api/users"}, 
    value=0.156
)
```

### Logs

```python
# Create a simple log
telemetry.logs().new_log(
    msg="User logged in", 
    tags={"user_id": "123"}, 
    level=20  # INFO level
)

# Get the logger directly
logger = telemetry.logs().get_logger()
logger.info("Message with structured data", extra={"key": "value"})
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
