from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Importante: Permite que el Frontend hable con este Backend

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"mensaje": "¡Backend en Flask funcionando correctamente!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)