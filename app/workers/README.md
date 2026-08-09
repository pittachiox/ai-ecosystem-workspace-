# Workers Package

This package contains asynchronous background workers executed through ARQ.

## Responsibilities
- Time-series preprocessing and forecasting jobs
- Non-time-series image training and inference jobs
- Long-running jobs that should not block the HTTP API
- Redis-backed queue task orchestration
