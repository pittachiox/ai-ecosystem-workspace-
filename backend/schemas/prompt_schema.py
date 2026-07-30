from pydantic import BaseModel
from typing import Optional

class PromptGenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    stream: bool = False

class PromptGenerateResponse(BaseModel):
    generated_text: str
    execution_time_ms: float
    tokens_used: int
    model_name: str
