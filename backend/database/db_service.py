import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        server = f"{os.getenv('DB_SERVER')},{os.getenv('DB_PORT')}"
        database = os.getenv('DB_NAME')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        
        return pyodbc.connect(connection_string)
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def obtener_usuarios():
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Nombre, Rol, Sede FROM Usuarios") 
    
    columnas = [column[0] for column in cursor.description]
    usuarios = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    
    conn.close()
    return usuarios