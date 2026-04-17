from fastapi import FastAPI

from backend.setting.config import get_settings

settings = get_settings()

app = FastAPI()

if settings.run_mode == "ASYNC":
    from backend.api.infor import router as infor_router
    from backend.api.users import router as user_router
    from backend.api.items import router as item_router
    from backend.api.auth import router as auth_router
    from backend.database.primary_replica import init_db , close_db

    app.include_router(infor_router)
    app.include_router(user_router)
    app.include_router(item_router)
    app.include_router(auth_router)

    @app.on_event("startup")
    async def startup():
        await init_db()

    @app.on_event("shutdown")
    async def shutdown():
        await close_db()

else:
    from backend.sync.api.infor import router as infor_router
    from backend.sync.api.users import router as user_router
    from backend.sync.api.items import router as item_router
    from backend.sync.database.generic import init_db , close_db

    app.include_router(infor_router)
    app.include_router(user_router)
    app.include_router(item_router)
    

    @app.on_event("startup")
    def startup():
        init_db()

    @app.on_event("shutdown")
    def shutdown():
        close_db()