"""
Centralized constants for the LLM Prompt Runner.

- PROMPTS_DIR, RESULTS_DIR: prompt and result directories
- MODEL_PROVIDERS: model key -> provider ('colab' | 'openai'); use MODEL_PROVIDERS for lookup and MODEL_KEYS[i] to choose by index
- MODEL_KEYS: ordered list of model keys (derived from MODEL_PROVIDERS)
- PROMPTS_FILE: default prompts file name under prompts/
"""
from pathlib import Path

from integrations.colab_llm_provider import COLAB_MODELS
from integrations.openai_llm_provider import OPENAI_MODELS

# Directories
PROMPTS_DIR = Path("prompts")
RESULTS_DIR = Path("results")
PROMPTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Models: single source — key -> provider; MODEL_KEYS is the ordered list of keys
MODEL_PROVIDERS = {k: "colab" for k in COLAB_MODELS} | {k: "openai" for k in OPENAI_MODELS}
MODEL_KEYS = list(MODEL_PROVIDERS.keys())

PROMPTS_FILE = "test-prompt.txt"

# Decoding parameters (fixed for all experiments)
TEMPERATURE = 0.0
TOP_P = 1.0
MAX_TOKENS = 2048

# OpenAI API key (optional; use for local development and DO NOT commit real values).
# Fill this locally with your key; keep it as None in the repository.
OPENAI_API_KEY = ''

# PostgreSQL (results stored in llm_prompt_results table)
RESULTS_DATABASE_NAME = "datasets_db"
RESULTS_DATABASE_HOST = "localhost"
RESULTS_DATABASE_PORT = 5432
RESULTS_DATABASE_USER = "postgres"
RESULTS_DATABASE_PASSWORD = "postgres"
