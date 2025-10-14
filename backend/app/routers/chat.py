from fastapi import APIRouter, HTTPException
from ..models import ChatRequest, ParsedStrategy
from ..services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/parse", response_model=ParsedStrategy)
async def parse_strategy(request: ChatRequest):
    """
    Parse natural language trading strategy description into structured format
    """
    try:
        result = await chat_service.parse_strategy(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
