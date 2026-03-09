import requests
import json
import time
import os
from tqdm import tqdm
import pandas as pd

TOKEN = os.getenv('GITHUB_TOKEN')

# --------------------------------------------------------------------
# Fetch FULL file + snippet
# --------------------------------------------------------------------
def fetch_file_and_snippet(repo_url, commit_hash, file_path, start_line, end_line, request_count):

    # Controla limite de requests
    if request_count > 4500:
        print("Reached 4500 requests, sleeping for 1 hour ...")
        time.sleep(3600)
        request_count = 0

    # Normaliza nome do repositório para raw.githubusercontent URL
    repo_name = (
        repo_url.replace("git@", "")
                .replace("https://", "")
                .replace("http://", "")
                .replace("github.com:", "")
                .replace("github.com/", "")
                .replace(".git", "")
    )

    raw_url = f"https://raw.githubusercontent.com/{repo_name}/{commit_hash}/{file_path.lstrip('/')}"
    headers = {"Authorization": f"token {TOKEN}"}

    response = requests.get(raw_url, headers=headers)

    if response.status_code == 200:
        full_file = response.text
        lines = full_file.splitlines()
        snippet = "\n".join(lines[start_line-1:end_line])
        return snippet, full_file, request_count + 1

    else:
        print(f"Failed to fetch file: {raw_url} (status: {response.status_code})")
        return None, None, request_count + 1


# --------------------------------------------------------------------
# Process CSV (limit 10 rows) + Save JSON + Save CSV
# --------------------------------------------------------------------
def process_dataset(original_csv_file, json_file, csv_file_with_source_code, batch_size=50):

    request_count = 0
    json_data = []
    csv_rows = []
    counter = 0
    skipped_ids = []
    error_ids = []

    # Leitura manual, dataset separado por ';'
    with open(original_csv_file, "r") as f:
        next(f)  # pular header

        for line in tqdm(f, desc="Fetching code + source files"):

            try:
                parts = line.strip().split(";")
                
                # Validate we have enough fields
                if len(parts) < 15:
                    print(f"Warning: Line {counter + 1} has only {len(parts)} fields, expected 15. Skipping.")
                    error_ids.append(counter + 1)
                    counter += 1
                    continue
                
                (original_id, _, _, smell, severity, _, type_field, code_name, repo_url,
                 commit_hash, file_path, start_line, end_line, _, _) = parts

                start_line = int(start_line)
                end_line = int(end_line)

                snippet, full_file, request_count = fetch_file_and_snippet(
                    repo_url, commit_hash, file_path, start_line, end_line, request_count
                )

                if snippet and full_file:
                    entry = {
                        "id": original_id,  # Preserve original ID
                        "repo_url": repo_url,
                        "commit_hash": commit_hash,
                        "file_path": file_path,
                        "start_line": start_line,
                        "end_line": end_line,
                        "code_snippet": snippet,
                        "file_content": full_file,
                        "smell": smell,
                        "severity": severity,
                        "type": type_field,
                        "code_name": code_name
                    }

                    json_data.append(entry)
                    csv_rows.append(entry)
                else:
                    # Track skipped entries due to fetch failure
                    skipped_ids.append({
                        "id": original_id,
                        "repo_url": repo_url,
                        "file_path": file_path,
                        "reason": "Failed to fetch file"
                    })
                    print(f"Warning: Failed to fetch file for ID {original_id}")

            except ValueError as e:
                print(f"Error parsing line {counter + 1}: {e}")
                error_ids.append(counter + 1)
            except Exception as e:
                print(f"Unexpected error processing line {counter + 1}: {e}")
                error_ids.append(counter + 1)

            counter += 1
            if counter % batch_size == 0:
                save_json(json_file, json_data)
                json_data = []

    # salvar json remanescente
    if json_data:
        save_json(json_file, json_data)

    print(f"Completed JSON saving. Output: {json_file}")
    print(f"Saving CSV to: {csv_file_with_source_code}")

    # Salva CSV com pandas
    df = pd.DataFrame(csv_rows)
    df.to_csv(csv_file_with_source_code, index=False)
    print("CSV saved successfully.")
    
    # Report statistics
    print(f"\n=== Processing Summary ===")
    print(f"Total rows processed: {counter}")
    print(f"Successfully processed: {len(csv_rows)}")
    print(f"Skipped (fetch failures): {len(skipped_ids)}")
    print(f"Errors (parsing issues): {len(error_ids)}")
    
    if skipped_ids:
        skipped_file = csv_file_with_source_code.replace(".csv", "_skipped.csv")
        skipped_df = pd.DataFrame(skipped_ids)
        skipped_df.to_csv(skipped_file, index=False)
        print(f"Skipped entries saved to: {skipped_file}")
    
    if error_ids:
        print(f"Error line numbers: {error_ids[:10]}{'...' if len(error_ids) > 10 else ''}")


# --------------------------------------------------------------------
# JSON incremental saving
# --------------------------------------------------------------------
def save_json(json_file, json_data):
    try:
        with open(json_file, "r") as f:
            existing_data = json.load(f)
    except:
        existing_data = []

    existing_data.extend(json_data)

    with open(json_file, "w") as f:
        json.dump(existing_data, f, indent=4)

    print(f"Saved batch of {len(json_data)} entries.")


# --------------------------------------------------------------------
# Inputs (só executa quando rodar o script, não ao importar)
# --------------------------------------------------------------------
if __name__ == "__main__":
    original_csv_file = "original_mlcq_samples.csv"
    json_file = "original_mlcq_samples.json"
    csv_file_with_source_code = "mlcq_samples_with_source_code.csv"
    process_dataset(original_csv_file, json_file, csv_file_with_source_code)
