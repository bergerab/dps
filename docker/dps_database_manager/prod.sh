#!/bin/sh

echo "Waiting for TimescaleDB..."

while ! nc -z $SQL_HOST $SQL_PORT; do
    sleep 0.5    
done

echo "TimescaleDB started"

exec "$@"
