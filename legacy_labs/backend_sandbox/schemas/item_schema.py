from pydantic import BaseModel

class ItemCreateRequest(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
