from typing import List

from start_here.experiments.definition import EXPERIMENTS
from database.experiment_log import (
    create_all_tables,
    get_experiment,
    get_experiment_by_name,
    create_experiment,
    add_prompts_bulk,
    delete_prompts_for_experiment,
)
from managers.prompt_input_manager import read_from_file


def _resolve_prompts(experiment_definition: dict) -> List[str]:
    if "prompts" in experiment_definition:
        return experiment_definition["prompts"]
    if "prompts_file" in experiment_definition:
        return read_from_file(experiment_definition["prompts_file"])
    return []


def load_database() -> None:
    create_all_tables()
    for experiment_definition in EXPERIMENTS:
        name = experiment_definition["name"]
        if get_experiment_by_name(name) is not None:
            print(f"Experiment '{name}' already exists, skipping.")
            continue
        prompt_texts = _resolve_prompts(experiment_definition)
        experiment_id = create_experiment(
            name=name,
            model_key=experiment_definition["model_key"],
            temperature=float(experiment_definition["temperature"]),
            top_p=float(experiment_definition["top_p"]),
            max_tokens=int(experiment_definition["max_tokens"]),
        )
        add_prompts_bulk(experiment_id, prompt_texts)
        print(f"Created experiment '{name}' (id={experiment_id}) with {len(prompt_texts)} prompt(s).")


def refresh_prompts_from_file(experiment_id: int) -> None:
    experiment = get_experiment(experiment_id)
    if not experiment:
        raise ValueError(f"No experiment with id={experiment_id}")
    name = experiment["name"]
    definition = next((e for e in EXPERIMENTS if e["name"] == name), None)
    if not definition or "prompts_file" not in definition:
        return
    prompt_texts = read_from_file(definition["prompts_file"])
    delete_prompts_for_experiment(experiment_id)
    add_prompts_bulk(experiment_id, prompt_texts)
    print(f"Reloaded {len(prompt_texts)} prompt(s) from file for experiment '{name}' (id={experiment_id}).")


if __name__ == "__main__":
    load_database()
