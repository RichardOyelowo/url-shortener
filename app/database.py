import os
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


load_dotenv()
DATABASE = os.getenv("DATABASE_URL")

class Base(DeclarativeBase):
    pass

engine = create_async_engine(DATABASE)
async_session = async_sessionmaker(engine)

async def get_db():
    async with async_session() as session:
        yield session
