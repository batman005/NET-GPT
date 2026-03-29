import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from app.routers import query
from app.utils.logger import setup_logging, get_logger
from app.rag.faiss_retriever import initialize_rag
from app.rag.embedding_config import get_embedding_config

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)

logger = get_logger(__name__, component="api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    Replaces deprecated @app.on_event() decorators.
    """
    # Startup
    logger.info("=" * 70)
    logger.info("Net-GPT Starting...")
    logger.info("=" * 70)
    
    # Test embedding model connection
    logger.info("Testing embedding model connection...")
    embedding_config = get_embedding_config()
    if embedding_config.test_connection():
        logger.info("Embedding model ready")
    else:
        logger.warning("Embedding model connection failed - RAG may not work")
    
    # Initialize RAG system
    logger.info("Initializing RAG system...")
    if initialize_rag():
        logger.info("RAG system initialized")
    else:
        logger.warning("RAG system initialization failed - continuing without RAG")
    
    logger.info("=" * 70)
    logger.info("Net-GPT ready")
    logger.info("=" * 70)
    
    yield
    
    # Shutdown (if needed in future)
    logger.info("Net-GPT shutting down...")


app = FastAPI(
    title="Net-GPT",
    description="NLP to SQL query engine for network device data",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(query.router, tags=["query"])

logger.info("Net-GPT application loaded")