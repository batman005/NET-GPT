import os
import time
from typing import Dict, List
from dotenv import load_dotenv
from app.db.mysql_client import get_db_connection
from app.utils.decorators import log_execution_time, cache_result, handle_errors
from app.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__, component="db")

# Get cache TTL from environment
_CACHE_TTL: int = int(os.getenv("SCHEMA_CACHE_TTL", "3600"))

# Initialize cache variables
_schema_cache: Dict[str, List[str]] = None
_schema_cache_time: float = None


@log_execution_time
@cache_result(ttl_seconds=_CACHE_TTL)
@handle_errors(default_return={})
def load_schema() -> Dict[str, List[str]]:
    """Load database schema from MySQL, with caching."""
    
    logger.info("Loading schema from database...")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        db_name = os.getenv("DB_NAME", "network_ai")
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY table_name, ordinal_position
        """, (db_name,))
        
        rows = cursor.fetchall()
        
        schema = {}
        for table, column in rows:
            if table not in schema:
                schema[table] = []
            schema[table].append(column)
        
        # Update cache
        _schema_cache = schema
        _schema_cache_time = time.time()
        logger.info(f"Schema loaded: {len(schema)} tables cached")
        
        return schema
    
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        # Return cached schema even if expired, better than nothing
        if _schema_cache is not None:
            logger.warning("Returning stale cached schema due to load error")
            return _schema_cache
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to close connection: {e}")


def clear_schema_cache() -> None:
    """Manually clear the schema cache."""
    global _schema_cache, _schema_cache_time
    _schema_cache = None
    _schema_cache_time = None
    logger.info("Schema cache cleared")


