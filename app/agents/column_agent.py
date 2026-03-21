import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt
from app.utils.decorators import log_function_call

logger = logging.getLogger(__name__)
llm = get_llm()


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
        
        logger.info(f"Selected columns: {columns[:100]}...")
        return columns
        
    except Exception as e:
        logger.error(f"Failed to select columns: {e}")
        raise ValueError(f"Failed to select columns: {str(e)}")