from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt
from app.utils.decorators import log_function_call
from app.utils.logger import get_logger

logger = get_logger(__name__, component="agents")
llm = get_llm()


@log_function_call(log_args=False, log_result=False)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def explain_query(sql: str, max_length: int = 500) -> str:
    """
    Generate a concise explanation of a SQL query.
    
    Args:
        sql: SQL query to explain
        max_length: Maximum length of explanation in characters (default: 500)
        
    Returns:
        Concise natural language explanation of the query (2-3 sentences max)
        
    Raises:
        ValueError: If explanation generation fails
    """
    if not sql or not isinstance(sql, str):
        raise ValueError("SQL must be a non-empty string")
    
    if max_length < 100:
        max_length = 100
    
    logger.debug(f"Explaining query: {sql[:50]}...")
    
    try:
        prompt_template = load_prompt("explain_prompt.txt")
        prompt = prompt_template.format(sql=sql)
        
        response = llm.invoke(prompt)
        explanation = response.strip()
        
        if not explanation:
            logger.warning("Empty explanation generated")
            return "No explanation available"
        
        # Truncate if too long (keep it to-the-point)
        if len(explanation) > max_length:
            explanation = explanation[:max_length].rsplit(" ", 1)[0] + "..."
            logger.debug(f"Explanation truncated to {len(explanation)} chars")
        
        logger.debug(f"Generated explanation: {explanation[:100]}...")
        return explanation
        
    except Exception as e:
        logger.error(f"Failed to explain query: {e}")
        raise ValueError(f"Failed to explain query: {str(e)}")