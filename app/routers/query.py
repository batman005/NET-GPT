import json
from typing import AsyncIterator, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from app.services.interfaces import IPipelineService
from app.dependencies import get_pipeline_service
from app.schemas import QueryRequest, BatchQueryRequest, QueryResponse
from app.utils.logger import get_logger

logger = get_logger(__name__, component="query")
router = APIRouter()


async def _sse_events(
    pipeline: IPipelineService,
    question: str,
    user_id: str,
) -> AsyncIterator[str]:
    """Format pipeline stream events as Server-Sent Events."""
    async for event in pipeline.execute_stream(question, user_id=user_id):
        event_name = event.get("stage", "message")
        payload = json.dumps(event, default=str)
        yield f"event: {event_name}\ndata: {payload}\n\n"


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    x_user_id: Optional[str] = Header(default="anonymous"),
    pipeline: IPipelineService = Depends(get_pipeline_service)
) -> Dict[str, Any]:
    """
    Ask a question, get SQL query and results.
    
    Header: X-User-ID=john (optional, for tracking)
    
    Dependency Injection: pipeline service is automatically provided by FastAPI
    """
    logger.info(f"Query from {x_user_id}: {request.question}")
    
    try:
        result = await pipeline.execute(request.question, user_id=x_user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Query failed")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/batch")
async def batch_query(
    request: BatchQueryRequest,
    x_user_id: Optional[str] = Header(default="anonymous"),
    pipeline: IPipelineService = Depends(get_pipeline_service)
) -> Dict[str, Any]:
    """
    Run multiple queries at the same time (concurrent).
    Much faster than running them one-by-one.
    
    Dependency Injection: pipeline service is automatically provided by FastAPI
    """
    logger.info(f"Batch query from {x_user_id}: {len(request.questions)} questions")
    
    try:
        results = await pipeline.execute_batch(request.questions, user_id=x_user_id)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def stream_query_post(
    request: QueryRequest,
    x_user_id: Optional[str] = Header(default="anonymous"),
    pipeline: IPipelineService = Depends(get_pipeline_service)
) -> StreamingResponse:
    """
    Stream query progress with Server-Sent Events over POST.

    Use this endpoint from frontend fetch() when you need JSON request bodies.
    """
    logger.info(f"SSE POST query from {x_user_id}: {request.question}")
    return StreamingResponse(
        _sse_events(pipeline, request.question, x_user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
