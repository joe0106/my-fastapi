from backend.setting.config import get_settings
from backend.database.generic import crud_class_decorator as generic_crud_class_decorator
from functools import lru_cache

settings = get_settings()

@lru_cache
def crud_class_decorator(cls):
    if settings.app_mode == 'primary_replica':
        from .primary_replica import crud_class_decorator as primary_replica_crud_class_decorator
        return primary_replica_crud_class_decorator(cls)
    return generic_crud_class_decorator(cls)

async def init_db():
    if settings.app_mode == 'primary_replica':
        from .primary_replica import init_db as primary_replica_init_db
        await primary_replica_init_db()
    from backend.database.generic import init_db as generic_init_db
    await generic_init_db()

async def close_db():
    if settings.app_mode == 'primary_replica':
        from .primary_replica import close_db as primary_replica_close_db
        await primary_replica_close_db()
    from backend.database.generic import close_db as generic_close_db
    await generic_close_db()