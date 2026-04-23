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
repuser=$REPLICA_USER
reppass=$REPLICA_PASSWORD
export PGPASSWORD=$POSTGRES_PASSWORD

echo -e "$GREEN Wait until primary is ready$NC"
while ! docker exec primary pg_isready -U $user -d $db; do
    sleep 1
done

# Get actual PGDATA path from the running container
REAL_PGDATA=$(docker exec primary psql -U $user -d $db -t -c "SHOW data_directory;" | tr -d '[:space:]')
echo -e "$GREEN Primary PGDATA is located at: $REAL_PGDATA$NC"

# Check replication user
echo -e "$GREEN Ensure replication user exists$NC"
exist=$(docker exec primary psql -U $user -d $db -t -c "SELECT 1 FROM pg_roles WHERE rolname = '$repuser';" | tr -d '[:space:]')
if [ "$exist" != "1" ]; then
    docker exec primary psql -U $user -d $db -c "CREATE ROLE \"$repuser\" WITH LOGIN REPLICATION PASSWORD '$reppass';"
fi

# Configure primary
echo -e "$GREEN Configuring Primary pg_hba.conf and postgresql.conf$NC"
# Use a more reliable way to append to pg_hba.conf
docker exec primary bash -c "echo \"host replication $repuser 172.22.0.101/32 scram-sha-256\" >> $REAL_PGDATA/pg_hba.conf"
# Copy configuration file
docker cp ./primary-replica/postgresql.conf primary:$REAL_PGDATA/postgresql.conf

echo -e "$GREEN Restarting Primary to apply changes$NC"
docker restart primary
while ! docker exec primary pg_isready -U $user -d $db; do sleep 1; done

# ==== Replica Setup ====
echo -e "$GREEN Initializing Replica with pg_basebackup...$NC"
# Use docker compose to ensure correct network and volume context
docker compose -f "$dc_file" stop replica

# Wipe replica data and run backup using a temporary container from the same image
# We use the same PGDATA path for consistency
docker compose -f "$dc_file" run --rm --no-deps \
    -e PGPASSWORD="$reppass" \
    replica \
    bash -c "rm -rf /var/lib/postgresql/data/pgdata/* && \
             pg_basebackup -h primary -p 5432 -U $repuser -D /var/lib/postgresql/data/pgdata -R -Xs -P && \
             chown -R 999:999 /var/lib/postgresql/data/pgdata && \
             chmod 700 /var/lib/postgresql/data/pgdata"

echo -e "$GREEN Starting Replica$NC"
docker compose -f "$dc_file" start replica
