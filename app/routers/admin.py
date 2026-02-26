from fastapi import APIRouter
from app.models import Link, Click
from app.database import SessionDep
from sqlalchemy import select, delete
from app.utils import decode_shortcode
from app.schemas import LinkCreate, LinkResponse

admin_router = APIRouter(prefix="/admin")


@admin_router.get("/links")
async def all_links(db: SessionDep):
    links = await db.execute(select(Link))
    results = links.scalars().all()

    return {"links": results}


@admin_router.get("/links/{shortcode}/analytics/")
async def get_analytics(shortcode: str, db: SessionDep):
    result = await db.execute(select(Click).join(Link).where(Link.short_code == shortcode))
    analytics = result.scalars().all()

    return {"analytics": analytics}


@admin_router.delete("/links/{id}")
async def delete_link(id: int, db : SessionDep):
    await db.execute(delete(Link).where(Link.id == id))
    await db.commit()

    return {"message": "Link deleted"}

