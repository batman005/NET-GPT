import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from app.services.interfaces import IPipelineService
from app.dependencies import get_pipeline_service
from app.schemas import QueryRequest, BatchQueryRequest, QueryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


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
