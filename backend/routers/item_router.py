from fastapi import APIRouter, Depends
from ..schemas.item_schema import ItemCreateRequest, ItemResponse
from ..dependencies.database import get_db

router = APIRouter(prefix="/api/v1/items", tags=["Items Management"])

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreateRequest, db=Depends(get_db)):
    return {"id": 1, **item.model_dump()}

@router.get("/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db=Depends(get_db)):
    return {"id": item_id, "name": "Fake Item", "price": 0.0}
