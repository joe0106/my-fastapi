import redis

REDIS_URL = "redis://localhost:6379"

CONNECTION_POOL = redis.ConnectionPool.from_url(REDIS_URL)

def check_has_all_key(result: dict, cls: object):
    '''
    check if result has all the fields in cls object
    '''
    result_keys = result.keys()
    for key in cls.__annotations__.keys():
        if key not in result_keys:
            return False
    return True

def query_res_to_dict(result):
    '''
    parse sql query result into dictionary and do other field parsing
    '''
    result = dict(result)
    if result.get("birthday"):
        result["birthday"] = result["birthday"].strftime("%Y-%m-%d")
    
    return result

def generic_cache_get(prefix: str, key: str, cls: object):
    '''
    prefix: namspace for redis key ( such as `user` 、`item` 、`article` )
    key: **parameter name** in caller function ( such as `user_id` 、`email` 、`item_id` )
    cls: **response schema** in caller function ( such as `UserSchema.UserRead` 、`UserSchema.UserId` 、`ItemSchema.ItemRead` )
    '''
    rc = redis.Redis(connection_pool=CONNECTION_POOL)

    def inner(func):
        async def wrapper(*args, **kwargs):
            #未使用關鍵字參數就無法查詢cache，故呼叫原方法
            value_key = kwargs.get(key)
            if not value_key:
                return await func(*args, **kwargs)
            
            #redis key
            cache_key = f"{prefix}:{value_key}"

            #try get redis kv
            try:
                redis_result = rc.hgetall(cache_key)
                #檢核所有欄位都要包含在類別(cls)欄位中，才能算是cache hit
                if check_has_all_key(redis_result, cls):
                    return cls(**redis_result)
            except:
                pass

            #if cache doesnt hit, do sql query
            sql_result = await func(*args, **kwargs)
            if not sql_result:
                return None
            
            #cache query result
            rc.hset(cache_key, mapping=query_res_to_dict(sql_result))

            #return query result
            return sql_result

        return wrapper
    return inner

def generic_cache_update(prefix: str, key: str):
    rc = redis.Redis(connection_pool=CONNECTION_POOL)
    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            if not value_key:
                return await func(*args, **kwargs)
            # redis key
            cache_key = f"{prefix}:{value_key}"
            try:
                sql_result = await func(*args, **kwargs)
                rc.hset(cache_key, mapping=query_res_to_dict(sql_result))
            except:
                pass
            return sql_result
        return wrapper
    return inner

def generic_cache_delete(prefix: str, key: str):
    rc = redis.Redis(connection_pool=CONNECTION_POOL)
    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            if not value_key:
                return await func(*args, **kwargs)
            # redis key
            cache_key = f"{prefix}:{value_key}"
            try:
                rc.delete(cache_key)
            except:
                pass
            return await func(*args, **kwargs)
        return wrapper
    return inner