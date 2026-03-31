import os
from urllib.parse import quote_plus

server = os.getenv("DB_SERVER", "localhost")
port = os.getenv("DB_PORT", "1433")
database = os.getenv("DB_NAME", "timelog")
username = os.getenv("DB_USER", "sa")
password = os.getenv("DB_PASSWORD", "SuperPassword123!")
driver = "ODBC Driver 17 for SQL Server"

pwd_encoded = quote_plus(password)
driver_encoded = quote_plus(driver)

SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{username}:{pwd_encoded}@{server}:{port}/{database}?driver={driver_encoded}&TrustServerCertificate=yes"