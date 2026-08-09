from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from schemas.prompt_schema import PromptGenerateRequest, PromptGenerateResponse
from services.ai_service import AIService
from dependencies.auth import get_current_user

ai_router = APIRouter(prefix="/api/v1/ai", tags=["AI Engine"])
ai_service = AIService()

@ai_router.post("/generate", response_model=PromptGenerateResponse)
async def generate(request: PromptGenerateRequest, user=Depends(get_current_user)):
    result = await ai_service.generate_response(
        prompt=request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    return PromptGenerateResponse(**result)

@ai_router.get("/stream")
async def stream(prompt: str, user=Depends(get_current_user)):
    return StreamingResponse(
        ai_service.stream_response(prompt), 
        media_type="text/event-stream"
    )
