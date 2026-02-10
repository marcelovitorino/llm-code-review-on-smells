# LLM Code Review on Smells

Tool to run prompts on Large Language Models (LLMs) for code review with focus on smells. Supports multiple providers (OpenAI and Google Colab AI) and saves results to JSON.

## Project Structure

```
llm-code-review-on-smells/
├── constants/          # Configuration and constants
├── execution/          # Prompt reading, result generation, and main runner
│   └── runner.ipynb    # Main execution notebook
├── integrations/       # LLM providers (OpenAI, Colab)
├── prompts/            # TXT prompt files (created automatically)
└── results/            # JSON results (created automatically)
```

## Requirements

- Python 3.x
- For OpenAI: `pip install openai` and API key configured
- For Colab: Google Colab (integration only works in Colab environment)

## Supported Models

| Provider         | Models                                                  |
| ---------------- | ------------------------------------------------------- |
| **Colab**  | Gemini 2.0 Flash, Gemini 2.0 Flash Lite, Gemini 1.5 Pro |
| **OpenAI** | GPT-4.1, GPT-4, GPT-4 Turbo, GPT-3.5 Turbo              |

## Configuration

1. **OpenAI (local development):** Set the API key in `constants/constants.py` (`OPENAI_API_KEY`) or via environment variable. Do not commit real keys to the repository.
2. **Colab:** Open `execution/runner.ipynb` in Google Colab. Gemini models will be used via `google.colab.ai`.

## Usage

1. Place your prompts in `.txt` files in the `prompts/` directory.
2. Use `---` on its own line to separate multiple prompts in the same file.
3. Open `execution/runner.ipynb` and run the cells in order.

### Steps in `execution/runner.ipynb`

The notebook runs the following steps:

1. **Setup** — Install dependencies and import integrations, readers, and constants.
2. **List available models** — Print all models with their indices; use `MODEL_KEYS[i]` to select one.
3. **Choose model and decoding setup** — Set `MODEL = MODEL_KEYS[i]` and confirm decoding parameters (temperature, top_p, max_tokens).
4. **Define prompts** — Read prompts from a TXT file in `prompts/` via `read_from_file(PROMPTS_FILE)` (default: `test-prompt.txt`). Prompts separated by `---`; each can be multi-line.
5. **Run and save** — Execute each prompt with the selected model, collect results, and save to a timestamped JSON file in `results/`.
