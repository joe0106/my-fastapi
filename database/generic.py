from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models.items import Item
from models.users import User
from setting.config import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    return SessionLocal()

def init_db():
    Base.metadata.create_all(bind=engine, tables=[User.__table__, Item.__table__])