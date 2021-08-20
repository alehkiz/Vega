#!/bin/sh
echo $SQL_HOST
if [ "$DATABASE" = "vega_dev" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
echo "$DATABASE"
echo "aqui"
# while true; do
#     flask db upgrade
#     if [[ "$?" == "0" ]]; then
#         break
#     fi
#     echo Upgrade command failed, retrying in 5 secs...
#     sleep 5
# done
flask init-db
echo 'Iniciando servidor...'
# exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app
exec "$@"
