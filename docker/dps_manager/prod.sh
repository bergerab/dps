#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
	sleep 0.5	
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py initadmin
python manage.py initapikey

exec "$@"
