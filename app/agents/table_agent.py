import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt
from app.utils.decorators import log_function_call

logger = logging.getLogger(__name__)
llm = get_llm()


@log_function_call(log_args=True, log_result=False)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def select_tables(question: str, schema: str) -> str:
    """
    Select relevant tables for answering the question.
    
    Args:
        question: User's natural language question
        schema: Formatted database schema
        
    Returns:
        Comma-separated list of table names
        
    Raises:
        ValueError: If no tables can be selected
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string")
    
    if not schema or not isinstance(schema, str):
        raise ValueError("Schema must be a non-empty string")
    
    logger.debug(f"Selecting tables for: {question[:50]}...")
    
    try:
        prompt_template = load_prompt("table_prompt.txt")
        prompt = prompt_template.format(
            question=question,
            schema=schema
        )
        
        response = llm.invoke(prompt)
        tables = response.strip()
        
        if not tables:
            raise ValueError("No tables selected by LLM")
        
        # Validate format (comma-separated values)
        selected = [t.strip() for t in tables.split(",") if t.strip()]
        if not selected:
            raise ValueError("Invalid table format from LLM")
        
        logger.info(f"Selected tables: {tables}")
        return tables
        
    except Exception as e:
        logger.error(f"Failed to select tables: {e}")
        raise ValueError(f"Failed to select tables: {str(e)}")