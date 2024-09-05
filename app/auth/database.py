from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy import text, create_engine, String
from app.auth.config import settings
from typing import Annotated
import asyncio

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True
)

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True
)

session_factory = sessionmaker(sync_engine)
async_session_factory = sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass