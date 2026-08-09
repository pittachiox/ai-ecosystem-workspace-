# Application Layer

This package holds the production-ready application layer for the AI ecosystem platform.

## Responsibilities
- Domain configuration and runtime settings
- External service adapters and wrappers
- Background workers for asynchronous jobs
- API route modules and versioned controllers
- Pydantic schemas shared across the application

## Directory Overview
- `core/`: configuration and security primitives
- `services/`: service wrappers for MinIO, Label Studio, and Redis
- `workers/`: ARQ jobs for time-series and non-time-series processing
- `api/`: FastAPI router modules
- `schemas/`: request/response DTOs
