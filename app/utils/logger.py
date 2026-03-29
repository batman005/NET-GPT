"""
Simple logging system for Net-GPT.
Each component logs to its own file. No duplication, no complexity.
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

# Log directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"

# Component log files
COMPONENT_LOGS = {
    "pipeline": "pipeline.log",
    "agents": "agents.log",
    "rag": "rag.log",
    "db": "db.log",
    "llm": "llm.log",
    "api": "api.log",
    "query": "query.log",
    "error": "error.log",
}

# Settings
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 3
LOG_LEVEL = "INFO"

# Track if setup is done
_loggers = {}
_setup_done = False


class SimpleFormatter(logging.Formatter):
    """Simple one-line format: [LEVEL] module | message"""
    
    def format(self, record):
        return (
            f"[{record.levelname}] "
            f"{record.name} | "
            f"{record.getMessage()}"
        )


def get_logger(name: str, component: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a module, optionally routing to a specific component file.
    
    Args:
        name: Module name (typically __name__)
        component: Optional component name (pipeline, agents, rag, db, llm, api, query)
    
    Returns:
        logging.Logger: Configured logger
    
    Example:
        logger = get_logger(__name__, component="pipeline")
        logger.info("Pipeline started")
    """
    global _setup_done
    
    # Setup logging on first call
    if not _setup_done:
        _setup_logging()
    
    # Get or create logger
    logger_name = name
    if component:
        logger_name = f"{name}.{component}"
    
    logger = logging.getLogger(logger_name)
    
    # If component-specific, add handler for that component's log file
    if component and component in COMPONENT_LOGS:
        # Remove any existing handlers to avoid duplication
        logger.handlers = []
        logger.propagate = False
        
        # Set logger level to DEBUG so messages aren't filtered before reaching handler
        logger.setLevel(logging.DEBUG)
        
        # Add component-specific handler
        log_file = LOGS_DIR / COMPONENT_LOGS[component]
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        handler.setFormatter(SimpleFormatter())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    
    return logger


def _setup_logging():
    """Initialize logging system with console and error log."""
    global _setup_done
    
    # Create logs directory
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create logs directory: {e}")
        return
    
    # Configure root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    # Remove old handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    # Console handler (all INFO and above)
    console = logging.StreamHandler()
    console.setLevel(LOG_LEVEL)
    console.setFormatter(SimpleFormatter())
    root.addHandler(console)
    
    # Error-only log file
    try:
        error_log = LOGS_DIR / COMPONENT_LOGS["error"]
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(SimpleFormatter())
        root.addHandler(error_handler)
    except Exception as e:
        print(f"Warning: Could not create error log: {e}")
    
    _setup_done = True


def setup_logging(log_level: str = "INFO"):
    """
    Set up logging system.
    
    Args:
        log_level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    global LOG_LEVEL, _setup_done
    LOG_LEVEL = log_level
    _setup_done = False
    _setup_logging()
