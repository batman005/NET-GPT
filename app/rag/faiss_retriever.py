"""
FAISS-based retriever for schema-aware document retrieval.
Builds and manages vector store for database schema, joins, and examples.
"""

import logging
from typing import List, Dict, Any, Set
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from app.rag.embedding_config import get_embeddings
from app.rag.schema_config import NETWORK_DB_SCHEMA

logger = logging.getLogger(__name__)


class FAISSRetriever:
    """FAISS-based vector store retriever for schema and join patterns."""
    
    def __init__(self):
        """Initialize FAISS retriever."""
        self.vector_store = None
        self.retriever = None
        self.documents_built = False
    
    def build_vector_store(self) -> bool:
        """
        Build FAISS vector store from schema, joins, and examples.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Building FAISS vector store from schema...")
            documents = self._prepare_documents()
            
            if not documents:
                logger.error("No documents prepared for vector store")
                return False
            
            logger.info(f"Creating vector store with {len(documents)} documents...")
            embeddings = get_embeddings()
            
            # Build FAISS index
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=embeddings
            )
            
            # Create retriever with top-k search
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 5}  # Retrieve top 5 relevant documents
            )
            
            self.documents_built = True
            logger.info("FAISS vector store built successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build FAISS vector store: {e}")
            return False
    
    def _prepare_documents(self) -> List[Document]:
        """
        Prepare documents from schema for vector store.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        # ===== Layer 1: Table Schemas =====
        logger.debug("Preparing table schema documents...")
        for table_name, table_info in NETWORK_DB_SCHEMA["tables"].items():
            columns_str = ", ".join([
                f"{col['name']} ({col['type']}): {col.get('description', '')}"
                for col in table_info["columns"]
            ])
            
            foreign_keys_str = ""
            if table_info.get("foreign_keys"):
                fk_list = [f"{k} → {v}" for k, v in table_info["foreign_keys"].items()]
                foreign_keys_str = f"\nForeign Keys: {', '.join(fk_list)}"
            
            schema_content = f"""
            Table Name: {table_name}
            Description: {table_info['description']}
            Primary Key: {table_info['primary_key']}
            {foreign_keys_str}

            Columns:
            {columns_str}
            """
            
            schema_doc = Document(
                page_content=schema_content,
                metadata={
                    "type": "table_schema",
                    "table_name": table_name,
                    "layer": 1,
                    "priority": "high"
                }
            )
            documents.append(schema_doc)
        
        # ===== Layer 2: Join Patterns =====
        logger.debug("Preparing join pattern documents...")
        for join_pattern in NETWORK_DB_SCHEMA["common_joins"]:
            join_content = f"""
            Join Pattern: {join_pattern['name']}
            Tables: {' → '.join(join_pattern['tables'])}
            Condition: {join_pattern['condition']}
            Description: {join_pattern['description']}
            Use Cases: {', '.join(join_pattern.get('use_cases', []))}

            Example SQL:
            {join_pattern['example_sql'].strip()}
            """
            
            join_doc = Document(
                page_content=join_content,
                metadata={
                    "type": "join_pattern",
                    "tables": join_pattern['tables'],
                    "layer": 2,
                    "priority": "high"
                }
            )
            documents.append(join_doc)
        
        # ===== Layer 3: Example Queries =====
        logger.debug("Preparing example query documents...")
        for query_example in NETWORK_DB_SCHEMA["example_queries"]:
            example_content = f"""
            Query Type: {query_example['type']}
            Description: {query_example['description']}
            Complexity: {query_example['complexity']}
            Tables Used: {', '.join(query_example['tables'])}

            SQL:
            {query_example['sql'].strip()}
            """
            
            example_doc = Document(
                page_content=example_content,
                metadata={
                    "type": "example_query",
                    "tables": query_example['tables'],
                    "complexity": query_example['complexity'],
                    "layer": 3,
                    "priority": "medium"
                }
            )
            documents.append(example_doc)
        
        logger.debug(f"Prepared {len(documents)} documents for vector store")
        return documents
    
    def retrieve_context(self, user_query: str) -> Dict[str, Any]:
        """
        Retrieve relevant context for user query.
        
        Args:
            user_query: Natural language user query
            
        Returns:
            Dictionary with tables, joins, examples, and context
        """
        if not self.retriever:
            logger.error("Vector store not initialized. Call build_vector_store first.")
            return {
                "tables": set(),
                "join_patterns": [],
                "example_queries": [],
                "raw_context": "",
                "error": "Vector store not initialized"
            }
        
        try:
            logger.debug(f"Retrieving context for: {user_query[:80]}...")
            
            # Retrieve relevant documents using invoke method
            docs = self.retriever.invoke(user_query)
            
            # Organize by type
            context = {
                "tables": set(),
                "join_patterns": [],
                "example_queries": [],
                "raw_context": "",
                "retrieved_docs": len(docs)
            }
            
            for doc in docs:
                metadata = doc.metadata
                content = doc.page_content
                
                if metadata.get("type") == "table_schema":
                    table_name = metadata.get("table_name")
                    context["tables"].add(table_name)
                    logger.debug(f"  Found table: {table_name}")
                    
                elif metadata.get("type") == "join_pattern":
                    context["join_patterns"].append(content)
                    tables = metadata.get("tables", [])
                    logger.debug(f"  Found join pattern: {' → '.join(tables)}")
                    
                elif metadata.get("type") == "example_query":
                    context["example_queries"].append(content)
                    logger.debug(f"  Found example query: {metadata.get('type')}")
                
                context["raw_context"] += f"\n---\n{content}"
            
            # Convert tables set to sorted list for consistency
            context["tables"] = sorted(list(context["tables"]))
            
            logger.info(f"Retrieved context: {len(context['tables'])} tables, "
                       f"{len(context['join_patterns'])} joins, "
                       f"{len(context['example_queries'])} examples")
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {
                "tables": set(),
                "join_patterns": [],
                "example_queries": [],
                "raw_context": "",
                "error": str(e)
            }
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table schema dictionary
        """
        table_name_lower = table_name.lower()
        tables = NETWORK_DB_SCHEMA["tables"]
        
        for table, schema in tables.items():
            if table.lower() == table_name_lower:
                return schema
        
        logger.warning(f"Table not found: {table_name}")
        return {}
    
    def get_all_tables(self) -> List[str]:
        """Get list of all available tables."""
        return sorted(list(NETWORK_DB_SCHEMA["tables"].keys()))


# Global FAISS retriever instance
_faiss_retriever = None


def get_faiss_retriever() -> FAISSRetriever:
    """
    Get or create global FAISS retriever instance.
    
    Returns:
        FAISSRetriever instance
    """
    global _faiss_retriever
    if _faiss_retriever is None:
        _faiss_retriever = FAISSRetriever()
    return _faiss_retriever


def initialize_rag() -> bool:
    """
    Initialize RAG system (build FAISS vector store).
    Call this once at application startup.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Initializing RAG system...")
    retriever = get_faiss_retriever()
    
    if retriever.build_vector_store():
        logger.info("RAG system initialized successfully")
        return True
    else:
        logger.error("Failed to initialize RAG system")
        return False
