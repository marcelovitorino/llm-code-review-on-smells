import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional

from database.experiment_log import upsert_evaluation_labels
from integrations.label_studio.label_studio_provider import LabelStudioClient
from managers.evaluation_input_manager import parse_task_external_id

DEFAULT_SNAPSHOT_DIR = (
    Path(__file__).resolve().parent.parent
    / "integrations"
    / "label_studio"
    / "snapshots"
)

_LABEL_BY_CHOICE = {
    "I": "I", "Instrumental": "I",
    "H": "H", "Helpful": "H",
    "M": "M", "Misleading": "M",
    "U": "U", "Uncertain": "U",
}


def _field(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(item) for item in value if item is not None).strip()
    return str(value).strip()


def _parse_result_array(result: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    parsed = {"label": None, "needs_review": False, "comment": ""}
    for item in result or []:
        from_name = item.get("from_name")
        value = item.get("value", {}) or {}
        if from_name == "label":
            choices = value.get("choices") or []
            for choice in choices:
                canonical = _LABEL_BY_CHOICE.get(choice)
                if canonical is not None:
                    parsed["label"] = canonical
                    break
        elif from_name == "needs_review":
            parsed["needs_review"] = bool(value.get("choices"))
        elif from_name == "comment":
            parsed["comment"] = _coerce_text(value.get("text"))
    return parsed


def _completed_by_identifier(annotation: Any) -> str:
    completed_by = _field(annotation, "completed_by")
    if isinstance(completed_by, Mapping):
        readable = (
            completed_by.get("email")
            or completed_by.get("username")
        )
        if readable:
            return readable
    elif completed_by is not None:
        if hasattr(completed_by, "email") and completed_by.email:
            return completed_by.email
        if hasattr(completed_by, "username") and completed_by.username:
            return completed_by.username

    created_username = _field(annotation, "created_username")
    if created_username:
        return created_username

    if isinstance(completed_by, Mapping):
        return str(completed_by.get("id", "unknown"))
    if completed_by is not None:
        return str(completed_by)
    return "unknown"


def _parse_created_at(annotation: Any) -> datetime:
    created_at = _field(annotation, "created_at")
    if isinstance(created_at, datetime):
        return created_at
    if isinstance(created_at, str):
        try:
            return datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _extract_task_data(task: Any) -> Mapping[str, Any]:
    return _field(task, "data") or {}


def _iter_valid_annotations(task: Any) -> Iterable[Any]:
    annotations = _field(task, "annotations") or []
    for annotation in annotations:
        if _field(annotation, "was_cancelled", False):
            continue
        yield annotation


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "model_dump"):
        return _to_jsonable(value.model_dump())
    if hasattr(value, "dict") and callable(value.dict):
        return _to_jsonable(value.dict())
    if hasattr(value, "__dict__"):
        return _to_jsonable(vars(value))
    return str(value)


def collect_labels_from_tasks(tasks: Iterable[Any]) -> List[Mapping[str, Any]]:
    rows: List[Mapping[str, Any]] = []
    for task in tasks:
        task_id = _field(task, "id")
        task_data = _extract_task_data(task)
        external_id = task_data.get("task_external_id")
        if not external_id:
            continue
        try:
            llm_result_id, smell_occurrence_id = parse_task_external_id(external_id)
        except (ValueError, TypeError):
            continue
        label_config_version = task_data.get("label_config_version") or "unknown"

        for annotation in _iter_valid_annotations(task):
            parsed = _parse_result_array(_field(annotation, "result"))
            if parsed["label"] is None:
                continue
            rows.append(
                {
                    "llm_result_id": llm_result_id,
                    "smell_occurrence_id": smell_occurrence_id,
                    "label_config_version": label_config_version,
                    "ls_task_id": task_id,
                    "ls_annotation_id": _field(annotation, "id", 0),
                    "annotator": _completed_by_identifier(annotation),
                    "label": parsed["label"],
                    "needs_review": parsed["needs_review"],
                    "comment": parsed["comment"] or None,
                    "lead_time_seconds": _field(annotation, "lead_time"),
                    "created_at": _parse_created_at(annotation),
                }
            )
    return rows


def sync_labels_from_label_studio_to_db(
    client: LabelStudioClient,
    project_id: int,
    annotator_filter: Optional[str] = None,
) -> int:
    tasks = client.list_tasks_with_annotations(project_id)
    rows = collect_labels_from_tasks(tasks)
    if annotator_filter is not None:
        rows = [row for row in rows if row["annotator"] == annotator_filter]
    return upsert_evaluation_labels(rows)


def snapshot_label_studio_to_json(
    client: LabelStudioClient,
    project_id: int,
    output_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    project = client.get_project(project_id)
    tasks = client.list_tasks_with_annotations(project_id)

    payload = {
        "exported_at": datetime.now().astimezone().isoformat(),
        "project_id": project_id,
        "project_title": getattr(project, "title", None),
        "label_config": getattr(project, "label_config", None),
        "task_count": len(tasks),
        "tasks": [_to_jsonable(task) for task in tasks],
    }

    output_path = output_dir / f"snapshot_{project_id}_{timestamp}.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return output_path
