from label_studio_sdk import Client

from core.config import settings


def get_client() -> Client:
    return Client(url=settings.label_studio_url, api_key=settings.label_studio_api_key)


def list_projects():
    client = get_client()
    projects = client.get_projects()
    for project in projects:
        print(f"Project ID: {project.id}, Name: {project.name}")
    return projects


def list_project_tasks(project_id: int):
    client = get_client()
    project = client.get_project(project_id)
    tasks = project.get_tasks()
    for task in tasks:
        print(f"Task ID: {task.id}, Data: {task.data}")
    return tasks


if __name__ == "__main__":
    projects = list_projects()
    if projects:
        project_id = projects[0].id
        print(f"Listing tasks for project {project_id}")
        list_project_tasks(project_id)
