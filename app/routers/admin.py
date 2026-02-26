from os import link
from app.models import Link, Click
from sqlalchemy import select, delete
from app.database import SessionDep
from fastapi import APIRouter

admin_router = APIRouter()


@admin_router.get("/admins/links/")
async def links(db: SessionDep):
    results = await db.execute(select(Link))
    links = results.scalars().all()

    return {"links": links}


@admin_router.get("/admins/links/{shortcode}/analytics")
async def analytics(shortcode: str, db: SessionDep):
    results = await db.execute(select(Click).join(Click.link).where(Link.short_code == shortcode))
    analytics = results.scalars().all()

    return {"analytics": analytics}


@admin_router.delete("/admins/links/{id}")
async def delete_link(id: int, db: SessionDep):
    result = await db.execute(delete(Link).where(Link.id == id))
    await db.commit()
    
    return {"message":"link deleted"}
