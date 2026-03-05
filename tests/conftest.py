import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.utils import verify_header
from app.database import Base, get_session

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(DATABASE_URL)
test_session = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def db_setup():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_setup):
    # passes as get_session
    async def get_test_session():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session


    # passes as verify header for admin routes
    async def bypass_header():
        return

    app.dependency_overrides[verify_header] = bypass_header
    

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
