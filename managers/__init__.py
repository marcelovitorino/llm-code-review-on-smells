"""
Managers package: orchestration and entrypoints.

- prompt_input_manager: Read prompts from files
- prompt_output_manager: Save results to database
- database_manager: load_database() creates tables and seeds experiments/prompts
"""
from managers.prompt_input_manager import read_from_file
from managers.prompt_output_manager import save_results
from managers.database_manager import load_database

__all__ = ["read_from_file", "save_results", "load_database"]
