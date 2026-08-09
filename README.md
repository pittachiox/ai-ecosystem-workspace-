# AI Ecosystem Workspace

This repository has been reorganized from a sandbox prototype into a production-oriented AI ecosystem workspace.

## Project Purpose
The platform provides a layered backend for:
- MinIO-based file storage and presigned access
- Label Studio automation for data labeling
- Time-series preprocessing, model training, and forecasting
- Non-time-series image preprocessing and inference
- Asynchronous queue processing through Redis and ARQ

## Top-level Architecture
- `app/`: application layer with core config, services, workers, routes, and schemas
- `scripts/`: automation scripts for reporting and OpenAPI exports
- `storage/`: persistent storage for datasets and logs
- `diagrams/`: design and system documentation assets
- `legacy_labs/`: archived sandbox and demo materials

## Quick Start
1. Install dependencies:
   `python -m pip install -r requirements.txt`
2. Start core services:
   `docker compose up -d`
3. Launch the API:
   `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
4. Open the docs:
   - http://localhost:8000/docs
   - http://localhost:8000/redoc

## Key Endpoints
- Storage: `/api/v1/storage/*`
- Labeling: `/api/v1/ls/*`
- Time-series: `/api/v1/timeseries/*`
- Non-time-series: `/api/v1/nontimeseries/*`

## Notes
This workspace keeps historical sandbox experiments under `legacy_labs/` to preserve the original signal while keeping the active project clean and maintainable.
