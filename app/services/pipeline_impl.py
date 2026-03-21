"""
Concrete implementation of pipeline service.
Implements IPipelineService for query execution.
"""
import logging
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

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=10)

VALID_INTENTS = ["network_query", "topology_query", "device_lookup", "metrics_query", "alert_query"]


class PipelineService(IPipelineService):
    """Production pipeline service implementation."""
    
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
        Execute the NLP to SQL pipeline (sync version).
        
        Steps:
        1. Load schema
        2. Detect intent
        3. Select tables
        4. Select columns
        5. Generate SQL
        6. Validate SQL
        7. Explain query
        8. Execute query
        """
        try:
            logger.info(f"Starting pipeline for question: {question}")
            
            # Load schema
            raw_schema = load_schema()
            schema = format_schema(raw_schema)
            schema_tables = set(raw_schema.keys())
            
            if not schema_tables:
                return {
                    "success": False,
                    "question": question,
                    "error": "Failed to load database schema",
                    "error_type": "SchemaLoadError"
                }
            
            # Detect intent
            intent = detect_intent(question).strip().lower()
            if not self._validate_intent(intent):
                logger.error(f"Invalid intent detected: {intent}")
                return {
                    "success": False,
                    "question": question,
                    "error": f"Invalid intent: {intent}. Valid intents: {VALID_INTENTS}",
                    "error_type": "InvalidIntent"
                }
            logger.info(f"Detected intent: {intent}")
            
            # Select tables
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
            logger.info(f"Selected tables: {tables}")
            
            # Select columns
            columns = select_columns(question, tables, schema).strip()
            if not columns:
                logger.warning("No columns selected, continuing anyway")
            logger.debug(f"Selected columns: {columns[:100]}...")
            
            # Generate SQL
            raw_sql = generate_sql(question, tables, columns, schema).strip()
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
            
            # Extract and validate SQL
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
            logger.info(f"Valid SQL extracted: {sql[:100]}...")
            
            # Explain query
            try:
                explanation = explain_query(sql).strip()
            except Exception as e:
                logger.warning(f"Failed to explain query: {e}")
                explanation = f"Query explanation failed: {str(e)}"
            
            # Execute query
            result = execute_query(sql)
            if result.get("status") != "success":
                logger.error(f"Query execution failed: {result}")
            else:
                logger.info(f"Query executed successfully, returned {result.get('count', 0)} rows")
            
            return {
                "success": True,
                "question": question,
                "intent": intent,
                "tables": tables,
                "columns": columns,
                "sql": sql,
                "explanation": explanation,
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
