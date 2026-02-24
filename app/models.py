from .database import Base
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    username: Mapped[str] = mapped_column("name", String(50))
    email: Mapped[str] = mapped_column("email",String, unique=True)
    hashed_password: Mapped[str] = mapped_column("hashed_password", String)
    is_active: Mapped[bool] = mapped_column("is_active", default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", default=lambda: datetime.now(timezone.utc))
    links: Mapped[list["Link"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User id:{self.id}, username:{self.username}>"


class Link(Base):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    original_url: Mapped[str] = mapped_column("original_url")
    short_code: Mapped[str] = mapped_column("short_code", unique=True)
    click_count: Mapped[int] = mapped_column("click_count",Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", default=lambda: datetime.now(timezone.utc))
    user: Mapped["User"] = relationship(back_populates="links")

    def __repr__(self):
        return f"<Link id:{self.id}, click_count:{self.click_count}>"


class Click(Base):
    __tablename__ = "click"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    link_id: Mapped[int] = mapped_column("link_id", Integer, ForeignKey("link.id"))
    created_at: Mapped[datetime] = mapped_column("created_at", default=lambda: datetime.now(timezone.utc))

