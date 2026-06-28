import os
from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/pagination_demo",
)

engine: AsyncEngine | None = None
async_session: sessionmaker | None = None


def get_engine() -> AsyncEngine:
    global engine
    if engine is None:
        engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    return engine


def get_session() -> sessionmaker:
    global async_session
    if async_session is None:
        async_session = sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return async_session


async def init_models() -> None:
    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
