import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.routers import query
from app.utils.logging_config import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)

logger = get_logger(__name__)

app = FastAPI(
    title="Net-GPT",
    description="NLP to SQL query engine for network device data",
    version="1.0.0"
)

app.include_router(query.router, tags=["query"])

logger.info("Net-GPT application started")