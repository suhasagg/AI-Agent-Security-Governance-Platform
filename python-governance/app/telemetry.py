from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from .config import settings
p=TracerProvider()
p.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
 endpoint=settings.otel_exporter_otlp_endpoint.rstrip("/")+"/v1/traces")))
trace.set_tracer_provider(p)
tracer=trace.get_tracer("ai-agent-security-governance")
