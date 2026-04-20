from random import random
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.setting.config import get_primary_replica_settings
from backend.models.base import Base

settings = get_primary_replica_settings()

primary_engine = create_async_engine(
    settings.primary_database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=8,
    max_overflow=0
)

replica_engine = create_async_engine(
    settings.replica_database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=8,
    max_overflow=0
)

#create session
primarySession = async_sessionmaker(primary_engine, expire_on_commit=False, autocommit=False)
replicaSession = async_sessionmaker(replica_engine, expire_on_commit=False, autocommit=False)

readSessions = [primarySession, replicaSession]

@asynccontextmanager
async def get_write_db():
    async with primarySession() as db:
        async with db.begin():
            yield db

@asynccontextmanager
async def get_read_db():
    session = random.choice(readSessions)
    async with session() as db:
        async with db.begin():
            yield db

async def init_db():
    async with primary_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # async with primary_engine as conn:
    #     await conn.run_sync(Base.metadata.create_all)

async def close_db():
    # async with primary_engine.begin() as conn:
    #     await conn.close()
    # async with replica_engine.begin() as conn:
    #     await conn.close()
    async with primarySession.begin() as conn:
        await conn.close()
    async with replicaSession.begin() as conn:
        await conn.close()

def db_session_decorator(func):
    async def wrapper(*args, **kwargs):
        if "get" in func.__name__:
            async with get_read_db() as db_session:
                kwargs["db_session"] = db_session
                result = await func(*args, **kwargs)
                return result
        async with get_write_db as db_session:
            kwargs["db_session"] = db_session
            result = await func(*args, **kwargs)
            return result
    return wrapper

def crud_class_decorator(cls):
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, db_session_decorator(method))
    return cls