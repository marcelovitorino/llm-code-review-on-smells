from datetime import datetime
from typing import List, Dict

from database.experiment_log import insert_results


def save_results(
    experiment_id: int,
    results: List[Dict],
    model_key: str,
    model_name: str,
) -> str:
    database_identifier, inserted_rows = insert_results(
        experiment_id=experiment_id,
        results=results,
        model_key=model_key,
        model_name=model_name,
    )
    timestamp = datetime.now().isoformat()
    print(
        f"\n[{timestamp}] Results saved to database: {database_identifier} "
        f"(experiment_id={experiment_id}, model_key={model_key}, total_rows={inserted_rows})"
    )
    return database_identifier
