import os
import logging
from typing import Dict, Any
from mysql.connector import pooling
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

dbconfig = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "network_ai")
}

try:
    pool = pooling.MySQLConnectionPool(
        pool_name="network_ai_pool",
        pool_size=int(os.getenv("DB_POOL_SIZE", 5)),
        **dbconfig
    )
    logger.info("Database connection pool initialized")
except Exception as e:
    logger.error(f"Failed to initialize database connection pool: {e}")
    raise


def get_db_connection():
    """Get a database connection from the pool."""
    try:
        return pool.get_connection()
    except mysql.connector.Error as e:
        logger.error(f"Failed to get database connection: {e}")
        raise


def execute_query(sql: str) -> Dict[str, Any]:
    """Execute a SQL query and return the result."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        logger.debug(f"Executing query: {sql[:100]}...")
        cursor.execute(sql)
        result = cursor.fetchall()
        logger.debug(f"Query returned {len(result)} rows")
        return {"status": "success", "data": result, "count": len(result)}
    except mysql.connector.Error as e:
        logger.error(f"Database error: [{e.errno}] {e.msg}")
        return {"status": "error", "error_code": e.errno, "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error during query execution: {e}")
        return {"status": "error", "error_code": -1, "message": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to close connection: {e}")