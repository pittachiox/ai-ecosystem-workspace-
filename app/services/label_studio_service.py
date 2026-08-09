from __future__ import annotations

from typing import Any

import requests
from label_studio_sdk import Client

from app.core.config import settings


class LabelStudioService:
    def __init__(self, url: str | None = None, api_key: str | None = None) -> None:
        self.url = url or settings.label_studio_url
        self.api_key = api_key or settings.label_studio_api_key
        self.client = Client(url=self.url, api_key=self.api_key)

    def create_project(self, title: str, description: str = "", label_config: str = "") -> dict[str, Any]:
        project = self.client.projects.create(
            title=title,
            description=description,
            label_config=label_config or "<Label><Image name=\"image\" value=\"image\"/>\n<Rectangle name=\"box\" toName=\"image\"/>\n</Label>",
        )
        return project

    def import_tasks_from_urls(self, project_id: int, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        imported = []
        for task in tasks:
            imported.append(self.client.projects.import_tasks(project_id, task))
        return imported

    def export_annotations(self, project_id: int, format_name: str = "COCO") -> Any:
        response = requests.get(
            f"{self.url}/api/projects/{project_id}/export?exportType={format_name}",
            headers={"Authorization": f"Token {self.api_key}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json() if response.headers.get("Content-Type", "").lower().endswith("json") else response.content


label_studio_service = LabelStudioService()
