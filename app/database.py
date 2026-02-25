import os
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


load_dotenv()

class Base(DeclarativeBase):
    pass

engine = create_async_engine(os.getenv("DATABASE_URL"))
async_session = async_sessionmaker(engine)

async def get_session():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
