from fastapi import APIRouter
from sqlalchemy import text

from database.generic import get_db
from models.items import Item
from models.users import User
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

@router.get("/test/create", response_description="測試資料庫寫入User: 'test0', Item: 'item0'")
def test():
    '''
    測試資料庫寫入
    '''
    db_session = get_db()
    result = {
        "user": None,
        "item": None
    }
    try:
        test_user = User("123456", "test0", 0, None, "2000-01-01", "123@email.com")
        db_session.add(test_user)
        db_session.commit()
        result["user"] = str(test_user)

        test_item = Item("item0",99.9, "brand0", "test0", test_user.id)
        db_session.add(test_item)
        db_session.commit()
        result["item"] = str(test_item)
        
    except Exception as e:
        print(e)

    return result

@router.get("/test/read", response_description="測試資料庫寫入User: 'test0', Item: 'item0'")
def test_read():
    '''
    測試資料庫讀取
    '''
    db_session = get_db()
    result = {
        "user": None,
        "item": None,
        "user.items": None
    }
    try:
        test_user = db_session.query(User).filter(User.name == "test0").first()
        test_item = db_session.query(Item).filter(Item.brand == "brand0").first()
        result["user"] = test_user
        result["item"] = test_item
        result["user.items"] = test_user.items

    except Exception as e:
        print(e)

    return result