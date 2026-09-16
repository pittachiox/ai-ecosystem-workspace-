# Assignment 09 — Observability Tools for AI Ecosystem

**Student Name:** [Your Name]
**Student ID:** [Your ID]
**Course:** 241-353 AI Ecosystem Module
**Repository:** https://github.com/yourusername/eco_varintorn

---

## 1. Introduction & Objectives

This assignment integrates a full observability stack into the AI Ecosystem project and instruments the FastAPI backend and NER inference worker. The three pillars of observability covered are:

- Metrics — quantitative measurements (counts, latencies, histograms).
- Logs — structured JSON logs with trace context for debugging.
- Traces — distributed traces and spans to follow requests across services.

Objectives:
- Deploy OpenTelemetry Collector, Prometheus, Loki, Tempo, and Grafana using `docker-compose`.
- Instrument the FastAPI Web API and NER Inference Worker to emit traces/metrics/logs to the collector.
- Provide scripts to simulate traffic and verify flows via UIs.
- Produce a report documenting the integration and verification steps.

---

## 2. Part 1 - Observability Tools Deep-Dive

### OpenTelemetry Collector
- What: Central telemetry router/exporter receiving OTLP (gRPC/HTTP).
- What it does: Collects traces/metrics/logs, processes them (batching, resource enrichment), and exports to backends (Tempo, Prometheus, Loki).
- Key benefits: Unified telemetry ingestion, resource mapping, customizable pipelines.
- AI use case: Aggregate traces from API → worker pipelines and forward metrics to Prometheus.

### Prometheus
- What: Pull-based metrics system and time-series DB.
- What it does: Scrapes metrics endpoints (OTel collector + app endpoints) and stores timeseries.
- Key benefits: Powerful querying (PromQL), alerting, integration with Grafana.
- AI use case: Monitor request rates, inference latencies, model throughput.

### Grafana Loki
- What: Log aggregation system optimized for labels and trace correlation.
- What it does: Indexes logs with labels and integrates with Tempo traces.
- Key benefits: Efficient log storage, easy correlation with traces.
- AI use case: Inspect structured inference logs with `job_id` and `trace_id` context.

### Grafana Tempo
- What: Distributed tracing backend.
- What it does: Stores and serves traces for visualization in Grafana Explore and Trace UI.
- Key benefits: Cost-effective trace storage, integration with Grafana.
- AI use case: Visualize trace waterfall across FastAPI → inference worker spans.

### Grafana
- What: Visualization and observability UI.
- What it does: Connects to Prometheus, Loki, and Tempo to build dashboards and trace explorations.
- Key benefits: Unified observability UX, dashboards, alerting.
- AI use case: Create dashboards for inference latency, success rates, and logs/traces correlation.

---

## 3. Part 2 - System Architecture & Integration

**Services deployed (compose):**
- `otel-collector` — otel/opentelemetry-collector-contrib:0.98.0 (OTLP gRPC+HTTP, Prom exporter)
- `prometheus` — prom/prometheus:v2.51.0
- `loki` — grafana/loki:3.0.0
- `tempo` — grafana/tempo:2.4.1
- `grafana` — grafana/grafana:10.4.1

**Port mappings:**
- OTLP gRPC: 4317
- OTLP HTTP: 4318
- OTel Prometheus Exporter: 8889
- Prometheus UI: 9090
- Loki: 3100
- Tempo: 3200
- Grafana: 3000

**Docker Compose:** The repository `docker-compose.yml` includes these services and references config files in `observability/`.

**Key config files added/updated:**
- `observability/otel-collector-config.yaml`
- `observability/prometheus.yml`
- `observability/loki-config.yaml`
- `observability/tempo-config.yaml`
- `observability/grafana/provisioning/datasources/datasources.yaml`

**Code instrumentation snippets (already applied):**

FastAPI (snippet):
```python
from app.core.telemetry import setup_telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

# Initialize telemetry
setup_telemetry(service_name="fastapi-app")

# Create FastAPI app ...
FastAPIInstrumentor.instrument_app(app)
Instrumentator().instrument(app).expose(app)
```

NER Inference Worker (snippet):
```python
from app.core.telemetry import setup_telemetry
from opentelemetry import trace, metrics

setup_telemetry(service_name="inference-worker")
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

jobs_counter = meter.create_counter("inference_jobs_total")
jobs_latency = meter.create_histogram("inference_job_latency_ms")

with tracer.start_as_current_span("process_inference_job") as job_span:
    job_span.set_attribute("job.id", job_id)
    # ...
    with tracer.start_as_current_span("execute_ner_inference") as infer_span:
        infer_span.set_attribute("model.name", model_name)
        infer_span.set_attribute("entities.count", entities_count)
        infer_span.set_attribute("latency_ms", infer_latency)

jobs_counter.add(1, attributes={"model": model_name, "status": "completed"})
jobs_latency.record(total_latency, attributes={"model": model_name})
```

---

## 4. Verification & Screenshots Guide

Placeholders where screenshots should be taken after running the stack:

- System Architecture Diagram: `overview.drawio` (or PNG export)
- Grafana Datasources: Grafana → Configuration → Data Sources (should show Prometheus, Loki, Tempo)
- Prometheus Targets: `http://localhost:9090/targets` (expect `UP` for `otel-collector` and other scrape targets)
- Metrics Explorer: Grafana → Explore or custom dashboard showing `ai_ecosystem` metrics
- Loki Log Explorer: Grafana → Explore (Logs) and search for `job_id` or `trace_id`
- Tempo Traces: Grafana → Explore (Traces) and view waterfall for sample trace
- Swagger UI API testing: `http://localhost:8002/docs` to send inference requests

For each section capture a screenshot and include it in your submission.

---

## 5. Runbook / Steps to Reproduce Locally

1. Start Docker Compose

```bash
docker-compose up -d --build
```

2. Verify services

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Loki: http://localhost:3100
- Tempo: http://localhost:3200
- FastAPI app: http://localhost:8002

3. Run traffic simulation (after services healthy)

```bash
python3 scripts/traffic_simulation.py
```

4. Inspect metrics/logs/traces in Grafana Explore and Prometheus Targets.

---

## 6. Conclusion & Version Control

This assignment integrated tracing, metrics, and logging end-to-end into the AI Ecosystem using OpenTelemetry, Prometheus, Loki, Tempo, and Grafana. The FastAPI application and the NER worker were instrumented to emit traces, metrics, and structured logs that can be correlated via `job_id` and `trace_id`.

To save to your GitHub repository:

```bash
git add .
git commit -m "Assignment 09: Add observability stack and instrumentation"
git push origin main
```

---

**Files changed / added:**
- `app/main.py` (FastAPI telemetry + metrics)
- `app/workers/inference_worker.py` (tracing/metrics/logging)
- `observability/*` (configs included in repo)
- `scripts/traffic_simulation.py` (traffic simulator)
- `ASSIGNMENT_09_REPORT.md` (this report)



