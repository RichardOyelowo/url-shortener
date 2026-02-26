from app.models import Link, Click
from sqlalchemy import select
from app.schemas import LinkCreate
from app.database import SessionDep 
from app.utils import convert_to_shortcode
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse


router = APIRouter()

@router.get("/{shortcode}")
async def load_link(shortcode: str, db: SessionDep):
    results = await db.execute(select(Link).where(Link.short_code == shortcode))
    link = results.scalars().first()
    
    if link:
        # create click object
        clicked = Click(link_id=link.id)
        db.add(clicked)
        
        # increment click count
        link.click_count += 1
        await db.commit()
        await db.refresh(link)

        return RedirectResponse(url=link.original_url, status_code=302)

    raise HTTPException(status_code=404, detail="Link not Found")


@router.post("/links/")
async def create_link(link: LinkCreate, db: SessionDep):
    results = await db.execute(select(Link).where(Link.original_url == link.original_url))
    existing = results.scalars().first()

    if existing:
        return existing

    new_link = Link(original_url=link.original_url)
    db.add(new_link)
    await db.flush()

    # shortcode generation
    new_link.short_code = convert_to_shortcode(new_link.id)
    await db.commit()
    await db.refresh(new_link)

    return new_link
