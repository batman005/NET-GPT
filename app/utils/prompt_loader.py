import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def load_prompt(filename: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        filename: Name of the prompt file (e.g., 'intent_prompt.txt')
        
    Returns:
        Content of the prompt file
        
    Raises:
        FileNotFoundError: If prompt file doesn't exist
        IOError: If prompt file cannot be read
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")
    
    try:
        base_path = Path(__file__).resolve().parent.parent
        prompt_path = base_path / "prompts" / filename
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        logger.debug(f"Loading prompt: {filename}")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not content:
            logger.warning(f"Prompt file is empty: {filename}")
        
        return content
        
    except Exception as e:
        logger.error(f"Failed to load prompt {filename}: {e}")
        raise