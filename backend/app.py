from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
# import pyodbc  # <-- No hace falta para SQLite
import os
import sqlite3

# variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración SQLite
DB_FILE = 'timelog.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Para acceder a las columnas por nombre
    return conn

def init_db():
    """Inicializa la base de datos con el archivo schema.sql si no existe"""
    if not os.path.exists(DB_FILE):
        with app.app_context():
            conn = get_db_connection()
            try:
                with open('schema.sql', mode='r') as f:
                    conn.cursor().executescript(f.read())
                conn.commit()
                print("Base de datos inicializada correctamente.")
            except FileNotFoundError:
                print("Error: No se encontró el archivo 'schema.sql'.")
            finally:
                conn.close()

# --- RUTAS DE EJEMPLO ---

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "database": "SQLite conectada"})

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"mensaje": "¡Backend en Flask funcionando correctamente!"})

# --- RUTAS DE PRUEBA PARA AZURE SQL (COMENTADAS) ---
# def get_connection():
#     conn_str = (
#         f"DRIVER={DB_CONFIG['driver']};"
#         f"SERVER={DB_CONFIG['server']};"
#         f"DATABASE={DB_CONFIG['database']};"
#         f"UID={DB_CONFIG['username']};"
#         f"PWD={DB_CONFIG['password']};"
#         "Encrypt=yes;"
#         "TrustServerCertificate=no;"
#         "Connection Timeout=30;"
#     )
#     return pyodbc.connect(conn_str)

# @app.route('/api/db-test', methods=['GET'])
# def db_test():
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1")
#         return jsonify({"db": "Conexión a Azure SQL OK"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db() # Aseguramos que se crea la DB al arrancar
    app.run(debug=True, port=5000)