import re
import logging
from typing import Optional
import sqlparse

logger = logging.getLogger(__name__)


def extract_sql(text: str) -> Optional[str]:
    """
    Extract SQL query from text.
    Handles markdown blocks, multiple queries, and complex formatting.
    """
    if not text or not isinstance(text, str):
        logger.warning("Invalid input to extract_sql")
        return None
    
    # Remove markdown code blocks
    text = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*$", "", text)
    
    # Try parsing with sqlparse
    try:
        statements = sqlparse.parse(text)
        
        for statement in statements:
            # Look for SELECT statements
            if statement.get_type().upper() == 'SELECT':
                sql = str(statement).strip()
                # Ensure it ends with semicolon
                if not sql.endswith(';'):
                    sql += ';'
                logger.debug(f"Extracted SQL: {sql[:100]}...")
                return sql
    except Exception as e:
        logger.warning(f"sqlparse failed: {e}, falling back to regex")
    
    # Fallback: regex extraction
    match = re.search(r"(SELECT\s+.*?;)", text, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
        logger.debug(f"Extracted SQL via regex: {sql[:100]}...")
        return sql
    
    logger.warning("No valid SQL found in text")
    return None