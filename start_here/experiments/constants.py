import os
from pathlib import Path

from integrations.colab_llm_provider import COLAB_MODELS
from integrations.openai_llm_provider import OPENAI_MODELS

_project_root = Path(__file__).resolve().parent.parent.parent
PROMPTS_DIR = _project_root / "prompts"
RESULTS_DIR = _project_root / "results"
PROMPTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

PROMPTS_FILE = "code-review-prompt-v4.txt"

TEMPERATURE = 0.0
TOP_P = 1.0
MAX_TOKENS = 2048

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

RESULTS_DATABASE_NAME = "datasets_db"
RESULTS_DATABASE_HOST = "localhost"
RESULTS_DATABASE_PORT = 5432
RESULTS_DATABASE_USER = "postgres"
RESULTS_DATABASE_PASSWORD = "postgres"

LABEL_STUDIO_PORT = 9180
LABEL_STUDIO_URL = f"http://localhost:{LABEL_STUDIO_PORT}"
LABEL_STUDIO_DATABASE_NAME = "labelstudio_db"
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY", "")
LABEL_STUDIO_PROJECT_TITLE = "LLM Code Review — IHMU"
LABEL_STUDIO_LABEL_CONFIG_VERSION = "v1"
LABEL_STUDIO_DEFAULT_ANNOTATOR = "marcelo"

MODEL_PROVIDERS = {k: "colab" for k in COLAB_MODELS} | {k: "openai" for k in OPENAI_MODELS}
MODEL_KEYS = list(MODEL_PROVIDERS.keys())
