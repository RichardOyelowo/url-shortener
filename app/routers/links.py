from app.schemas import LinkCreate, LinkResponse
from fastapi import APIRouter

router = APIRouter()


@router.get("/{shortcode}")
async def load_link(shortcode: str):
    pass


@router.post("/links")
async def create_link(link: LinkCreate):
    pass

