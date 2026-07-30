from fastapi import FastAPI
from .routers.item_router import router as item_router
from .core.config import settings

app = FastAPI(title="FastAPI & AI Ecosystem Skeleton API", version="1.0.0")

app.include_router(item_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
