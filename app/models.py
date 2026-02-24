from .database import Base
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Link(Base):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    original_url: Mapped[str] = mapped_column("original_url")
    short_code: Mapped[str] = mapped_column("short_code", unique=True)
    click_count: Mapped[int] = mapped_column("click_count",Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", default=lambda: datetime.now(timezone.utc))
    
    clicks: Mapped[list["Click"]] = relationship(back_populates="link")

    def __repr__(self):
        return f"<Link id:{self.id}, click_count:{self.click_count}>"


class Click(Base):
    __tablename__ = "click"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    link_id: Mapped[int] = mapped_column("link_id", Integer, ForeignKey("link.id"))
    created_at: Mapped[datetime] = mapped_column("created_at", default=lambda: datetime.now(timezone.utc))
    
    link: Mapped["Link"] = relationship(back_populates="clicks")
