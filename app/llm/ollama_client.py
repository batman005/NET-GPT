import os
import logging
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

load_dotenv()

logger = logging.getLogger(__name__)


def get_llm() -> OllamaLLM:
    """Initialize and return Ollama LLM client."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    
    logger.debug(f"Initializing Ollama with model: {model} at {host}")
    
    return OllamaLLM(
        base_url=host,
        model=model,
        temperature=0.1
    )