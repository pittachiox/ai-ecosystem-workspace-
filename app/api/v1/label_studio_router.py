from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.schemas.label_schema import LabelStudioImportTaskRequest, LabelStudioProjectCreateRequest
from app.services.label_studio_service import label_studio_service

router = APIRouter(prefix="/ls", tags=["Labeling"])


@router.post("/projects", summary="Create a Label Studio project", description="Create a new project in Label Studio.")
async def create_project(payload: LabelStudioProjectCreateRequest) -> dict[str, Any]:
    try:
        project = label_studio_service.create_project(payload.title, payload.description, payload.label_config)
        return {"status": "created", "project": project}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Project creation failed: {exc}") from exc


@router.post("/import-data", summary="Import data into a project", description="Import MinIO URL data as tasks into a Label Studio project.")
async def import_data(payload: LabelStudioImportTaskRequest) -> dict[str, Any]:
    try:
        task = {"data": {"image": payload.image_url}, "meta": payload.metadata or {}}
        result = label_studio_service.import_tasks_from_urls(payload.project_id, [task])
        return {"status": "imported", "result": result}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Import failed: {exc}") from exc


@router.get("/export-labels", summary="Export labels", description="Export annotations from Label Studio in JSON or COCO format.")
async def export_labels(project_id: int = Query(..., description="Project ID"), export_type: str = Query(default="COCO", description="Export format")) -> Any:
    try:
        return {"project_id": project_id, "export": label_studio_service.export_annotations(project_id, format_name=export_type)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}") from exc
