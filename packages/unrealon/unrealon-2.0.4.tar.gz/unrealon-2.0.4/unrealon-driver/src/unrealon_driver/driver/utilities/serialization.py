"""
Serialization utilities for driver components.

Handles result saving and JSON serialization with Pydantic support.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SerializationUtility:
    """Utility class for serialization and result saving."""
    
    @staticmethod
    def save_results_to_file(data: dict, filename: str, results_dir: Optional[str] = None) -> Path:
        """
        Save parsing results to JSON file with automatic serialization.
        
        Args:
            data: Data to save (can contain Pydantic models)
            filename: Base filename (without extension)
            results_dir: Directory to save to (default: ./data/results)
            
        Returns:
            Path to saved file
        """
        if results_dir is None:
            results_dir = "./data/results"
        
        results_path = Path(results_dir)
        results_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = results_path / f"{filename}_{timestamp}.json"
        
        # Convert Pydantic models to dict for JSON serialization
        serializable_data = SerializationUtility._serialize_for_json(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Results saved to: {filepath}")
        return filepath
    
    @staticmethod
    def _serialize_for_json(data: Any) -> Any:
        """Recursively serialize data for JSON, handling Pydantic models."""
        if hasattr(data, "model_dump"):
            # Pydantic v2 model
            return data.model_dump()
        elif isinstance(data, dict):
            return {key: SerializationUtility._serialize_for_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [SerializationUtility._serialize_for_json(item) for item in data]
        else:
            return data
