import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from label_studio_sdk import Client

from core.config import settings

REPORT_DIR = Path(__file__).parent / "label_studio_reports"
EXAMPLE_PROJECT_TITLE = "Work #5 Example Project"
EXAMPLE_PROJECT_DESCRIPTION = (
    "Example project created automatically for Work #5."
)
EXAMPLE_LABEL_CONFIG = """<View>
  <Text name="text" value="$text" />
  <Choices name="label" toName="text">
    <Choice value="Positive" />
    <Choice value="Negative" />
    <Choice value="Neutral" />
  </Choices>
</View>"""
EXAMPLE_TASKS = [
    {"data": {"text": "The product arrived on time and works well."}},
    {"data": {"text": "I am unhappy with the customer service."}},
    {"data": {"text": "It is okay, but could be better."}},
]


def get_client() -> Client:
    return Client(url=settings.label_studio_url, api_key=settings.label_studio_api_key)


def get_projects() -> List[Any]:
    client = get_client()
    return client.get_projects()


def list_projects() -> List[Any]:
    projects = get_projects()
    if not projects:
        print("No projects found in Label Studio.")
        return []

    print("Projects in Label Studio:")
    for project in projects:
        title = getattr(project, "title", None) or getattr(project, "name", None)
        print(f"- Project ID: {project.id}, Title: {title}")
    return projects


def save_projects_report(projects: List[Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "projects.json"
    payload = [
        {
            "id": project.id,
            "title": getattr(project, "title", None) or getattr(project, "name", None),
            "description": getattr(project, "description", None),
        }
        for project in projects
    ]
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved projects report to {report_path}")
    return report_path


def find_project_by_title(title: str) -> Optional[Any]:
    for project in get_projects():
        project_title = getattr(project, "title", None) or getattr(project, "name", None)
        if project_title == title:
            return project
    return None


def create_example_project(
    title: str = EXAMPLE_PROJECT_TITLE,
    description: str = EXAMPLE_PROJECT_DESCRIPTION,
    label_config: str = EXAMPLE_LABEL_CONFIG,
    tasks: Optional[List[Dict[str, Any]]] = None,
) -> Any:
    client = get_client()
    print(f"Creating example project: {title}")
    project = client.create_project(
        title=title,
        description=description,
        label_config=label_config,
        expert_instruction="Please label each sentence as Positive, Negative, or Neutral.",
        show_instruction=True,
        enable_empty_annotation=True,
    )

    if tasks:
        task_ids = project.import_tasks(tasks)
        print(f"Imported {len(task_ids)} tasks into project {project.id}")
    else:
        task_ids = []

    print(f"Created project {project.id} ({title})")
    return project


def ensure_example_project() -> Any:
    existing = find_project_by_title(EXAMPLE_PROJECT_TITLE)
    if existing:
        print(f"Found existing example project: {EXAMPLE_PROJECT_TITLE} ({existing.id})")
        return existing

    return create_example_project(tasks=EXAMPLE_TASKS)


def list_project_tasks(project_id: int) -> List[Any]:
    client = get_client()
    project = client.get_project(project_id)
    tasks = project.get_tasks()
    if not tasks:
        print(f"No tasks found in project {project_id}.")
        return []

    print(f"Tasks for project {project_id}:")
    for task in tasks:
        task_id = getattr(task, "id", None) or task.get("id")
        task_data = getattr(task, "data", None) or task.get("data")
        print(f"- Task ID: {task_id}, Data: {task_data}")
    return tasks


def save_tasks_report(project_id: int, tasks: List[Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"project_{project_id}_tasks.json"
    payload = [
        {
            "id": getattr(task, "id", None) or task.get("id"),
            "data": getattr(task, "data", None) or task.get("data"),
            "annotations": getattr(task, "annotations", None) or task.get("annotations"),
        }
        for task in tasks
    ]
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved task report to {report_path}")
    return report_path


if __name__ == "__main__":
    projects = list_projects()
    if not projects:
        project = ensure_example_project()
        projects = [project]
    else:
        project = projects[0]

    save_projects_report(projects)
    tasks = list_project_tasks(project.id)
    save_tasks_report(project.id, tasks)
