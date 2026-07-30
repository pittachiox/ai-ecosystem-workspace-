from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.item_router import router as item_router
from .core.config import settings

app = FastAPI(title="FastAPI & AI Ecosystem Skeleton API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(item_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
