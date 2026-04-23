#!/bin/bash
set -e

# ==== Color ====
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "$GREEN Load environment variables$NC"
source ./primary-replica/db.env
user=$POSTGRES_USER
db=$POSTGRES_DB
export PGPASSWORD=$POSTGRES_PASSWORD

# wait until primary is ready using `pg_isready`
while ! docker exec primary bash -c "pg_isready -U $user -d $db"; do
    echo -e "$RED Wait until primary is ready$NC"
    sleep 1
done

echo -e "$GREEN List all tables in primary$NC"
docker exec primary bash -c "psql -U $user -d $db -c '\dt'"

# wait until replica is ready using `pg_isready`
while ! docker exec replica pg_isready -U $user -d $db; do
    echo -e "$RED Wait until replica is ready$NC"
    sleep 1
done

echo -e "$GREEN List all tables in replica$NC"
docker exec replica psql -U $user -d $db -c "\dt"

echo -e "$GREEN Checking if replica is in recovery mode...$NC"
docker exec replica psql -U $user -d $db -c "SELECT pg_is_in_recovery();"

echo -e "$GREEN Waiting for replica to connect and start streaming...$NC"
# Explicitly wait for pg_stat_replication to show streaming state
# Timeout after 60 seconds
counter=0
max_attempts=30
while ! docker exec primary psql -U $user -d $db -t -c "SELECT state FROM pg_stat_replication;" | grep -q "streaming"; do
    echo -e "$RED Replica not streaming yet, waiting (attempt $counter/$max_attempts)...$NC"
    if [ $counter -ge $max_attempts ]; then
        echo -e "$RED FAILED: Replica did not start streaming within timeout.$NC"
        echo -e "$RED [Primary Logs]$NC"
        docker logs primary --tail 50
        echo -e "$RED [Replica Logs]$NC"
        docker logs replica --tail 50
        echo -e "$RED [pg_stat_replication]$NC"
        docker exec primary psql -U $user -d $db -c "SELECT * FROM pg_stat_replication;"
        echo -e "$RED [Replica recovery state]$NC"
        docker exec replica psql -U $user -d $db -c "SELECT pg_is_in_recovery(), pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();"
        exit 1
    fi
    sleep 2
    counter=$((counter+1))
done
echo -e "$GREEN Replica is streaming! Proceeding with tests.$NC"

echo -e "$GREEN Add new table in primary$NC"
docker exec primary psql -U $user -d $db -c "CREATE TABLE IF NOT EXISTS test (id int);"
sleep 1

echo -e "$GREEN List all tables in primary$NC"
docker exec primary psql -U $user -d $db -c "\dt"
sleep 1

echo -e "$GREEN List all tables in replica$NC"
docker exec replica psql -U $user -d $db -c "\dt"
sleep 1

echo -e "$GREEN Add new table in primary$NC"
docker exec primary psql -U $user -d $db -c "CREATE TABLE IF NOT EXISTS test2 (id int);"
sleep 1

echo -e "$GREEN List all tables in replica$NC"
docker exec replica psql -U $user -d $db -c "\dt"
sleep 1

echo -e "$RED Remove$NC test2 table in primary"
docker exec primary psql -U $user -d $db -c "DROP TABLE IF EXISTS test2;"

echo -e "$GREEN List all tables in primary$NC"
docker exec primary psql -U $user -d $db -c "\dt"

echo -e "$GREEN List all tables in replica$NC"
docker exec replica psql -U $user -d $db -c "\dt"

echo -e "$RED Remove$NC test table in primary"
docker exec primary psql -U $user -d $db -c "DROP TABLE IF EXISTS test;"

echo -e "$GREEN List all tables in primary$NC"
docker exec primary psql -U $user -d $db -c "\dt"

echo -e "$GREEN List all tables in replica$NC"
docker exec replica psql -U $user -d $db -c "\dt"