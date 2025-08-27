
import json
import yaml
import os
from typing import Any
from ...utils.logging import get_logger, get_structured_logger

def load_json(file_path: str) -> Any:
    logger = get_logger("causalllm.utils")
    struct_logger = get_structured_logger("utils")
    
    logger.info(f"Loading JSON file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        struct_logger.log_interaction(
            "load_json",
            {
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "data_type": type(data).__name__,
                "success": True
            }
        )
        
        logger.info(f"Successfully loaded JSON from {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        struct_logger.log_error(e, {"file_path": file_path})
        raise

def save_json(data: Any, file_path: str) -> None:
    logger = get_logger("causalllm.utils")
    struct_logger = get_structured_logger("utils")
    
    logger.info(f"Saving JSON to: {file_path}")
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size = os.path.getsize(file_path)
        
        struct_logger.log_interaction(
            "save_json",
            {
                "file_path": file_path,
                "file_size": file_size,
                "data_type": type(data).__name__,
                "success": True
            }
        )
        
        logger.info(f"Successfully saved JSON to {file_path} ({file_size} bytes)")
        
    except Exception as e:
        logger.error(f"Failed to save JSON to {file_path}: {e}")
        struct_logger.log_error(e, {"file_path": file_path, "data_type": type(data).__name__})
        raise

def load_yaml(file_path: str) -> Any:
    logger = get_logger("causalllm.utils")
    struct_logger = get_structured_logger("utils")
    
    logger.info(f"Loading YAML file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        struct_logger.log_interaction(
            "load_yaml",
            {
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "data_type": type(data).__name__,
                "success": True
            }
        )
        
        logger.info(f"Successfully loaded YAML from {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load YAML from {file_path}: {e}")
        struct_logger.log_error(e, {"file_path": file_path})
        raise

def save_yaml(data: Any, file_path: str) -> None:
    logger = get_logger("causalllm.utils")
    struct_logger = get_structured_logger("utils")
    
    logger.info(f"Saving YAML to: {file_path}")
    
    try:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        file_size = os.path.getsize(file_path)
        
        struct_logger.log_interaction(
            "save_yaml",
            {
                "file_path": file_path,
                "file_size": file_size,
                "data_type": type(data).__name__,
                "success": True
            }
        )
        
        logger.info(f"Successfully saved YAML to {file_path} ({file_size} bytes)")
        
    except Exception as e:
        logger.error(f"Failed to save YAML to {file_path}: {e}")
        struct_logger.log_error(e, {"file_path": file_path, "data_type": type(data).__name__})
        raise
