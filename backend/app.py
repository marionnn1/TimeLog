from flask import Flask, jsonify
from flask_cors import CORS
from database.db_service import obtener_usuarios

app = Flask(__name__)
CORS(app)

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    # Llamamos al servicio que creamos, dejando este controlador súper limpio
    usuarios = obtener_usuarios()
    
    if usuarios is not None:
        return jsonify({
            "status": "success", 
            "data": usuarios
        }), 200
    else:
        return jsonify({
            "status": "error", 
            "message": "Fallo en la conexión a SQL Server"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)