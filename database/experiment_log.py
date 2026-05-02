from typing import Any, Iterable, List, Mapping, Optional, Tuple

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

from start_here.experiments.constants import (
    RESULTS_DATABASE_NAME,
    RESULTS_DATABASE_HOST,
    RESULTS_DATABASE_PORT,
    RESULTS_DATABASE_USER,
    RESULTS_DATABASE_PASSWORD,
)
from database.migrations import ensure_schema


def _open_connection() -> psycopg2.extensions.connection:
    connection = psycopg2.connect(
        dbname=RESULTS_DATABASE_NAME,
        user=RESULTS_DATABASE_USER,
        password=RESULTS_DATABASE_PASSWORD,
        host=RESULTS_DATABASE_HOST,
        port=RESULTS_DATABASE_PORT,
    )
    ensure_schema(connection)
    return connection


def create_all_tables() -> None:
    connection = psycopg2.connect(
        dbname=RESULTS_DATABASE_NAME,
        user=RESULTS_DATABASE_USER,
        password=RESULTS_DATABASE_PASSWORD,
        host=RESULTS_DATABASE_HOST,
        port=RESULTS_DATABASE_PORT,
    )
    try:
        ensure_schema(connection)
    finally:
        connection.close()


def create_experiment(
    name: str,
    model_key: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> int:
    connection = _open_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO experiment_setup (name, model_key, temperature, top_p, max_tokens)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (name, model_key, temperature, top_p, max_tokens),
        )
        row = cursor.fetchone()
        connection.commit()
        return row[0]
    finally:
        connection.close()


def add_prompt(experiment_id: int, prompt_text: str) -> int:
    connection = _open_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO prompt (experiment_id, prompt_text)
            VALUES (%s, %s)
            RETURNING id
            """,
            (experiment_id, prompt_text),
        )
        row = cursor.fetchone()
        connection.commit()
        return row[0]
    finally:
        connection.close()


def add_prompts_bulk(experiment_id: int, prompt_texts: List[str]) -> List[int]:
    connection = _open_connection()
    try:
        cursor = connection.cursor()
        rows = [(experiment_id, text) for text in prompt_texts]
        execute_values(
            cursor,
            """
            INSERT INTO prompt (experiment_id, prompt_text)
            VALUES %s
            RETURNING id
            """,
            rows,
        )
        ids = [row[0] for row in cursor.fetchall()]
        connection.commit()
        return ids
    finally:
        connection.close()


def delete_prompts_for_experiment(experiment_id: int) -> None:
    connection = _open_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM prompt WHERE experiment_id = %s",
                (experiment_id,),
            )
        connection.commit()
    finally:
        connection.close()


def get_experiment_by_name(name: str) -> Optional[Mapping[str, Any]]:
    connection = _open_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, name, model_key, temperature, top_p, max_tokens, created_at
                FROM experiment_setup
                WHERE name = %s
                """,
                (name,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        connection.close()


def get_experiment(experiment_id: int) -> Optional[Mapping[str, Any]]:
    connection = _open_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, name, model_key, temperature, top_p, max_tokens, created_at
                FROM experiment_setup
                WHERE id = %s
                """,
                (experiment_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        connection.close()


def list_experiments() -> List[Mapping[str, Any]]:
    connection = _open_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, name, model_key, temperature, top_p, max_tokens, created_at
                FROM experiment_setup
                ORDER BY created_at DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def get_prompts(experiment_id: int) -> List[Mapping[str, Any]]:
    connection = _open_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, experiment_id, prompt_text
                FROM prompt
                WHERE experiment_id = %s
                ORDER BY id
                """,
                (experiment_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


EVALUATION_TARGET_SMELLS = ("long method", "feature envy", "data class")
EVALUATION_TARGET_SEVERITIES = ("major", "critical")


def fetch_unlabeled_pairs(
    annotator: str,
    limit: Optional[int] = None,
    demo_only: Optional[bool] = None,
) -> List[Mapping[str, Any]]:
    connection = _open_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT
                    r.id            AS llm_result_id,
                    o.id            AS smell_occurrence_id,
                    f.file_path,
                    f.file_content,
                    o.code_snippet,
                    o.code_name,
                    o.start_line,
                    o.end_line,
                    LOWER(o.smell)  AS oracle_smell,
                    o.severity      AS oracle_severity,
                    o.type          AS oracle_granularity,
                    r.response      AS llm_response
                FROM llm_prompt_results r
                JOIN mlcq_files            f ON f.id = r.mlcq_file_id
                JOIN mlcq_smell_occurrences o ON o.id = ANY(f.smell_occurrence_ids)
                LEFT JOIN evaluation_labels el
                       ON el.llm_result_id       = r.id
                      AND el.smell_occurrence_id = o.id
                      AND el.annotator           = %s
                WHERE r.success = TRUE
                  AND r.response IS NOT NULL
                  AND LOWER(o.smell) IN %s
                  AND o.severity IN %s
                  AND el.id IS NULL
            """
            parameters: List[Any] = [
                annotator,
                EVALUATION_TARGET_SMELLS,
                EVALUATION_TARGET_SEVERITIES,
            ]
            if demo_only is True:
                query += " AND f.demo_set = TRUE"
            elif demo_only is False:
                query += " AND f.demo_set = FALSE"
            query += " ORDER BY r.id, o.id"
            if limit is not None:
                query += " LIMIT %s"
                parameters.append(limit)
            cursor.execute(query, tuple(parameters))
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def upsert_evaluation_labels(rows: Iterable[Mapping[str, Any]]) -> int:
    payload = [
        (
            row["llm_result_id"],
            row["smell_occurrence_id"],
            row["label_config_version"],
            row["ls_task_id"],
            row["ls_annotation_id"],
            row["annotator"],
            row["label"],
            row["needs_review"],
            row.get("comment"),
            row.get("lead_time_seconds"),
            row["created_at"],
        )
        for row in rows
    ]
    if not payload:
        return 0
    connection = _open_connection()
    try:
        cursor = connection.cursor()
        execute_values(
            cursor,
            """
            INSERT INTO evaluation_labels (
                llm_result_id, smell_occurrence_id, label_config_version,
                ls_task_id, ls_annotation_id, annotator, label,
                needs_review, comment, lead_time_seconds, created_at
            )
            VALUES %s
            ON CONFLICT (llm_result_id, smell_occurrence_id, annotator) DO UPDATE SET
                label_config_version = EXCLUDED.label_config_version,
                ls_task_id           = EXCLUDED.ls_task_id,
                ls_annotation_id     = EXCLUDED.ls_annotation_id,
                label                = EXCLUDED.label,
                needs_review         = EXCLUDED.needs_review,
                comment              = EXCLUDED.comment,
                lead_time_seconds    = EXCLUDED.lead_time_seconds,
                created_at           = EXCLUDED.created_at
            """,
            payload,
        )
        connection.commit()
        return cursor.rowcount if cursor.rowcount is not None else len(payload)
    finally:
        connection.close()


def list_evaluation_labels(annotator: Optional[str] = None) -> List[Mapping[str, Any]]:
    connection = _open_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            if annotator is None:
                cursor.execute(
                    """
                    SELECT * FROM evaluation_labels
                    ORDER BY created_at DESC
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM evaluation_labels
                    WHERE annotator = %s
                    ORDER BY created_at DESC
                    """,
                    (annotator,),
                )
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def insert_results(
    experiment_id: int,
    results: Iterable[Mapping],
    model_key: str,
    model_name: str,
) -> Tuple[str, int]:
    connection = _open_connection()
    try:
        rows = [
            (
                experiment_id,
                result["prompt_id"],
                result.get("mlcq_file_id"),
                model_key,
                model_name,
                result.get("prompt"),
                result.get("response"),
                result.get("timestamp"),
                float(result.get("duration_seconds", 0.0)),
                bool(result.get("success")),
                result.get("error"),
            )
            for result in results
        ]

        cursor = connection.cursor()
        execute_values(
            cursor,
            """
            INSERT INTO llm_prompt_results (
                experiment_id,
                prompt_id,
                mlcq_file_id,
                model_key,
                model_name,
                prompt,
                response,
                timestamp,
                duration_seconds,
                success,
                error
            )
            VALUES %s
            """,
            rows,
        )
        connection.commit()
        inserted_rows = cursor.rowcount if cursor.rowcount is not None else len(rows)
        database_identifier = (
            f"postgresql://{RESULTS_DATABASE_HOST}:{RESULTS_DATABASE_PORT}/{RESULTS_DATABASE_NAME}"
        )
        return database_identifier, inserted_rows
    finally:
        connection.close()
