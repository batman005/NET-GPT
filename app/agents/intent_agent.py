import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt
from app.utils.decorators import log_function_call

logger = logging.getLogger(__name__)
llm = get_llm()

VALID_INTENTS = ["network_query", "topology_query", "device_lookup", "metrics_query", "alert_query"]


@log_function_call(log_args=True, log_result=False)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def detect_intent(question: str) -> str:
    """
    Detect the intent of the user's question.
    
    Args:
        question: User's natural language question
        
    Returns:
        Intent classification (e.g., 'topology_query', 'device_lookup')
        
    Raises:
        ValueError: If intent cannot be detected or is invalid
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string")
    
    logger.debug(f"Detecting intent for: {question[:50]}...")
    
    try:
        prompt_template = load_prompt("intent_prompt.txt")
        prompt = prompt_template.format(question=question)
        
        response = llm.invoke(prompt)
        intent = response.strip().lower()
        
        logger.debug(f"Raw intent response: {intent}")
        
        # Validate intent is one of the allowed values
        if intent not in VALID_INTENTS:
            logger.warning(f"Invalid intent detected: {intent}. Defaulting to 'network_query'")
            intent = "network_query"  # Fallback to default intent
        
        logger.info(f"Detected intent: {intent}")
        return intent
        
    except Exception as e:
        logger.error(f"Failed to detect intent: {e}")
        raise ValueError(f"Failed to detect intent: {str(e)}")