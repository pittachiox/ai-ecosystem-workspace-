import asyncio
import time

class AIService:
    def __init__(self):
        self.model_name = "Qwen-3B-Local"

    async def generate_response(self, prompt: str, max_tokens: int, temperature: float) -> dict:
        start_time = time.time()
        # Rule-based / local LLM simulation
        await asyncio.sleep(0.5)
        generated_text = f"Simulated response for: {prompt}"
        execution_time_ms = (time.time() - start_time) * 1000
        tokens_used = len(generated_text.split())
        return {
            "generated_text": generated_text,
            "execution_time_ms": execution_time_ms,
            "tokens_used": tokens_used,
            "model_name": self.model_name
        }

    async def stream_response(self, prompt: str):
        # Simulated streaming
        words = f"Streaming response for {prompt}...".split()
        for word in words:
            await asyncio.sleep(0.1)
            yield f"data: {word}\n\n"
        yield "data: [DONE]\n\n"
