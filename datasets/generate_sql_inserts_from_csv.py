import ast

import pandas as pd

TARGET_SMELLS = ["feature envy", "long method", "data class"]
RELEVANT_SEVERITIES = ["major", "critical"]
SEVERITY_PRIORITY = {"critical": 0, "major": 1}


def escape_sql(value):
    if pd.isna(value):
        return "NULL"
    value = str(value).replace("'", "''")
    return f"'{value}'"


def _parse_list(raw):
    if pd.isna(raw):
        return []
    if isinstance(raw, list):
        return raw
    return ast.literal_eval(str(raw))


def _format_text_array(raw):
    items = _parse_list(raw)
    if not items:
        return "ARRAY[]::TEXT[]"
    escaped = ",".join(escape_sql(item) for item in items)
    return f"ARRAY[{escaped}]::TEXT[]"


def _format_int_array(raw):
    items = _parse_list(raw)
    if not items:
        return "ARRAY[]::INTEGER[]"
    escaped = ",".join(str(int(item)) for item in items)
    return f"ARRAY[{escaped}]::INTEGER[]"


def generate_sql_inserts(input_csv, output_sql):
    dataframe = pd.read_csv(input_csv)
    dataframe = dataframe[
        dataframe["smell"].isin(TARGET_SMELLS)
        & dataframe["severity"].isin(RELEVANT_SEVERITIES)
    ]
    dataframe = dataframe.assign(_sev_rank=dataframe["severity"].map(SEVERITY_PRIORITY))
    dataframe = (
        dataframe.sort_values(["_sev_rank", "id"])
        .drop_duplicates(
            subset=["repo_url", "commit_hash", "file_path", "smell"],
            keep="first",
        )
        .drop(columns="_sev_rank")
    )
    with open(output_sql, "w", encoding="utf-8") as file_handle:
        file_handle.write("BEGIN;\n")
        for _, row in dataframe.iterrows():
            sql = (
                "INSERT INTO mlcq_smell_occurrences "
                "(id, repo_url, commit_hash, file_path, start_line, end_line, "
                "code_snippet, file_content, smell, severity, type, code_name)"
                " VALUES ("
                f"{int(row['id'])},"
                f"{escape_sql(row['repo_url'])},"
                f"{escape_sql(row['commit_hash'])},"
                f"{escape_sql(row['file_path'])},"
                f"{row['start_line']},"
                f"{row['end_line']},"
                f"{escape_sql(row['code_snippet'])},"
                f"{escape_sql(row['file_content'])},"
                f"{escape_sql(row['smell'])},"
                f"{escape_sql(row['severity'])},"
                f"{escape_sql(row['type'])},"
                f"{escape_sql(row['code_name'])}"
                ");\n"
            )
            file_handle.write(sql)
        file_handle.write("COMMIT;\n")
    print(f"SQL file generated: {output_sql}")
    return output_sql


def generate_sql_inserts_for_files(input_csv, output_sql):
    dataframe = pd.read_csv(input_csv, sep=";")
    with open(output_sql, "w", encoding="utf-8") as file_handle:
        file_handle.write("BEGIN;\n")
        for _, row in dataframe.iterrows():
            sql = (
                "INSERT INTO mlcq_files "
                "(repo_url, commit_hash, file_path, file_content, "
                "annotated_smells, annotation_count, smell_occurrence_ids)"
                " VALUES ("
                f"{escape_sql(row['repo_url'])},"
                f"{escape_sql(row['commit_hash'])},"
                f"{escape_sql(row['file_path'])},"
                f"{escape_sql(row['file_content'])},"
                f"{_format_text_array(row['annotated_smells'])},"
                f"{int(row['annotation_count'])},"
                f"{_format_int_array(row['smell_occurrence_ids'])}"
                ");\n"
            )
            file_handle.write(sql)
        file_handle.write("COMMIT;\n")
    print(f"SQL file generated: {output_sql}")
    return output_sql


if __name__ == "__main__":
    generate_sql_inserts(
        input_csv="mlcq_enriched_dataset.csv",
        output_sql="mlcq_smell_occurrences_inserts.sql",
    )
    generate_sql_inserts_for_files(
        input_csv="mlcq_files.csv",
        output_sql="mlcq_files_inserts.sql",
    )
