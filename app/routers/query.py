from fastapi import APIRouter
from app.services.pipeline import run_pipeline

router = APIRouter()


@router.post("/query")
def query(question: str):

    result = run_pipeline(question)
    
    return result