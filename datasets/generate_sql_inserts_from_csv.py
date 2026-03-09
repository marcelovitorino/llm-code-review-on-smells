import pandas as pd


def escape_sql(value):
    if pd.isna(value):
        return "NULL"
    value = str(value).replace("'", "''")
    return f"'{value}'"


def generate_sql_inserts(input_csv, output_sql):
    dataframe = pd.read_csv(input_csv)
    with open(output_sql, "w", encoding="utf-8") as file_handle:
        file_handle.write("BEGIN;\n")
        for _, row in dataframe.iterrows():
            sql = (
                "INSERT INTO mlcq_samples "
                "(repo_url, commit_hash, file_path, start_line, end_line, "
                "code_snippet, file_content, smell, severity, type, code_name)"
                " VALUES ("
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


if __name__ == "__main__":
    generate_sql_inserts(
        input_csv="MLCQ_processed_with_source.csv",
        output_sql="mlcq_inserts.sql",
    )
