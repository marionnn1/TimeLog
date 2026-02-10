from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pyodbc

from config import DB_CONFIG

# variables
load_dotenv()

app = Flask(__name__)
CORS(app)

def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"mensaje": "¡Backend en Flask funcionando correctamente!"})

@app.route('/api/db-test', methods=['GET'])
def db_test():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return jsonify({"db": "Conexión a Azure SQL OK"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
