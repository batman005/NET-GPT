"""
Pydantic schemas for query-related requests and responses.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Single query request."""
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Question about network data"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show devices with temperature warnings"
            }
        }


class BatchQueryRequest(BaseModel):
    """Multiple queries request."""
    questions: list[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of questions to process concurrently"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    "Show devices with temperature warnings",
                    "List interfaces that are down",
                    "What BGP neighbors do we have?"
                ]
            }
        }


class QueryResponse(BaseModel):
    """Query result."""
    success: bool = Field(
        ...,
        description="Whether query execution was successful"
    )
    question: str = Field(
        ...,
        description="The original question"
    )
    intent: str = Field(
        None,
        description="Detected intent (network_query, topology_query, etc.)"
    )
    tables: str = Field(
        None,
        description="Selected database tables"
    )
    columns: str = Field(
        None,
        description="Selected columns from tables"
    )
    sql: str = Field(
        None,
        description="Generated SQL query"
    )
    explanation: str = Field(
        None,
        description="Plain English explanation of the SQL query"
    )
    result: Dict[str, Any] = Field(
        None,
        description="Query execution result with data and count"
    )
    error: str = Field(
        None,
        description="Error message if execution failed"
    )
    request_id: str = Field(
        None,
        description="Unique request identifier for tracking"
    )
    user_id: str = Field(
        None,
        description="User identifier from X-User-ID header"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "question": "Show devices with temperature warnings",
                "intent": "metrics_query",
                "tables": "devices, device_health",
                "sql": "SELECT * FROM devices JOIN device_health WHERE temperature > 70",
                "explanation": "This query finds all devices with high temperature readings",
                "result": {
                    "status": "success",
                    "data": [
                        {"device_id": 1, "hostname": "router-1", "temperature": 75}
                    ],
                    "count": 1
                },
                "error": None,
                "user_id": "john"
            }
        }


class BatchQueryResponse(BaseModel):
    """Batch query result."""
    success: bool = Field(
        ...,
        description="Whether batch execution was successful"
    )
    total: int = Field(
        ...,
        description="Total number of queries"
    )
    successful: int = Field(
        ...,
        description="Number of successful queries"
    )
    results: list[QueryResponse] = Field(
        ...,
        description="Results for each query"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total": 3,
                "successful": 3,
                "results": [
                    {
                        "success": True,
                        "question": "Query 1",
                        "sql": "SELECT ...",
                        "result": {"status": "success", "count": 5}
                    },
                    {
                        "success": True,
                        "question": "Query 2",
                        "sql": "SELECT ...",
                        "result": {"status": "success", "count": 3}
                    },
                    {
                        "success": True,
                        "question": "Query 3",
                        "sql": "SELECT ...",
                        "result": {"status": "success", "count": 10}
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str = Field(
        ...,
        description="Error message"
    )
    error_type: str = Field(
        None,
        description="Type of error (e.g., InvalidIntent, SchemaLoadError)"
    )
    request_id: str = Field(
        None,
        description="Unique request identifier for tracking"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid tables detected: invalid_table",
                "error_type": "InvalidTables",
                "request_id": "abc12345"
            }
        }
