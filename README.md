# 參考來源
此專案參考自zhu424 (jason810496)
大大的鐵人賽[文章](https://ithelp.ithome.com.tw/users/20148985/ironman/6772)

# How to run

```bash
uv run python3 main.py
```

# Container

資料庫使用PostgresSQL及MySQL兩個DB，於`uv run python3 main.py --db postgress`時可指定（預設為PostgresSQL）。

## PostgresSQL 容器啟用指令

```bash
docker run --name fastapi_postgres_dev -e POSTGRES_USER=fastapi_tutorial -e POSTGRES_PASSWORD=fastapi_tutorial_password -e POSTGRES_DB=fastapi_tutorial -p 5432:5432 --volume fastapi_tutorial_postgres_dev:/var/lib/postgresql/data -d postgres:15.1 
```

## MySQL 容器啟用指令

```bash
docker run --name fastapi_mysql_dev -e MYSQL_USER=fastapi_tutorial -e MYSQL_ROOT_PASSWORD=fastapi_tutorial_password -e MYSQL_DATABASE=fastapi_tutorial -p 3306:3306 --volume fastapi_tutorial_mysql_dev:/var/lib/mysql -d mysql:8.1
```