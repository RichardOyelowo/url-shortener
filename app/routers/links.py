from app.models import Link
from fastapi import APIRouter
from sqlalchemy import select
from app.schemas import LinkCreate
from app.database import SessionDep 
from app.utils import convert_to_shortcode


router = APIRouter()

@router.get("/{shortcode}")
async def load_link(shortcode: str, db: SessionDep):
    results = await db.execute(select(Link).where(Link.short_code == shortcode))
    link = results.scalars().first()
    return {"link": link}


@router.post("/links/")
async def create_link(link: LinkCreate, db: SessionDep):
    results = await db.execute(select(Link).where(Link.original_url == link.original_url))
    existing = results.first()

    if existing:
        return {"link": existing}

    new_link = Link(original_url=link.original_url)
    db.add(new_link)
    await db.flush()

    # shortcode generation
    new_link.short_code = convert_to_shortcode(new_link.id)
    await db.commit()
    await db.refresh(new_link)

    return new_link
