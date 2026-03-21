"""
Simple logging setup for Net-GPT.
Logs to console (colored) and files (JSON format).
"""
import logging
import logging.handlers
import os
import json
from datetime import datetime
from pathlib import Path

# Log directory - created only once when needed
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"

# Log files (relative to LOGS_DIR)
APP_LOG_FILE = LOGS_DIR / "app.log"
ERROR_LOG_FILE = LOGS_DIR / "error.log"

# Settings
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 3

# Track if setup was already called
_setup_done = False


class SimpleJSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing."""
    
    def format(self, record):
        try:
            log_data = {
                "time": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
                "module": record.module,
            }
            return json.dumps(log_data)
        except Exception as e:
            return f"ERROR formatting log: {str(e)}"


class SimpleTextFormatter(logging.Formatter):
    """Simple text format for console."""
    
    def format(self, record):
        return f"[{record.levelname:8}] {record.name:25} | {record.getMessage()}"


def setup_logging(log_level: str = "INFO"):
    """
    Setup logging to console and files.
    
    Args:
        log_level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    global _setup_done
    
    # Only setup once
    if _setup_done:
        return
    
    _setup_done = True
    
    # Create logs directory once
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create logs directory: {e}")
        return
    
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # Capture everything
    
    # Remove old handlers (in case setup is called again)
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    # Console handler (human readable)
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(SimpleTextFormatter())
    root.addHandler(console)
    
    # File handler - all logs (JSON)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            APP_LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(SimpleJSONFormatter())
        root.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")
    
    # File handler - errors only
    try:
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(SimpleJSONFormatter())
        root.addHandler(error_handler)
    except Exception as e:
        print(f"Warning: Could not create error handler: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get logger for a module."""
    return logging.getLogger(name)


