"""
Output Result Generator

Saves execution results to JSON files in the results/ directory.
Generates timestamped filenames automatically.
"""
import json
from typing import List, Dict
from datetime import datetime
from constants.constants import RESULTS_DIR


def save_results(
    results: List[Dict],
    model_key: str,
    model_name: str,
    output_file: str = None
) -> str:
    """Save results to a JSON file in the results directory
    
    Args:
        results: List of result dictionaries to save
        model_key: Model key used for execution
        model_name: Actual model name used
        output_file: Optional custom filename (default: auto-generated with timestamp)
        
    Returns:
        Path to the saved file
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Clean model key for filename
        clean_model_key = model_key.replace('/', '_').replace('\\', '_')
        output_file = f"results_{clean_model_key}_{timestamp}.json"
    
    # Ensure output is in results directory
    output_path = RESULTS_DIR / output_file
    
    output_data = {
        'model_key': model_key,
        'model_name': model_name,
        'timestamp': datetime.now().isoformat(),
        'total_prompts': len(results),
        'results': results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    return str(output_path)
