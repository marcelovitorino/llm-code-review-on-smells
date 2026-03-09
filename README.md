# LLM Code Review on Smells

Tool to run prompts on Large Language Models (LLMs) for code review with focus on smells. Supports multiple providers (OpenAI and Google Colab AI). Setup, prompts, and results are stored in PostgreSQL.

## Project Structure

```
llm-code-review-on-smells/
├── constants/              # Configuration and constants (including DB connection)
├── execution/
│   ├── experiments.py     # Experiment definitions (name, model, decoding, prompts)
│   ├── setup_database.py  # Creates tables and seeds DB from experiments.py
│   ├── results_repository.py
│   ├── output_result_generator.py
│   └── runner.ipynb       # Main execution notebook
├── integrations/          # LLM providers (OpenAI, Colab)
└── prompts/               # Optional TXT files referenced by experiments.py (prompts_file)
```

## Requirements

- Python 3.x
- PostgreSQL (database name and credentials in `constants/constants.py`)
- `pip install openai psycopg2-binary`
- For OpenAI: set `OPENAI_API_KEY` in constants or environment

## Supported Models

| Provider  | Models                                                                 |
| --------- | ---------------------------------------------------------------------- |
| **Colab** | Gemini 2.0 Flash, Gemini 2.0 Flash Lite, Gemini 1.5 Pro                |
| **OpenAI**| GPT-4.1, GPT-4, GPT-4 Turbo, GPT-3.5 Turbo                             |

## Configuration

- **PostgreSQL:** Edit `constants/constants.py` (`RESULTS_DATABASE_*`). Tables are created by the setup step.
- **OpenAI:** Set `OPENAI_API_KEY` in constants (do not commit real keys).

## Usage

1. **Define experiments** in `execution/experiments.py`: each entry has `name`, `model_key`, `temperature`, `top_p`, `max_tokens`, and either `prompts` (list of strings) or `prompts_file` (filename under `prompts/`, e.g. `"test-prompt.txt"`). In `prompts_file`, prompts are read from the file (multi-line allowed; use `---` on its own line to separate multiple prompts).
2. **Run setup once:** In `execution/runner.ipynb`, run the “Create tables and seed” cell (or run `python -m execution.setup_database` from the project root). This creates tables and inserts the experiments and prompts from `experiments.py`. Existing experiment names are skipped.
3. **Run the notebook:** Choose an experiment by id, load prompts from the DB, then run and save. Results are written to the `llm_prompt_results` table.

### Steps in `execution/runner.ipynb`

1. **Setup** — Install dependencies and imports.
2. **Create tables and seed** — Creates `experiment_setup`, `prompt`, `llm_prompt_results` and inserts definitions from `experiments.py` (run once).
3. **Available models** — List models and indices.
4. **Choose experiment** — Set `EXPERIMENT_ID` to an existing id or create one with `create_experiment()` and `add_prompts_bulk()`.
5. **Load prompts** — Load prompts for the chosen experiment from the database.
6. **Run and save** — Execute each prompt with the experiment’s model and decoding parameters; results are saved to the database.

## Prompt and experiment definitions (for DB insertion)

Defined in `execution/experiments.py` as a list of dicts. Each experiment has:

- `name`: unique label
- `model_key`: key from the integrations (e.g. `"gemini-2.0-flash"`)
- `temperature`, `top_p`, `max_tokens`: decoding parameters
- **Prompts** — use one of:
  - `prompts`: list of strings (each string is one prompt, multi-line allowed)
  - `prompts_file`: name of a file in `prompts/` (e.g. `"test-prompt.txt"`). File format: one or more prompts; if the file contains a line with only `---`, the file is split by that separator and each block is one prompt (multi-line blocks allowed)

Example:

```python
EXPERIMENTS = [
    {
        "name": "my_experiment",
        "model_key": "gemini-2.0-flash",
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 2048,
        "prompts": ["First prompt text.", "Second prompt."],
    },
    {
        "name": "from_file",
        "model_key": "gemini-2.0-flash",
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 2048,
        "prompts_file": "test-prompt.txt",
    },
]
```
