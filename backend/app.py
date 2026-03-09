from flask import Flask
from flask_cors import CORS

# --- IMPORTAMOS LOS CONTROLADORES DE TECHNICAL ---
from controllers.technical.imputaciones_user_controller import imputaciones_user_bp
from controllers.technical.myprojects_controller import myprojects_bp
from controllers.technical.ausencias_controller import ausencias_bp

# --- IMPORTAMOS LOS CONTROLADORES DE ADMIN (Aún en la raíz) ---
from controllers.admin.usuarios_controller import usuarios_bp
from controllers.admin.proyectos_controller import proyectos_bp
from controllers.admin.auditoria_controller import auditoria_bp
from controllers.admin.dashboard_controller import dashboard_bp

app = Flask(__name__)
CORS(app)

# REGISTRAMOS TODOS LOS BLUEPRINTS
app.register_blueprint(usuarios_bp)
app.register_blueprint(proyectos_bp)
app.register_blueprint(auditoria_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(imputaciones_user_bp)
app.register_blueprint(myprojects_bp)
app.register_blueprint(ausencias_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)