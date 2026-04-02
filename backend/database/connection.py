import os
import pyodbc

def get_db_connection():
    try:
        server = f"{os.getenv('DB_SERVER')},{os.getenv('DB_PORT', '1433')}"
        database = os.getenv('DB_NAME')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')

        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error de conexión a la BD: {e}")
        return None