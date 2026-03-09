# Notebooks

Ponto de entrada dos notebooks de execução do projeto.

| Notebook | Descrição |
|---------|-----------|
| **process_dataset_mlcq.ipynb** | Pipeline MLCQ: carrega CSV original, filtra (projetos relevantes), opcionalmente busca source code nos repositórios e gera SQL para a base. Dados em `datasets/`. |
| **run_llm_prompt.ipynb** | Executa prompts em modelos LLM (Colab AI, OpenAI). Experimentos e prompts em `execution/experiments.py`; resultados gravados no banco. |

Execute a partir da raiz do repositório ou abrindo o notebook nesta pasta (os paths são ajustados automaticamente).
