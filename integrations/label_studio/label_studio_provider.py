import os
from pathlib import Path
from typing import Any, Optional

from label_studio_sdk import LabelStudio

DEFAULT_LABEL_CONFIG_VERSION = "v1"
LABEL_CONFIG_DIR = Path(__file__).resolve().parent / "label_configs"


def load_label_config_xml(version: str = DEFAULT_LABEL_CONFIG_VERSION) -> str:
    config_path = LABEL_CONFIG_DIR / f"{version}.xml"
    if not config_path.is_file():
        available = sorted(p.stem for p in LABEL_CONFIG_DIR.glob("*.xml"))
        raise FileNotFoundError(
            f"label_config '{version}' not found. Available versions: {available}"
        )
    return config_path.read_text(encoding="utf-8")


class LabelStudioClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
    ):
        effective_base_url = base_url or os.environ.get("LABEL_STUDIO_URL")
        effective_api_key = api_key or os.environ.get("LABEL_STUDIO_API_KEY")
        if not effective_base_url:
            raise ValueError(
                "Label Studio base URL not configured. "
                "Set LABEL_STUDIO_URL env var or pass base_url."
            )
        if not effective_api_key:
            raise ValueError(
                "Label Studio API key not configured. "
                "Set LABEL_STUDIO_API_KEY env var or pass api_key."
            )

        self.base_url = effective_base_url.rstrip("/")
        self.sdk = LabelStudio(
            base_url=self.base_url,
            api_key=effective_api_key,
            timeout=timeout_seconds,
        )

    def whoami(self) -> Any:
        return self.sdk.users.whoami()

    def get_or_create_project(
        self,
        title: str,
        label_config_version: str = DEFAULT_LABEL_CONFIG_VERSION,
        description: Optional[str] = None,
    ) -> Any:
        for project in self.sdk.projects.list():
            if project.title == title:
                return project
        return self.sdk.projects.create(
            title=title,
            description=description or f"Auto-created via {label_config_version}",
            label_config=load_label_config_xml(label_config_version),
        )

    def update_project_label_config(self, project_id: int, label_config_version: str) -> Any:
        return self.sdk.projects.update(
            id=project_id,
            label_config=load_label_config_xml(label_config_version),
        )

    def get_project(self, project_id: int) -> Any:
        return self.sdk.projects.get(id=project_id)

    def import_tasks(self, project_id: int, tasks: list) -> Any:
        return self.sdk.projects.import_tasks(id=project_id, request=tasks)

    def list_tasks_with_annotations(self, project_id: int) -> list:
        return list(self.sdk.tasks.list(project=project_id, fields="all"))

    def list_existing_task_external_ids(self, project_id: int) -> set:
        external_ids = set()
        for task in self.sdk.tasks.list(project=project_id):
            data = getattr(task, "data", None)
            if data is None and isinstance(task, dict):
                data = task.get("data")
            if not data:
                continue
            external_id = data.get("task_external_id") if isinstance(data, dict) else None
            if external_id:
                external_ids.add(external_id)
        return external_ids

    def project_url(self, project_id: int) -> str:
        return f"{self.base_url}/projects/{project_id}/data?labeling=1"
