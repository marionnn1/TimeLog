from flask import Flask
from flask_cors import CORS

# 1. IMPORTAMOS TODOS LOS CONTROLADORES
from controllers.usuarios_controller import usuarios_bp
from controllers.proyectos_controller import proyectos_bp
from controllers.auditoria_controller import auditoria_bp
from controllers.dashboard_controller import dashboard_bp

app = Flask(__name__)
CORS(app)

# 2. REGISTRAMOS TODOS LOS CONTROLADORES
app.register_blueprint(usuarios_bp)
app.register_blueprint(proyectos_bp)
app.register_blueprint(auditoria_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)