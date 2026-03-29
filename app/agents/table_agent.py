import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt
from app.utils.decorators import log_function_call
from app.rag.rag_service import get_rag_service

logger = logging.getLogger(__name__)
llm = get_llm()


@log_function_call(log_args=True, log_result=False)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def select_tables(question: str, schema: str) -> str:
    """
    Select relevant tables for answering the question using RAG enhancement.
    
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
        # ===== RAG Enhancement: Retrieve relevant context =====
        rag_service = get_rag_service()
        rag_context = rag_service.retrieve_context_for_query(question)
        
        logger.info(f"RAG Retrieved: {len(rag_context.get('tables', []))} tables, "
                   f"{len(rag_context.get('join_patterns', []))} join patterns, "
                   f"{len(rag_context.get('example_queries', []))} examples")
        
        # ===== Load base prompt template =====
        prompt_template = load_prompt("table_prompt.txt")
        
        # ===== Build enhanced prompt with RAG context =====
        # Add RAG context to the prompt
        rag_tables_hint = ""
        if rag_context.get('tables'):
            rag_tables_hint = f"\n\nBased on semantic analysis, these tables appear relevant:\n"
            rag_tables_hint += ", ".join(rag_context['tables'])
        
        rag_joins_hint = ""
        if rag_context.get('join_patterns'):
            rag_joins_hint = f"\n\nCommon join patterns that might be useful:\n"
            for i, join in enumerate(rag_context['join_patterns'][:2], 1):
                # Extract join name
                lines = join.split("\n")
                join_name = next((l.replace("Join Pattern:", "").strip() 
                                for l in lines if "Join Pattern:" in l), f"Join {i}")
                rag_joins_hint += f"  - {join_name}\n"
        
        # Combine original schema with RAG enhancements
        enhanced_schema = schema + rag_tables_hint + rag_joins_hint
        
        prompt = prompt_template.format(
            question=question,
            schema=enhanced_schema
        )
        
        logger.debug(f"Enhanced prompt length: {len(prompt)} chars")
        
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