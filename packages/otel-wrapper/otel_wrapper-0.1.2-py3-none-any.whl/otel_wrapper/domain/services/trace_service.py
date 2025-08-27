from ...infrastructure.ports.outbound_trace_exporter import iTracesExporter


from opentelemetry.context import Context
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.trace import SpanKind, Span, set_span_in_context
import contextlib


class TraceProcessorService:
    def __init__(self, trace_exporter: iTracesExporter):
        self._exporter = trace_exporter
        self._tracer = self._exporter.get_tracer()
        self._trace_context_propagator = TraceContextTextMapPropagator()
        self._baggage_propagator = W3CBaggagePropagator()

    def new_span(
        self, name: str, kind: SpanKind = SpanKind.INTERNAL, attributes: dict = None
    ):
        """Create a new span with the given name, kind, and attributes."""
        try:
            if attributes is None:
                attributes = {}
            return self._tracer.start_span(name=name, kind=kind, attributes=attributes)
        except Exception as e:
            print(f"Error creating span {name}: {str(e)}")
            return None

    @contextlib.contextmanager
    def span_in_context(
        self, name: str, kind: SpanKind = SpanKind.INTERNAL, attributes: dict = None
    ):
        """Context manager for creating a span and setting it as the current context."""
        span = self.new_span(name, kind, attributes)
        try:
            with set_span_in_context(span) as context:
                yield span, context
        finally:
            if span:
                span.end()

    def inject_context_into_headers(self, headers: dict, context: Context = None):
        """Inject current trace context into headers for propagation across service boundaries."""
        self._trace_context_propagator.inject(carrier=headers, context=context)
        self._baggage_propagator.inject(carrier=headers, context=context)
        return headers

    def extract_context_from_headers(self, headers: dict) -> Context:
        """Extract trace context from headers to continue traces across service boundaries."""
        context = self._trace_context_propagator.extract(carrier=headers)
        context = self._baggage_propagator.extract(carrier=headers, context=context)
        return context

    def get_tracer(self):
        """Get the underlying tracer instance."""
        return self._tracer
