# 參考來源
此專案參考自zhu424 (jason810496)
大大的鐵人賽[文章](https://ithelp.ithome.com.tw/users/20148985/ironman/6772)

# How to run

```bash
uv run python3 run.py
# dbtype
uv run python3 run.py --db postgress
# run mode
uv run python3 run.py --sync
```

# Container

資料庫使用PostgresSQL及MySQL兩個DB，於`uv run python3 run.py --db postgress`時可指定（預設為PostgresSQL）。

## PostgresSQL 容器啟用指令

```bash
docker run --name fastapi_postgres_dev -e POSTGRES_USER=fastapi_tutorial -e POSTGRES_PASSWORD=fastapi_tutorial_password -e POSTGRES_DB=fastapi_tutorial -p 5432:5432 --volume fastapi_tutorial_postgres_dev:/var/lib/postgresql/data -d postgres:15.1 
```

### 容器指令
```bash
# enter container
docker exec -it {container_id} psql -U fastapi_tutorial
# describe db opject
\d "User"
# list all tables
\dt
# quit
\q
# help
\?
#case sensitive
select * from "User"; 
#顯示使用者
select * from User;
```

## MySQL 容器啟用指令

```bash
docker run --name fastapi_mysql_dev -e MYSQL_USER=fastapi_tutorial -e MYSQL_ROOT_PASSWORD=fastapi_tutorial_password -e MYSQL_DATABASE=fastapi_tutorial -p 3306:3306 --volume fastapi_tutorial_mysql_dev:/var/lib/mysql -d mysql:8.1
```

# Database Operation Run Mode

```bash
uv run python3 main.py --sync
```

# Pytest testing framework

```bash
#cd into /tests folder
cd tests
#py test指向測試.py的目錄
uv run pytest tests/
```

- 特定mark測試使用mark屬性

```py
@pytest.mark.my_mark
def test_redis():
```

```bash
uv run pytest -m my_mark
```

- 跑測試時，需要三種資料庫的容器運行

# Docker build

```bash
docker build . -t my-fastapi
docker image ls
```

# Docker compose

```bash
docker compose up
docker compose ps
docker compose ls
```

# Redis Server

```bash
#redis image本身沒有支援find功能
docker run --name fastapi_redis_dev -p 6379:6379 -d redis --requirepass "fastapi_redis_password"
#使用redis-stack image除redis本體外，包含更多功能
docker run --name fastapi_redis_dev -p 6379:6379 -d redis/redis-stack:latest
```

# Docker compose - Primary-Replica mode

```bash
#use yaml file
docker compose -f docker-compose-primary-replica.yml up -d
docker compose -f docker-compose-primary-replica.yml down [service-name]
docker compose -f docker-compose-primary-replica.yml restart [service-name]
#check docker log when container is in detatch mode
docker logs primary -f
#進入容器的bash並執行命令
docker exec -it primary bash -c "psql -U [user] -d [database]"
```
