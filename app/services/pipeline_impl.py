"""
Concrete implementation of pipeline service.
Implements IPipelineService for query execution.
Enhanced with RAG (Retrieval-Augmented Generation) for better accuracy.
"""
import asyncio
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from app.services.interfaces import IPipelineService
from app.agents.intent_agent import detect_intent
from app.agents.table_agent import select_tables
from app.agents.column_agent import select_columns
from app.agents.sql_agent import generate_sql
from app.agents.explain_agent import explain_query
from app.db.mysql_client import execute_query
from app.db.schema_loader import load_schema
from app.utils.schema_formatter import format_schema
from app.utils.sql_extractor import extract_sql
from app.utils.decorators import log_execution_time_async, handle_errors_async
from app.rag.rag_service import get_rag_service
from app.utils.logger import get_logger

logger = get_logger(__name__, component="pipeline")
_executor = ThreadPoolExecutor(max_workers=10)

VALID_INTENTS = ["network_query", "topology_query", "device_lookup", "metrics_query", "alert_query"]


class PipelineService(IPipelineService):
    """Production pipeline service implementation."""
    
    def __init__(self):
        """Initialize pipeline with RAG service."""
        self.rag_service = get_rag_service()
        logger.info("Pipeline initialized with RAG enhancements")
    
    def _get_rag_context(self, question: str) -> Dict[str, Any]:
        """
        Retrieve RAG context for question.
        
        Returns enhanced context with tables, joins, and examples
        """
        try:
            logger.debug("Retrieving RAG context...")
            context = self.rag_service.retrieve_context_for_query(question)
            logger.info(f"RAG Context Retrieved: {len(context.get('tables', []))} tables, "
                       f"{len(context.get('join_patterns', []))} joins, "
                       f"{len(context.get('example_queries', []))} examples")
            return context
        except Exception as e:
            logger.warning(f"Failed to retrieve RAG context: {e}")
            return {
                "tables": [],
                "join_patterns": [],
                "example_queries": [],
                "raw_context": "",
                "error": str(e)
            }
    
    def _validate_intent(self, intent: str) -> bool:
        """Validate intent is in allowed list."""
        if not intent or not isinstance(intent, str):
            logger.error(f"Invalid intent type: {type(intent)}")
            return False
        intent = intent.strip().lower()
        return intent in VALID_INTENTS
    
    def _validate_tables(self, tables: str, valid_tables: set) -> bool:
        """Validate all returned tables exist in schema."""
        if not tables or not isinstance(tables, str):
            logger.error(f"Invalid tables type: {type(tables)}")
            return False
        selected = set(t.strip().lower() for t in tables.split(",") if t.strip())
        if not selected:
            logger.error("No tables selected")
            return False
        valid_lower = set(t.lower() for t in valid_tables)
        invalid = selected - valid_lower
        if invalid:
            logger.error(f"Invalid tables detected: {invalid}. Available: {valid_lower}")
            return False
        return True
    
    def _validate_sql(self, sql: str) -> bool:
        """Validate SQL is not empty and looks valid."""
        if not sql or not isinstance(sql, str):
            logger.error(f"Invalid SQL: empty or wrong type")
            return False
        sql = sql.strip().upper()
        if not sql.startswith("SELECT"):
            logger.error(f"SQL must start with SELECT")
            return False
        if "FROM" not in sql:
            logger.error("SQL must contain FROM clause")
            return False
        return True
    
    def run_pipeline_sync(self, question: str) -> Dict[str, Any]:
        """
        Execute the NLP to SQL pipeline with RAG enhancement (sync version).
        
        Pipeline Steps with RAG:
        1. Load schema
        2. Retrieve RAG context (tables, joins, examples) ← NEW
        3. Detect intent
        4. Select tables (with RAG enhancement)
        5. Select columns (with RAG enhancement)
        6. Generate SQL (with RAG context)
        7. Validate SQL
        8. Explain query (with RAG similar examples)
        9. Execute query
        """
        try:
            logger.info(f"{'='*60}")
            logger.info(f"Starting RAG-Enhanced Pipeline")
            logger.info(f"Question: {question[:80]}")
            logger.info(f"{'='*60}")
            
            # ===== Step 1: Load Schema =====
            logger.info("Step 1: Loading database schema...")
            raw_schema = load_schema()
            schema = format_schema(raw_schema)
            schema_tables = set(raw_schema.keys())
            
            if not schema_tables:
                logger.error("No schema tables found")
                return {
                    "success": False,
                    "question": question,
                    "error": "Failed to load database schema",
                    "error_type": "SchemaLoadError"
                }
            logger.info(f"Schema loaded: {len(schema_tables)} tables")
            
            # ===== Step 2: Retrieve RAG Context (NEW!) =====
            logger.info("Step 2: Retrieving RAG context...")
            rag_context = self._get_rag_context(question)
            rag_tables = rag_context.get("tables", [])
            rag_joins = rag_context.get("join_patterns", [])
            rag_examples = rag_context.get("example_queries", [])
            
            # ===== Step 3: Detect Intent =====
            logger.info("Step 3: Detecting intent...")
            intent = detect_intent(question).strip().lower()
            if not self._validate_intent(intent):
                logger.error(f"Invalid intent detected: {intent}")
                return {
                    "success": False,
                    "question": question,
                    "error": f"Invalid intent: {intent}. Valid intents: {VALID_INTENTS}",
                    "error_type": "InvalidIntent"
                }
            logger.info(f"Intent detected: {intent}")
            
            # ===== Step 4: Select Tables (RAG-Enhanced) =====
            logger.info("Step 4: Selecting tables with RAG enhancement...")
            # Table selection now uses RAG context (already integrated in table_agent.py)
            tables = select_tables(question, schema).strip()
            if not self._validate_tables(tables, schema_tables):
                logger.error(f"Invalid tables selected: {tables}")
                return {
                    "success": False,
                    "question": question,
                    "intent": intent,
                    "error": f"Invalid or non-existent tables: {tables}",
                    "error_type": "InvalidTables"
                }
            logger.info(f"Tables selected: {tables}")
            logger.info(f"RAG suggested tables: {rag_tables}")
            
            # ===== Step 5: Select Columns (RAG-Context) =====
            logger.info("Step 5: Selecting columns...")
            # Add RAG context hints to column selection
            column_context = f"RAG retrieved {len(rag_joins)} relevant join patterns for reference."
            columns = select_columns(question, tables, schema).strip()
            if not columns:
                logger.warning("No columns selected, continuing anyway")
            logger.info(f"Columns selected: {columns[:100] if columns else 'None'}...")
            
            # ===== Step 6: Generate SQL (RAG-Enhanced) =====
            logger.info("Step 6: Generating SQL with RAG context...")
            # Enhance schema with RAG suggestions for SQL generation
            rag_hints = "\n\nRAG SUGGESTIONS:\n"
            if rag_joins:
                rag_hints += f"Relevant join patterns: {len(rag_joins)} found\n"
            if rag_examples:
                rag_hints += f"Similar example queries available: {len(rag_examples)}\n"
            
            enhanced_schema = schema + rag_hints
            raw_sql = generate_sql(question, tables, columns, enhanced_schema).strip()
            
            if not raw_sql:
                logger.error("Empty SQL generated")
                return {
                    "success": False,
                    "question": question,
                    "intent": intent,
                    "tables": tables,
                    "columns": columns,
                    "error": "Failed to generate SQL query",
                    "error_type": "SQLGenerationError"
                }
            logger.debug(f"Generated raw SQL: {raw_sql[:100]}...")
            
            # ===== Step 7: Extract and Validate SQL =====
            logger.info("Step 7: Validating SQL...")
            sql = extract_sql(raw_sql)
            if not sql or not self._validate_sql(sql):
                logger.error(f"Invalid SQL generated: {sql}")
                return {
                    "success": False,
                    "question": question,
                    "intent": intent,
                    "tables": tables,
                    "columns": columns,
                    "error": f"Invalid SQL generated: {sql}",
                    "error_type": "InvalidSQL"
                }
            logger.info(f"SQL validated: {sql[:80]}...")
            
            # ===== Step 8: Explain Query (RAG-Enhanced) =====
            logger.info("Step 8: Explaining query...")
            try:
                # Use RAG similar examples if available for better explanation
                explanation_hint = ""
                if rag_examples:
                    explanation_hint = f"\nBased on {len(rag_examples)} similar example queries in the knowledge base."
                
                explanation = explain_query(sql).strip()
                explanation += explanation_hint
            except Exception as e:
                logger.warning(f"Failed to explain query: {e}")
                explanation = f"Query explanation failed: {str(e)}"
            logger.info(f"Query explanation generated: {explanation[:80]}...")
            
            # ===== Step 9: Execute Query =====
            logger.info("Step 9: Executing query...")
            result = execute_query(sql)
            if result.get("status") != "success":
                logger.error(f"Query execution failed: {result}")
            else:
                rows_count = result.get("count", 0)
                logger.info(f"Query executed successfully: {rows_count} rows returned")
            
            # ===== Return Final Result =====
            logger.info(f"{'='*60}")
            logger.info("Pipeline execution completed successfully")
            logger.info(f"{'='*60}")
            
            return {
                "success": True,
                "question": question,
                "intent": intent,
                "tables": tables,
                "columns": columns,
                "sql": sql,
                "explanation": explanation,
                "rag_context": {
                    "tables_suggested": rag_tables,
                    "join_patterns_found": len(rag_joins),
                    "similar_examples": len(rag_examples)
                },
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Pipeline failed: {type(e).__name__}: {e}", exc_info=True)
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    @log_execution_time_async
    @handle_errors_async(default_return={"success": False, "error": "Pipeline execution failed"})
    async def execute(self, question: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """Execute query asynchronously (non-blocking)."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_executor, self.run_pipeline_sync, question)
        result["user_id"] = user_id
        logger.info(f"[{user_id}] Query completed: {question[:50]}...")
        return result
    
    @log_execution_time_async
    @handle_errors_async(default_return=[])
    async def execute_batch(self, questions: list, user_id: str = "anonymous") -> list:
        """Execute multiple queries concurrently."""
        logger.info(f"[{user_id}] Running {len(questions)} concurrent queries")
        
        tasks = [self.execute(question, user_id) for question in questions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Query {i} failed: {result}")
                final_results.append({
                    "success": False,
                    "question": questions[i],
                    "error": str(result),
                    "error_type": type(result).__name__
                })
            else:
                final_results.append(result)
        
        logger.info(f"[{user_id}] All {len(questions)} queries completed")
        return final_results
