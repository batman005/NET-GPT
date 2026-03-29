"""
RAG Service orchestrator - manages RAG pipeline for query context.
Provides semantic retrieval of tables, joins, and examples.
"""

import logging
from typing import Dict, List, Any, Set
from app.rag.faiss_retriever import get_faiss_retriever, FAISSRetriever

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG Service for Net-GPT.
    Provides schema-aware context retrieval for SQL generation.
    """
    
    def __init__(self):
        """Initialize RAG service."""
        self.retriever: FAISSRetriever = get_faiss_retriever()
    
    def retrieve_context_for_query(self, user_query: str, k: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant context for a user query.
        
        This is the main entry point for RAG.
        
        Args:
            user_query: Natural language query from user
            k: Number of top documents to retrieve
            
        Returns:
            Dictionary containing:
                - tables: List of relevant table names
                - join_patterns: List of relevant join examples
                - example_queries: List of similar example queries
                - raw_context: Full context string for LLM
                - retrieved_docs: Number of documents retrieved
        """
        logger.info(f"Retrieving RAG context for: {user_query[:100]}")
        context = self.retriever.retrieve_context(user_query)
        return context
    
    def get_recommended_prompt_context(self, user_query: str) -> str:
        """
        Get formatted context for use in LLM prompts.
        
        Args:
            user_query: User query
            
        Returns:
            Formatted context string for prompt
        """
        context = self.retrieve_context_for_query(user_query)
        
        prompt_context = "=== SCHEMA CONTEXT (Retrieved by RAG) ===\n\n"
        
        # Add tables
        if context["tables"]:
            prompt_context += f"Relevant Tables:\n"
            for table in context["tables"]:
                prompt_context += f"  - {table}\n"
            prompt_context += "\n"
        
        # Add join patterns
        if context["join_patterns"]:
            prompt_context += f"Suggested Join Patterns:\n"
            for i, join in enumerate(context["join_patterns"][:2], 1):  # Top 2 joins
                # Extract join name from content
                lines = join.split("\n")
                pattern_name = lines[0].replace("Join Pattern:", "").strip() if lines else "Join"
                prompt_context += f"  {i}. {pattern_name}\n"
            prompt_context += "\n"
        
        # Add example queries
        if context["example_queries"]:
            prompt_context += f"Similar Query Examples:\n"
            for i, example in enumerate(context["example_queries"][:2], 1):  # Top 2 examples
                lines = example.split("\n")
                query_type = next((l.replace("Query Type:", "").strip() 
                                  for l in lines if "Query Type:" in l), "Query")
                prompt_context += f"  {i}. {query_type}\n"
            prompt_context += "\n"
        
        prompt_context += "=== END SCHEMA CONTEXT ===\n"
        
        return prompt_context
    
    def get_table_details(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table schema details
        """
        return self.retriever.get_table_schema(table_name)
    
    def get_all_available_tables(self) -> List[str]:
        """
        Get list of all available tables in the schema.
        
        Returns:
            List of table names
        """
        return self.retriever.get_all_tables()
    
    def validate_tables_exist(self, table_names: Set[str]) -> Dict[str, bool]:
        """
        Validate if tables exist in schema.
        
        Args:
            table_names: Set of table names to validate
            
        Returns:
            Dictionary mapping table names to existence boolean
        """
        available_tables = set(self.get_all_available_tables())
        return {
            table: table.lower() in {t.lower() for t in available_tables}
            for table in table_names
        }
    
    def is_initialized(self) -> bool:
        """Check if RAG system is initialized."""
        return self.retriever.documents_built


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGService:
    """
    Get or create global RAG service instance.
    
    Returns:
        RAGService instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
