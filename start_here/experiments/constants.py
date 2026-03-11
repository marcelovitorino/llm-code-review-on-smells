from pathlib import Path

from integrations.colab_llm_provider import COLAB_MODELS
from integrations.openai_llm_provider import OPENAI_MODELS

PROMPTS_DIR = Path("prompts")
RESULTS_DIR = Path("results")
PROMPTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

PROMPTS_FILE = "test-prompt.txt"

TEMPERATURE = 0.0
TOP_P = 1.0
MAX_TOKENS = 2048

OPENAI_API_KEY = ""

RESULTS_DATABASE_NAME = "datasets_db"
RESULTS_DATABASE_HOST = "localhost"
RESULTS_DATABASE_PORT = 5432
RESULTS_DATABASE_USER = "postgres"
RESULTS_DATABASE_PASSWORD = "postgres"

MODEL_PROVIDERS = {k: "colab" for k in COLAB_MODELS} | {k: "openai" for k in OPENAI_MODELS}
MODEL_KEYS = list(MODEL_PROVIDERS.keys())
