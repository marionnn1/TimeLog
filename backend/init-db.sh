#!/bin/bash
set -e

SQLCMD="/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P SuperPassword123! -C"
echo "Esperando a que SQL Server esté disponible..."

for i in {1..50}; do
    if $SQLCMD -Q "SELECT 1" > /dev/null 2>&1; then
        echo "SQL Server listo."
        break
    fi
    echo "Intento $i: Servidor no disponible, esperando..."
    sleep 2
done

echo "Creando base de datos timelog..."
$SQLCMD -Q "IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'timelog') CREATE DATABASE timelog;"

echo "Inyectando las tablas (schema.sql)..."
$SQLCMD -d timelog -i /app/schema.sql

echo "Insertando datos de prueba..."
$SQLCMD -d timelog -Q "INSERT INTO Usuarios (OidAzure, Nombre, Rol, Sede) VALUES ('12345-abcde', 'Usuario de Prueba Auto', 'Admin', 'Madrid');"

echo "¡Base de datos lista!"