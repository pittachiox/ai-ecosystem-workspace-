"""
OpenTelemetry telemetry bootstrapper for the AI Ecosystem.

This module sets up:
  - TracerProvider  → exports OTLP gRPC to OTel Collector → Tempo
  - MeterProvider   → exports OTLP gRPC to OTel Collector → Prometheus
  - LoggerProvider  → exports OTLP gRPC to OTel Collector → Loki
"""
from __future__ import annotations

import logging
import os

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_telemetry(service_name: str | None = None) -> None:
    """Initialize OpenTelemetry tracing, metrics, and logging for the service."""
    _service_name = service_name or os.getenv("OTEL_SERVICE_NAME", "ai-ecosystem-service")
    _endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    _env = os.getenv("DEPLOYMENT_ENV", "docker")

    resource = Resource.create(
        {
            "service.name": _service_name,
            "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "deployment.environment": _env,
        }
    )

    # ── Traces ──────────────────────────────────────────────────────────
    tracer_provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint=_endpoint, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)

    # ── Metrics ─────────────────────────────────────────────────────────
    metric_exporter = OTLPMetricExporter(endpoint=_endpoint, insecure=True)
    metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=15_000)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # ── Logs ────────────────────────────────────────────────────────────
    log_exporter = OTLPLogExporter(endpoint=_endpoint, insecure=True)
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    set_logger_provider(logger_provider)

    # Attach OTel log handler to the root Python logger
    otel_handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
    root_logger = logging.getLogger()
    root_logger.addHandler(otel_handler)
    root_logger.setLevel(logging.INFO)

    logging.info(
        "[telemetry] OpenTelemetry initialized",
        extra={"service.name": _service_name, "otlp.endpoint": _endpoint},
    )
