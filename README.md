# LLM Code Review on Smells

Run prompts on LLMs (OpenAI, Google Colab AI) for code review; experiments and results in PostgreSQL.

## Quick start

1. **Requirements:** Python 3.x, PostgreSQL. The notebook’s first cell installs dependencies (`openai`, `psycopg2-binary`).

2. **Config:** Edit `start_here/experiments/constants.py` — DB credentials (`RESULTS_DATABASE_*`), optional `OPENAI_API_KEY`.

3. **Run:** Open `start_here/notebooks/run_llm_prompt.ipynb` and run the cells in order:  
   - First cell: install deps + imports (run once).  
   - “Create tables and seed” cell: `load_database()` (run once).  
   - Then pick experiment, load prompts, run and save.

## Structure

- **start_here/experiments/** — `constants.py` (DB, API key, model keys), `definition.py` (experiment definitions).
- **database/** — `migrations.py` (schema), `experiment_log.py` (read/write experiments and results).
- **managers/** — `database_manager.py` (`load_database`), `prompt_input_manager.py`, `prompt_output_manager.py`.
- **start_here/notebooks/** — `run_llm_prompt.ipynb` (main), `process_dataset_mlcq.ipynb` (MLCQ pipeline).
- **integrations/** — LLM providers. **prompts/** — TXT files for `prompts_file` in experiments.

## Experiments

In `start_here/experiments/definition.py` each experiment has `name`, `model_key`, `temperature`, `top_p`, `max_tokens`, and either `prompts` (list of strings) or `prompts_file` (filename under `prompts/`). Use a line with only `---` in a file to separate multiple prompts.
