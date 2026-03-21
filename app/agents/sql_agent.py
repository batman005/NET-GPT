import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt
from app.utils.decorators import log_function_call

logger = logging.getLogger(__name__)
llm = get_llm()


@log_function_call(log_args=True, log_result=False)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_sql(question: str, tables: str, columns: str, schema: str) -> str:
    """
    Generate SQL query for the user's question.
    
    Args:
        question: User's natural language question
        tables: Selected table names
        columns: Selected columns
        schema: Formatted database schema
        
    Returns:
        Generated SQL query (may include markdown formatting)
        
    Raises:
        ValueError: If SQL generation fails
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string")
    
    if not tables or not isinstance(tables, str):
        raise ValueError("Tables must be a non-empty string")
    
    if not schema or not isinstance(schema, str):
        raise ValueError("Schema must be a non-empty string")
    
    logger.debug(f"Generating SQL for question: {question[:50]}...")
    
    try:
        prompt_template = load_prompt("sql_prompt.txt")
        prompt = prompt_template.format(
            question=question,
            tables=tables,
            columns=columns,
            schema=schema
        )
        
        response = llm.invoke(prompt)
        sql_text = response.strip()
        
        if not sql_text:
            raise ValueError("Empty SQL generated")
        
        logger.debug(f"Generated SQL: {sql_text[:100]}...")
        return sql_text
        
    except Exception as e:
        logger.error(f"Failed to generate SQL: {e}")
        raise ValueError(f"Failed to generate SQL: {str(e)}")