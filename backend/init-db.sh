#!/bin/bash
echo "Esperando a que SQL Server arranque..."
sleep 20s
 
echo "Creando base de datos timelog..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "SuperPassword123!" -C -Q "CREATE DATABASE timelog;"
 
echo "Inyectando las tablas (schema.sql)..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "SuperPassword123!" -d timelog -C -i /app/schema.sql
 
echo "Insertando datos de prueba..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "SuperPassword123!" -d timelog -C -Q "INSERT INTO Usuarios (OidAzure, Nombre, Rol, Sede) VALUES ('12345-abcde', 'Usuario de Prueba Auto', 'Admin', 'Madrid');"
 
echo "¡Base de datos lista!"