from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt
from app.utils.decorators import log_function_call
from app.utils.logger import get_logger

logger = get_logger(__name__, component="agents")
llm = get_llm()


def _parse_schema_to_columns(schema: str) -> Dict[str, set]:
    """
    Parse formatted schema to extract valid columns per table.
    
    Args:
        schema: Formatted schema string from format_schema (e.g., "table1(col1, col2)\ntable2(col3)")
        
    Returns:
        Dict mapping table names to set of valid column names
    """
    valid_columns = {}
    try:
        for line in schema.strip().split("\n"):
            if "(" in line and ")" in line:
                table_name = line.split("(")[0].strip()
                cols_str = line.split("(")[1].split(")")[0].strip()
                if cols_str:
                    cols = [c.strip() for c in cols_str.split(",")]
                    valid_columns[table_name] = set(cols)
        return valid_columns
    except Exception as e:
        logger.warning(f"Failed to parse schema: {e}")
        return {}


def _filter_valid_columns(columns_str: str, valid_columns: Dict[str, set]) -> str:
    """
    Filter selected columns to only include those that exist in schema.
    
    Args:
        columns_str: Comma-separated columns (e.g., "table.col1, table.col2")
        valid_columns: Dict of table -> set of valid column names
        
    Returns:
        Filtered columns string with only valid columns
    """
    if not columns_str or not valid_columns:
        return columns_str
    
    valid_cols = []
    invalid_cols = []
    
    for col in columns_str.split(","):
        col = col.strip()
        if "." in col:
            table, column = col.split(".", 1)
            table = table.strip()
            column = column.strip()
            
            if table in valid_columns and column in valid_columns[table]:
                valid_cols.append(col)
            else:
                invalid_cols.append(col)
        else:
            # Column without table prefix - can't validate, include it
            valid_cols.append(col)
    
    if invalid_cols:
        logger.warning(f"Filtered out invalid columns: {', '.join(invalid_cols)}")
    
    return ", ".join(valid_cols) if valid_cols else columns_str


@log_function_call(log_args=True, log_result=False)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def select_columns(question: str, tables: str, schema: str) -> str:
    """
    Select relevant columns for the given tables.
    
    Args:
        question: User's natural language question
        tables: Comma-separated list of table names
        schema: Formatted database schema
        
    Returns:
        Selected columns description
        
    Raises:
        ValueError: If columns cannot be selected
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string")
    
    if not tables or not isinstance(tables, str):
        raise ValueError("Tables must be a non-empty string")
    
    if not schema or not isinstance(schema, str):
        raise ValueError("Schema must be a non-empty string")
    
    logger.debug(f"Selecting columns for tables: {tables}")
    
    try:
        prompt_template = load_prompt("column_prompt.txt")
        prompt = prompt_template.format(
            question=question,
            tables=tables,
            schema=schema
        )
        
        response = llm.invoke(prompt)
        columns = response.strip()
        
        if not columns:
            logger.warning("No columns selected, returning empty string")
            return ""
        
        # Parse schema to get valid columns per table
        valid_columns = _parse_schema_to_columns(schema)
        
        # Filter LLM response to only include valid columns (prevents hallucination)
        filtered_columns = _filter_valid_columns(columns, valid_columns)
        
        logger.info(f"Selected columns: {filtered_columns[:100]}...")
        return filtered_columns
        
    except Exception as e:
        logger.error(f"Failed to select columns: {e}")
        raise ValueError(f"Failed to select columns: {str(e)}")