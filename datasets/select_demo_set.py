"""Select 8 stratified MLCQ samples for the labeling codebook (demo_set).

Criteria:
- 3 Long Method, 3 Feature Envy, 2 Data Class
- Mix of major/critical severities
- All from distinct repositories
- Mix of granularity (method/class) — automatic since LM/FE are methods, DC are classes
"""
from pathlib import Path
import json
import random
import sys

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from start_here.experiments.constants import (
    RESULTS_DATABASE_NAME,
    RESULTS_DATABASE_HOST,
    RESULTS_DATABASE_PORT,
    RESULTS_DATABASE_USER,
    RESULTS_DATABASE_PASSWORD,
)

RANDOM_SEED = 42
TARGETS = [
    ("long method", "critical", 1),
    ("long method", "major", 2),
    ("feature envy", "critical", 1),
    ("feature envy", "major", 2),
    ("data class", "critical", 1),
    ("data class", "major", 1),
]
DEMO_SET_OUT = _project_root / "datasets" / "demo_set.csv"
LABELING_SET_OUT = _project_root / "datasets" / "labeling_set.csv"


def repo_owner_name(repo_url: str) -> str:
    cleaned = repo_url.replace("git@github.com:", "").replace(".git", "")
    parts = cleaned.split("/")
    return f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else cleaned


def main() -> None:
    random.seed(RANDOM_SEED)
    connection = psycopg2.connect(
        dbname=RESULTS_DATABASE_NAME,
        user=RESULTS_DATABASE_USER,
        password=RESULTS_DATABASE_PASSWORD,
        host=RESULTS_DATABASE_HOST,
        port=RESULTS_DATABASE_PORT,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE mlcq_files
                ADD COLUMN IF NOT EXISTS demo_set boolean NOT NULL DEFAULT false
            """)
        connection.commit()
        print("[setup] demo_set column ensured on mlcq_files")

        # Reset previous demo selection so re-running is deterministic.
        with connection.cursor() as cursor:
            cursor.execute("UPDATE mlcq_files SET demo_set = false")
        connection.commit()

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    occ.id AS occurrence_id,
                    occ.repo_url,
                    occ.commit_hash,
                    occ.file_path,
                    occ.start_line,
                    occ.end_line,
                    occ.smell,
                    occ.severity,
                    occ.type,
                    occ.code_name,
                    f.id AS file_id,
                    f.file_content,
                    f.annotated_smells,
                    f.annotation_count
                FROM mlcq_smell_occurrences AS occ
                JOIN mlcq_files AS f
                  ON f.repo_url    = occ.repo_url
                 AND f.commit_hash = occ.commit_hash
                 AND f.file_path   = occ.file_path
                WHERE occ.smell IN ('long method', 'feature envy', 'data class')
                  AND occ.severity IN ('major', 'critical')
            """)
            candidates = pd.DataFrame(cursor.fetchall())

        candidates["repo"] = candidates["repo_url"].map(repo_owner_name)
        print(f"[load] {len(candidates)} candidate occurrences across "
              f"{candidates['repo'].nunique()} repos")

        used_repos: set[str] = set()
        used_file_ids: set[int] = set()
        chosen_rows: list[pd.Series] = []

        for smell, severity, count in TARGETS:
            pool = candidates[
                (candidates["smell"] == smell)
                & (candidates["severity"] == severity)
                & (~candidates["repo"].isin(used_repos))
                & (~candidates["file_id"].isin(used_file_ids))
            ].sample(frac=1, random_state=RANDOM_SEED)
            picked = pool.head(count)
            if len(picked) < count:
                raise RuntimeError(
                    f"Not enough distinct-repo candidates for "
                    f"{smell}/{severity}: needed {count}, got {len(picked)}"
                )
            for _, row in picked.iterrows():
                used_repos.add(row["repo"])
                used_file_ids.add(row["file_id"])
                chosen_rows.append(row)

        demo_df = pd.DataFrame(chosen_rows).reset_index(drop=True)
        print(f"[select] picked {len(demo_df)} samples across "
              f"{demo_df['repo'].nunique()} repos")

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE mlcq_files SET demo_set = true WHERE id = ANY(%s)",
                (demo_df["file_id"].astype(int).tolist(),),
            )
        connection.commit()
        print(f"[mark] demo_set=true on {len(demo_df)} files")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM mlcq_files WHERE demo_set = true"
            )
            demo_count = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM mlcq_files WHERE demo_set = false"
            )
            labeling_count = cursor.fetchone()[0]
            print(f"[verify] demo_set rows in DB:    {demo_count}")
            print(f"[verify] labeling_set rows:      {labeling_count}")

        demo_export_cols = [
            "occurrence_id", "file_id", "repo", "repo_url", "commit_hash",
            "file_path", "start_line", "end_line", "smell", "severity",
            "type", "code_name", "annotated_smells", "annotation_count",
            "file_content",
        ]
        demo_df[demo_export_cols].to_csv(
            DEMO_SET_OUT, sep=";", index=False
        )
        print(f"[save] demo_set CSV: {DEMO_SET_OUT}")

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    f.id AS file_id, f.repo_url, f.commit_hash, f.file_path,
                    f.annotated_smells, f.annotation_count,
                    f.smell_occurrence_ids, f.file_content
                FROM mlcq_files AS f
                WHERE f.demo_set = false
            """)
            labeling_df = pd.DataFrame(cursor.fetchall())
        labeling_df.to_csv(LABELING_SET_OUT, sep=";", index=False)
        print(f"[save] labeling_set CSV: {LABELING_SET_OUT} "
              f"({len(labeling_df)} rows)")

        print("\n=== DEMO SET SUMMARY ===")
        for i, row in demo_df.iterrows():
            print(
                f"\n--- Sample {i + 1}/8 ---"
                f"\n  occurrence_id : {row['occurrence_id']}"
                f"\n  file_id       : {row['file_id']}"
                f"\n  repo          : {row['repo']}"
                f"\n  commit        : {row['commit_hash']}"
                f"\n  file_path     : {row['file_path']}"
                f"\n  smell         : {row['smell']}"
                f"\n  severity      : {row['severity']}"
                f"\n  type          : {row['type']}"
                f"\n  code_name     : {row['code_name']}"
                f"\n  lines         : {row['start_line']}-{row['end_line']}"
                f"\n  file_loc      : {len((row['file_content'] or '').splitlines())} lines"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    main()
