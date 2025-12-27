from fastapi import APIRouter
from sqlalchemy import text

from database.generic import get_db
from setting.config import get_settings

router = APIRouter(
    tags=["infor"],
    prefix="/api"
)

@router.get("/")
def hello_world():
    return "hello world !!! @@"

@router.get("/infor")
def get_infor():
    settings = get_settings()

    databases = None
    db_session = get_db()

    try:
       databases = db_session.execute(text("SELECT datname FROM pg_database;")).fetchall()
    except Exception as e:
        print(e)

    if not databases:
        try:
            databases = db_session.execute(text("SHOW DATABASES;")).fetchall()
        except Exception as e:
            print(e)

    return {
        "app_name": settings.app_name,
        "author": settings.author,
        "app_mode": settings.app_mode,
        "port": settings.port,
        "reload": settings.reload,
        "db_type": settings.db_type,
        "database_url": settings.database_url,
        "databases": str(databases)
    }