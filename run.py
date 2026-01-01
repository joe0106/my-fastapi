import os
import argparse
import uvicorn

from dotenv import load_dotenv

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "run the server in different modes")
    parser.add_argument("--prod", action = "store_true", help = "Run the server in production mode")
    parser.add_argument("--test", action = "store_true", help = "Run the server in test mode")
    parser.add_argument("--dev",  action = "store_true", help = "Run the server in development mode")

    # 新增 db_type
    db_type =  parser.add_argument_group(title="Database Type", description="Run the server in different database type.")
    db_type.add_argument("--db", help="Run the server in database type.",choices=["mysql","postgresql"], default="postgresql")

    # 新增 run_mode
    run_mode = parser.add_argument_group(title="Run Mode", description="Run the server in Async or Sync mode. Default is Async.")
    run_mode.add_argument("--sync", action="store_true", help="Run the server in Sync mode.")

    args = parser.parse_args()

    # 判斷環境
    if args.prod:
        load_dotenv("setting/.env.prod")
    elif args.test:
        load_dotenv("setting/.env.test")
    else:
        load_dotenv("setting/.env.dev")

    # 同步或非同步存取
    if args.sync:
        os.environ["RUN_MODE"] = "SYNC"
    else:
        os.environ["RUN_MODE"] = "ASYNC"

    # export DB_TYPE 環境變數
    os.environ["DB_TYPE"] = args.db

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT")), reload=bool(os.getenv("RELOAD")))