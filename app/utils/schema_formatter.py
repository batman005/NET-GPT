import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def format_schema(schema: Dict[str, List[str]]) -> str:
    """
    Format database schema into readable text format.
    
    Args:
        schema: Dictionary mapping table names to list of column names
        
    Returns:
        Formatted schema string (one line per table with columns)
    """
    if not schema or not isinstance(schema, dict):
        logger.warning("Empty or invalid schema provided")
        return ""
    
    try:
        formatted_lines = []
        
        for table, columns in sorted(schema.items()):
            if not columns:
                logger.warning(f"Table {table} has no columns")
                formatted_lines.append(f"{table}()")
            else:
                # Sort columns for consistency
                sorted_cols = sorted(columns)
                cols_str = ", ".join(sorted_cols)
                formatted_lines.append(f"{table}({cols_str})")
        
        formatted = "\n".join(formatted_lines)
        logger.debug(f"Formatted schema: {len(formatted_lines)} tables, {len(formatted)} chars")
        return formatted
        
    except Exception as e:
        logger.error(f"Failed to format schema: {e}")
        return ""