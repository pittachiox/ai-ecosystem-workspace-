from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.ai_router import ai_router

app = FastAPI(title="AI LLM Inference API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)

@app.get("/")
async def root():
    return {"message": "Welcome to AI LLM Inference API"}
