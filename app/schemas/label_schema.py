from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class LabelStudioProjectCreateRequest(BaseModel):
    title: str = Field(..., description="Project title")
    description: str = Field(default="", description="Project description")
    label_config: str = Field(default="<Label><Image name=\"image\" value=\"image\"/><Rectangle name=\"box\" toName=\"image\"/></Label>", description="Label Studio labeling configuration")


class LabelStudioImportTaskRequest(BaseModel):
    project_id: int = Field(..., description="Target Label Studio project ID")
    image_url: str = Field(..., description="URL to import into Label Studio")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Optional metadata")
