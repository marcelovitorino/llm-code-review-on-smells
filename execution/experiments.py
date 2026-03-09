from constants.constants import TEMPERATURE, TOP_P, MAX_TOKENS

EXPERIMENTS = [
    {
        "name": "test_gemini_flash",
        "model_key": "gemini-2.0-flash",
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "max_tokens": MAX_TOKENS,
        "prompts": [
            "Hi, how are you?",
        ],
    },
    {
        "name": "test_from_file",
        "model_key": "gemini-2.0-flash",
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "max_tokens": MAX_TOKENS,
        "prompts_file": "test-prompt.txt",
    },
]
