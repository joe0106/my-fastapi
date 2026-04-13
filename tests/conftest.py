import json
import os
from pathlib import Path
import pytest_asyncio
import pytest
import asyncio
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport

def pytest_addoption(parser):
    parser.addoption("--prod",action="store_true", help="Run the server in production mode.")
    parser.addoption("--test",action="store_true", help="Run the server in test mode.")
    parser.addoption("--dev",action="store_true", help="Run the server in development mode.")
    parser.addoption("--sync",action="store_true", help="Run the server in Sync mode.")
    parser.addoption("--db", help="Run the server in database type.",choices=["mysql","postgresql"], default="postgresql")

@pytest_asyncio.fixture(scope="session")
#@pytest.fixture(scope="session")
async def dependencies(request):
    args = request.config

    project_root = Path(__file__).parent.parent
    
    env_file = ".env.dev"
    if args.getoption("prod"):
        env_file = ".env.prod"
    elif args.getoption("test"):
        env_file = ".env.test"
        
    env_path = project_root / "setting" / env_file
    load_dotenv(dotenv_path=env_path)

    if args.getoption("sync"):
            os.environ["RUN_MODE"] = "SYNC"
    else:
        os.environ["RUN_MODE"] = "ASYNC"

    os.environ["DB_TYPE"] = args.getoption("db")
    print("DB_TYPE",os.getenv("DB_TYPE"))

# @pytest.fixture(scope="module")
# def event_loop():
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()

@pytest_asyncio.fixture(scope="session")
async def async_client(dependencies) -> AsyncClient:
    from .app import app
    from database.generic import init_db
    await init_db()  # 在測試開始前初始化資料庫
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
         yield client
    # Teardown: 清空資料庫
    from database.generic import engine
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.execute(text('truncate table "User" CASCADE;'))

@pytest.fixture(scope="session")
def user_data():
    """讀取user_data.json"""
    data_path = data_path = Path(__file__).parent / "data" / "user_data.json"
    with open(data_path, "r", encoding="utf8") as f:
        data = json.load(f)
    return data

@pytest.fixture(scope="session")
def single_user_data():
    data_path = data_path = Path(__file__).parent / "data" / "single_user.json"
    with open(data_path, "r", encoding="utf8") as f:
        data = json.load(f)
    return data[0]