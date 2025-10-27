from fastapi import APIRouter, HTTPException
from typing import List

from ..models import ResearchRequest, ResearchResult
from ..services.research_service import research_service

router = APIRouter(prefix="/research", tags=["research"])

@router.post("", response_model=ResearchResult)
async def run_research(request: ResearchRequest) -> ResearchResult:
    try:
        return await research_service.research(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
