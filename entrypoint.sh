#!/bin/bash
# entrypoint.sh

DB_HOST="postgres-db"
DB_PORT="5432"
DB_USER="$POSTGRES_USER" 
DB_NAME="$POSTGRES_DB"   

echo "Esperando a que $DB_HOST:$DB_PORT esté disponible..."


until nc -z $DB_HOST $DB_PORT; do
  echo "PostgreSQL no disponible todavía, esperando..."
  sleep 2
done

echo " PostgreSQL está activo. Iniciando la aplicación web."


exec "$@"