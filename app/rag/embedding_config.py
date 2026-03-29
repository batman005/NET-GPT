"""
Embedding model configuration for RAG system.
Uses OllamaEmbeddings with nomic-embed-text model.
"""

import logging
from langchain_ollama import OllamaEmbeddings
from app.utils.logger import get_logger

logger = get_logger(__name__, component="rag")


class EmbeddingConfig:
    """Configuration for embedding models."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize embedding configuration.
        
        Args:
            base_url: Ollama server URL
        """
        self.base_url = base_url
        self._embeddings = None
    
    @property
    def embeddings(self) -> OllamaEmbeddings:
        """Get or create embeddings instance (lazy loading)."""
        if self._embeddings is None:
            logger.info(f"Initializing OllamaEmbeddings with nomic-embed-text")
            self._embeddings = OllamaEmbeddings(
                model="nomic-embed-text",
                base_url=self.base_url
            )
        return self._embeddings
    
    def test_connection(self) -> bool:
        """
        Test if Ollama embedding model is available.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try a simple embedding to verify connection
            test_embedding = self.embeddings.embed_query("test")
            logger.info(f"Embedding model connection successful (vector dim: {len(test_embedding)})")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to embedding model: {e}")
            return False


# Global embedding config instance
_embedding_config = None


def get_embedding_config(base_url: str = "http://localhost:11434") -> EmbeddingConfig:
    """
    Get or create global embedding configuration instance.
    
    Args:
        base_url: Ollama server URL
        
    Returns:
        EmbeddingConfig instance
    """
    global _embedding_config
    if _embedding_config is None:
        _embedding_config = EmbeddingConfig(base_url=base_url)
    return _embedding_config


def get_embeddings(base_url: str = "http://localhost:11434") -> OllamaEmbeddings:
    """
    Get embeddings instance directly.
    
    Args:
        base_url: Ollama server URL
        
    Returns:
        OllamaEmbeddings instance
    """
    return get_embedding_config(base_url).embeddings
