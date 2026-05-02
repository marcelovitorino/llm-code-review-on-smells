import json
import os
import time

import pandas as pd
import requests
from tqdm import tqdm


TOKEN = os.getenv("GITHUB_TOKEN")

TARGET_SMELLS = ["feature envy", "long method", "data class"]
RELEVANT_SEVERITIES = ["major", "critical"]
# Critical wins over major when reviewers disagree on the same (file, smell)
SEVERITY_PRIORITY = {"critical": 0, "major": 1}


def _dedup_by_file_and_smell(df, file_path_col):
    df = df.assign(_sev_rank=df["severity"].map(SEVERITY_PRIORITY))
    df = (
        df.sort_values(["_sev_rank", "id"])
        .drop_duplicates(
            subset=["repository" if file_path_col == "path" else "repo_url",
                    "commit_hash", file_path_col, "smell"],
            keep="first",
        )
        .drop(columns="_sev_rank")
    )
    return df


def fetch_full_file(repo_url, commit_hash, file_path, request_count):
    if request_count > 4500:
        print("Reached 4500 requests, sleeping for 1 hour ...")
        time.sleep(3600)
        request_count = 0

    repo_name = (
        repo_url.replace("git@", "")
        .replace("https://", "")
        .replace("http://", "")
        .replace("github.com:", "")
        .replace("github.com/", "")
        .replace(".git", "")
    )
    raw_url = f"https://raw.githubusercontent.com/{repo_name}/{commit_hash}/{file_path.lstrip('/')}"
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

    response = requests.get(raw_url, headers=headers)
    if response.status_code == 200:
        return response.text, request_count + 1
    print(f"Failed to fetch file: {raw_url} (status: {response.status_code})")
    return None, request_count + 1


def _aggregate_smell_occurrences(df):
    grouped = (
        df.groupby(["repository", "commit_hash", "path"], as_index=False)
        .agg(
            annotated_smells=("smell", lambda s: sorted(set(s))),
            annotation_count=("id", "count"),
            smell_occurrence_ids=("id", lambda s: sorted(s.tolist())),
        )
    )
    return grouped.rename(columns={"repository": "repo_url", "path": "file_path"})


def save_json(json_file, json_data):
    try:
        with open(json_file, "r") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(json_data)
    with open(json_file, "w") as f:
        json.dump(existing_data, f, indent=4)
    print(f"Saved batch of {len(json_data)} entries.")


def process_dataset(original_csv_file, json_file, csv_file_with_source_code, batch_size=50):
    """Read mlcq_smell_occurrences.csv, group by unique file, fetch file_content
    once per file, and write mlcq_files.csv (one row per file with the smell-level
    aggregations as arrays).
    """
    occurrences = pd.read_csv(original_csv_file, sep=";")
    occurrences = occurrences[
        occurrences["smell"].isin(TARGET_SMELLS)
        & occurrences["severity"].isin(RELEVANT_SEVERITIES)
    ].copy()
    occurrences = _dedup_by_file_and_smell(occurrences, file_path_col="path")

    files = _aggregate_smell_occurrences(occurrences)

    request_count = 0
    file_contents = []
    json_buffer = []
    skipped = []

    for idx, row in tqdm(files.iterrows(), total=len(files), desc="Fetching files"):
        full_file, request_count = fetch_full_file(
            row["repo_url"], row["commit_hash"], row["file_path"], request_count
        )
        file_contents.append(full_file)

        if full_file is None:
            skipped.append(
                {
                    "repo_url": row["repo_url"],
                    "commit_hash": row["commit_hash"],
                    "file_path": row["file_path"],
                    "reason": "Failed to fetch file",
                }
            )
            continue

        json_buffer.append(
            {
                "repo_url": row["repo_url"],
                "commit_hash": row["commit_hash"],
                "file_path": row["file_path"],
                "file_content": full_file,
                "annotated_smells": row["annotated_smells"],
                "annotation_count": int(row["annotation_count"]),
                "smell_occurrence_ids": row["smell_occurrence_ids"],
            }
        )
        if (idx + 1) % batch_size == 0:
            save_json(json_file, json_buffer)
            json_buffer = []

    if json_buffer:
        save_json(json_file, json_buffer)

    files["file_content"] = file_contents
    files = files.dropna(subset=["file_content"]).copy()
    files.to_csv(csv_file_with_source_code, sep=";", index=False)

    print("\n=== Processing Summary ===")
    print(f"Unique files in input:        {len(file_contents)}")
    print(f"Successfully fetched:         {len(files)}")
    print(f"Skipped (fetch failures):     {len(skipped)}")
    print(f"CSV saved to:                 {csv_file_with_source_code}")

    if skipped:
        skipped_file = csv_file_with_source_code.replace(".csv", "_skipped.csv")
        pd.DataFrame(skipped).to_csv(skipped_file, index=False)
        print(f"Skipped entries saved to:     {skipped_file}")


if __name__ == "__main__":
    process_dataset(
        original_csv_file="mlcq_smell_occurrences.csv",
        json_file="mlcq_files.json",
        csv_file_with_source_code="mlcq_files.csv",
    )
