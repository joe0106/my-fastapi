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

def merge_dict(d1: dict, d2: dict):
    '''
    把d2的東西合併到d1中
    '''
    for k, v in d2.items():
        d1[k] = v
    return d1

def generic_cache_update(prefix: str, key: str, update_with_page: bool = False, pagenation_key: str = None):
    rc = redis.Redis(connection_pool=CONNECTION_POOL)
    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            if not value_key:
                return await func(*args, **kwargs)
            
            sql_result = await func(*args, **kwargs)
            if not sql_result:
                return None
            
            # redis key
            cache_key = f"{prefix}:{value_key}"
            sql_dict = query_res_to_dict(sql_result)
            rc.hset(cache_key, mapping=sql_dict)

            if update_with_page:
                try:
                    page_key = f"{prefix}_page"
                    old_redis_result = rc.zrange(
                        name=page_key,
                        start=value_key,
                        end=value_key,
                        withscores=False,
                        byscore=True
                    )[0]

                    if isinstance(old_redis_result, (bytes, bytearray)):
                        old_redis_result = old_redis_result.decode('utf-8')

                    rc.zremrangebyscore(name=page_key, min=value_key, max=value_key)

                    #取出old_redis_result後，刪除cache，再把sql_dict合併到old_redis_result，然後再將pagenation_key合併到裡面(補充用)
                    rc.zadd(
                        name=page_key,
                        mapping={str(merge_dict(merge_dict(ast.literal_eval(old_redis_result), sql_dict), {pagenation_key: value_key})) : value_key},
                        nx=True
                    )
                except Exception as e:
                    print(f"redis error: {e}")
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

            try:
                page_key = f"{prefix}_page"
                rc.zremrangebyscore(name=page_key, min=value_key, max=value_key)
            except:
                pass

            return await func(*args, **kwargs)
        return wrapper
    return inner

import ast
def generic_pagenation_cache_get(prefix: str, cls: object):
    rc = redis.Redis(connection_pool=CONNECTION_POOL)
    def inner(func):
        async def wrapper(*args, **kwargs):
            if kwargs.get('keyword'):
                return await func(*args, **kwargs)
            
            last = kwargs.get('last')
            limit = kwargs.get('limit')
            right = last + limit

            #cache key的設計可能會影響redis整個資料庫的大小
            cache_key = f"{prefix}_page"
            #cache_key = f"{prefix}_page:last={last}:limit={limit}"

            try:
                redis_result: list = rc.zrange(name=cache_key, start=last, end=right, withscores=False, byscore=False)

                data = []
                if len(redis_result) > 0:
                    for row_str in redis_result:
                        if isinstance(row_str, (bytes, bytearray)):
                            row_str = row_str.decode("utf-8")
                        row_dict = ast.literal_eval(row_str)
                        data.append(cls(**row_dict))
                    return data
            except Exception as e:
                print(f'redis error: {e}')
                pass
            
            #如果沒有cache的話，回歸原本的sql查詢，並且cache結果
            sql_result = await func(*args, **kwargs)
            if not sql_result:
                return sql_result
            
            for row in sql_result:
                try:
                    rc.zadd(name=cache_key, mapping={ str(row._asdict()) : row.id })
                except Exception as e:
                    print(e)
            return sql_result

        return wrapper
    return inner