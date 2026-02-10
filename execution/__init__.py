"""
Execution Package

This package contains execution-related utilities:
- input_prompt_reader: Read prompts from files
- output_result_generator: Save results to files
"""
from execution.input_prompt_reader import read_from_file
from execution.output_result_generator import save_results

__all__ = ['read_from_file', 'save_results']
