import os
import tempfile
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.base import Base
from app.db.session import get_db

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
async def db_session():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    test_db_url = f"sqlite+aiosqlite:///{path}"

    engine = create_async_engine(test_db_url, echo=False, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with SessionLocal() as session:
            yield session
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
        try:
            os.remove(path)
        except OSError:
            pass

@pytest.fixture()
async def client(db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
