"""
Application dependencies and configuration.
"""
import logging
import os
from functools import lru_cache
from dotenv import load_dotenv

from app.services.interfaces import IPipelineService
from app.services.pipeline_impl import PipelineService

load_dotenv()

logger = logging.getLogger(__name__)


# Singleton instances
_pipeline_service: IPipelineService = None


class Settings:
    """Application settings from environment variables."""
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "network_ai")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    
    # Cache Configuration
    SCHEMA_CACHE_TTL: int = int(os.getenv("SCHEMA_CACHE_TTL", "3600"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Configuration
    API_TITLE: str = "Net-GPT"
    API_DESCRIPTION: str = "NLP to SQL query engine for network device data"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


def configure_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=get_settings().LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.info("Logging configured")


def get_pipeline_service() -> IPipelineService:
    """
    FastAPI dependency: Get pipeline service instance.
    
    Usage in routes:
        @router.post("/query")
        async def query(
            request: QueryRequest,
            pipeline: IPipelineService = Depends(get_pipeline_service)
        ):
            result = await pipeline.execute(request.question)
    """
    global _pipeline_service
    if _pipeline_service is None:
        _pipeline_service = PipelineService()
        logger.info("Pipeline service initialized")
    return _pipeline_service


def reset_pipeline_service() -> None:
    """Reset pipeline service for testing."""
    global _pipeline_service
    _pipeline_service = None
    logger.info("Pipeline service reset")
