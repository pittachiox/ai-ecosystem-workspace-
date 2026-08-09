# Project - Lib Installations - API List

![Status](https://img.shields.io/badge/Project-AI%20Ecosystem-blue)
![Status](https://img.shields.io/badge/Architecture-Production%20Ready-success)
![Status](https://img.shields.io/badge/Course-AI%20Ecosystem-orange)

## Executive Summary
This repository has been migrated from a sandbox-style prototype into a production-oriented AI ecosystem backend. The current implementation provides a structured FastAPI application with layered service wrappers, ARQ background workers, infrastructure integrations for Redis, MinIO, Label Studio, and an OpenAPI export pipeline for API snapshotting.

The project supports two main operational domains:
- Time-Series Application: preprocessing, queue-based model training, and forecasting
- Non-Time Series Application: image preprocessing, model training, and prediction workflows

## Objectives
- Clean the repository structure and archive legacy sandbox artifacts under `legacy_labs/`
- Organize the codebase into a layered application architecture under `app/`
- Provide service wrappers for external dependencies (MinIO, Label Studio, Redis)
- Use ARQ + Redis workers for asynchronous processing to avoid blocking API calls
- Expose production-ready FastAPI endpoints with OpenAPI metadata
- Generate API snapshot artifacts in CSV and Excel format

---

## Actual Repository Structure
The following structure represents the current repository state after inspection and cleanup.

```text
.
├── README.md
├── api_list_snapshot.csv
├── api_list_snapshot.xlsx
├── app/
│   ├── README.md
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── README.md
│   │       ├── __init__.py
│   │       ├── label_studio_router.py
│   │       ├── nontimeseries_router.py
│   │       ├── storage_router.py
│   │       └── timeseries_router.py
│   ├── core/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── config.py
│   ├── schemas/
│   │   ├── label_schema.py
│   │   ├── storage_schema.py
│   │   ├── task_schema.py
│   │   └── README.md
│   ├── services/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── label_studio_service.py
│   │   ├── minio_service.py
│   │   └── redis_service.py
│   └── workers/
│       ├── README.md
│       ├── __init__.py
│       ├── arq_config.py
│       ├── nontimeseries_worker.py
│       └── timeseries_worker.py
├── compose.yml
├── docker-compose.yml
├── diagrams/
│   ├── README.md
│   └── ...
├── frontend/
│   └── README.md
├── legacy_labs/
│   ├── README.md
│   ├── backend_sandbox/
│   │   ├── README.md
│   │   └── ...
│   ├── utils/
│   │   └── README.md
│   └── workers/
│       └── README.md
├── main.py
├── requirements.txt
├── scripts/
│   ├── README.md
│   ├── __init__.py
│   └── export_openapi_to_csv.py
├── storage/
│   ├── README.md
│   ├── artifacts/
│   │   └── README.md
│   ├── data/
│   │   └── README.md
│   └── log/
│       └── README.md
└── ...
```

### Folder Responsibilities
- `app/`: application layer and runtime orchestration
- `app/core/`: configuration and settings management
- `app/services/`: wrappers for MinIO, Label Studio, and Redis integrations
- `app/workers/`: ARQ background job processors
- `app/api/v1/`: API controller modules grouped by feature domain
- `app/schemas/`: Pydantic models for request/response payloads
- `scripts/`: automation utilities, including OpenAPI export tools
- `storage/`: local persisted artifacts, datasets, and logs
- `legacy_labs/`: archived sandbox experiments and legacy utilities

### README Coverage
README files are present in the active project folders and subfolders to document developer responsibilities for each layer.

---

## Tech Stack and Service Layer

### Dependencies from `requirements.txt`
| Library | Purpose |
|---|---|
| `fastapi` | API framework for routing, validation, and docs |
| `uvicorn` | ASGI server for running FastAPI |
| `minio` | Object storage client for MinIO bucket operations |
| `label-studio-sdk` | SDK for creating Label Studio projects and importing tasks |
| `redis` | Redis client for queueing and caching |
| `arq` | Asynchronous job runner for background tasks |
| `pandas` | API snapshot table generation |
| `openpyxl` | Excel export support for API snapshot |
| `pydantic` | Data validation and schema modeling |
| `pydantic-settings` | Settings management from environment variables |
| `requests` | HTTP request integration for Label Studio export |

### Infrastructure Services from `docker-compose.yml`
| Service | Image | Port | Role |
|---|---|---:|---|
| `redis` | `redis:8.8.0-alpine` | `6380:6379` | Queue and message broker |
| `postgres_db` | `postgres:15-alpine` | `5432` | Label Studio database backend |
| `label-studio-app` | `heartexlabs/label-studio:latest` | `8080` | Data labeling platform |
| `minio` | `minio/minio:latest` | `9000 / 9001` | Object storage and bucket management |

### Service Wrappers
#### `app/services/minio_service.py`
- Ensures bucket existence
- Uploads files to MinIO
- Lists stored objects
- Generates presigned URLs for temporary access
- Downloads objects to local paths

#### `app/services/label_studio_service.py`
- Creates Label Studio projects
- Imports tasks from external URL sources
- Exports annotations through the Label Studio API

#### `app/services/redis_service.py`
- Builds Redis connection settings
- Creates ARQ-compatible connection pools
- Enqueues jobs for background execution

### Worker Layer
#### Time-series workers (`app/workers/timeseries_worker.py`)
- `resample_timeseries` — resamples time-series data
- `train_timeseries_model` — simulates time-series model training
- `forecast_timeseries` — simulates forecast generation

#### Non-time-series workers (`app/workers/nontimeseries_worker.py`)
- `preprocess_images` — image preprocessing and augmentation placeholder
- `train_nontimeseries_model` — model training simulation for image tasks
- `predict_image_class` — inference simulation for image prediction

#### ARQ setup (`app/workers/arq_config.py`)
- Declares function registry for Redis queue execution
- Configures the ARQ worker runtime and startup/shutdown hooks

---

## Live API List
The current FastAPI application exposes the following endpoints based on the actual router definitions.

### Root and Health
| Method | Path | Parameters | Description |
|---|---|---|---|
| GET | `/` | none | Root landing endpoint |
| GET | `/health` | none | Service health check |

### Storage APIs (`Storage` tag)
| Method | Path | Parameters | Description |
|---|---|---|---|
| POST | `/storage/upload` | `bucket_name` optional, `object_name` required, `file_path` required | Uploads a local file into MinIO |
| GET | `/storage/files` | `bucket_name` optional | Lists objects in a MinIO bucket |
| GET | `/storage/presigned-url` | `bucket_name` optional, `object_name` required | Creates a presigned temporary access URL |

### Labeling APIs (`Labeling` tag)
| Method | Path | Parameters | Description |
|---|---|---|---|
| POST | `/ls/projects` | `title`, `description`, `label_config` | Creates a Label Studio project |
| POST | `/ls/import-data` | `project_id`, `image_url`, `metadata` optional | Imports an external URL as a Label Studio task |
| GET | `/ls/export-labels` | `project_id` required, `export_type` optional (`COCO` default) | Exports annotations from Label Studio |

### Time-Series APIs (`Time-Series` tag)
| Method | Path | Parameters | Description |
|---|---|---|---|
| POST | `/timeseries/process` | `data`, `sample_rate`, `window_size` | Queues time-series resampling/preprocessing |
| POST | `/timeseries/train` | `model_type`, `dataset_size`, `horizon` optional | Queues time-series training |
| POST | `/timeseries/forecast` | payload object | Queues forecasting inference |

### Non-Time-Series APIs (`Non-Time-Series` tag)
| Method | Path | Parameters | Description |
|---|---|---|---|
| POST | `/nontimeseries/train` | `model_type`, `dataset_size`, `horizon` optional | Queues image-model training |
| POST | `/nontimeseries/predict` | `image_path`, `model_name` | Queues image classification prediction |

### API and Tag metadata source
The live app metadata is registered in `app/main.py` with OpenAPI tags:
- `Storage`
- `Labeling`
- `Time-Series`
- `Non-Time-Series`

This metadata drives the generated Swagger UI and ReDoc output.

---

## Project Runtime and Execution Guide

### 1. Start infrastructure services
```bash
docker-compose up -d
```

Check status:
```bash
docker-compose ps
```

Running services in the active configuration:
- Redis
- PostgreSQL
- Label Studio
- MinIO

### 2. Start the FastAPI server
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Health and OpenAPI validation
```bash
curl http://localhost:8000/health
curl http://localhost:8000/openapi.json
```

Expected health response:
```json
{"status": "ok"}
```

### 4. Generate API snapshot
The repository includes a script that fetches `/openapi.json` and exports a CSV/XLSX snapshot.

```bash
python scripts/export_openapi_to_csv.py
```

Generated files:
- `api_list_snapshot.csv`
- `api_list_snapshot.xlsx`

### 5. Open API documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Notes on the Current Implementation
- The project is intentionally structured as a layered architecture to separate API, service, worker, and configuration concerns.
- `legacy_labs/` preserves the earlier sandbox experiments and historical proof-of-concept work.
- The current operational backend focuses on orchestration and integration patterns rather than full production ML pipeline execution.
- The asynchronous workers represent queue-driven processing for time-series and image tasks, with placeholder logic that can later be connected to real model training and inference runtimes.

---

## Summary of Discovered Facts
The repository currently contains:
- root-level FastAPI app entrypoint (`main.py`)
- layered application code under `app/`
- Redis, MinIO, PostgreSQL, and Label Studio services via Docker Compose
- real API definitions for storage, labeling, time-series, and non-time-series use cases
- export script generating snapshots from the live OpenAPI schema
- documentation coverage across project folders via `README.md` files

This README is generated from the actual inspected source and runtime configuration of the repository, not from assumptions or stale sandbox notes.
