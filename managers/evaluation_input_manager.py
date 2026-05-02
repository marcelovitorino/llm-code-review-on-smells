import random
from typing import Any, Mapping, Optional, Tuple

from database.experiment_log import fetch_unlabeled_pairs
from integrations.label_studio.code_html import (
    CODEBOOK_HTML,
    DECISION_TREE_HTML,
    build_oracle_details_html,
    render_code_html,
)
from integrations.label_studio.label_studio_provider import (
    DEFAULT_LABEL_CONFIG_VERSION,
    LabelStudioClient,
)


def build_task_external_id(llm_result_id: int, smell_occurrence_id: int) -> str:
    return f"{llm_result_id}-{smell_occurrence_id}"


def parse_task_external_id(task_external_id: str) -> Tuple[int, int]:
    llm_result_id_str, smell_occurrence_id_str = task_external_id.split("-")
    return int(llm_result_id_str), int(smell_occurrence_id_str)


def _build_task_data(
    pair: Mapping[str, Any],
    label_config_version: str,
) -> dict:
    snippet_html = render_code_html(
        pair["code_snippet"] or "",
        language="java",
    )
    file_html = render_code_html(
        pair["file_content"] or "",
        language="java",
        highlight_lines=(pair["start_line"], pair["end_line"]),
    )
    oracle_details_html = build_oracle_details_html(
        severity=pair["oracle_severity"],
        granularity=pair["oracle_granularity"] or "",
        code_name=pair["code_name"] or "",
        start_line=pair["start_line"],
        end_line=pair["end_line"],
        file_path=pair["file_path"],
    )
    return {
        "task_external_id": build_task_external_id(
            pair["llm_result_id"], pair["smell_occurrence_id"]
        ),
        "label_config_version": label_config_version,
        "snippet_html": snippet_html,
        "file_html": file_html,
        "oracle_smell": pair["oracle_smell"],
        "oracle_severity": pair["oracle_severity"],
        "oracle_granularity": pair["oracle_granularity"] or "",
        "code_name": pair["code_name"] or "",
        "start_line": pair["start_line"],
        "end_line": pair["end_line"],
        "file_path": pair["file_path"],
        "llm_response": pair["llm_response"],
        "oracle_details_html": oracle_details_html,
        "codebook_html": CODEBOOK_HTML,
        "decision_tree_html": DECISION_TREE_HTML,
    }


def upload_responses_to_label_studio(
    client: LabelStudioClient,
    project_id: int,
    annotator: str,
    label_config_version: str = DEFAULT_LABEL_CONFIG_VERSION,
    limit: Optional[int] = None,
    shuffle_seed: Optional[int] = None,
    demo_only: Optional[bool] = None,
) -> int:
    pairs = fetch_unlabeled_pairs(
        annotator=annotator,
        limit=limit,
        demo_only=demo_only,
    )
    if not pairs:
        print(
            f"nenhum par elegível para demo_only={demo_only} "
            "(verifique se há llm_prompt_results para arquivos com esse filtro)"
        )
        return 0

    already_uploaded = client.list_existing_task_external_ids(project_id)
    fresh_pairs = [
        pair
        for pair in pairs
        if build_task_external_id(pair["llm_result_id"], pair["smell_occurrence_id"])
        not in already_uploaded
    ]
    skipped = len(pairs) - len(fresh_pairs)
    if skipped:
        print(f"skipping {skipped} pares já presentes no projeto LS")
    if not fresh_pairs:
        return 0

    tasks = [
        {"data": _build_task_data(pair, label_config_version)}
        for pair in fresh_pairs
    ]

    rng = random.Random(shuffle_seed)
    rng.shuffle(tasks)

    client.import_tasks(project_id=project_id, tasks=tasks)
    return len(tasks)
