from flask import Flask
from flask_cors import CORS

# --- TECHNICAL ---
from controllers.technical.imputaciones_user_controller import imputaciones_user_bp
from controllers.technical.myprojects_controller import myprojects_bp
from controllers.technical.ausencias_controller import ausencias_bp

# --- ADMIN ---
from controllers.admin.usuarios_controller import usuarios_bp
from controllers.admin.proyectos_controller import proyectos_bp
from controllers.admin.auditoria_controller import auditoria_bp
from controllers.admin.dashboard_controller import dashboard_bp
from controllers.admin.tickets_controller import tickets_bp

# --- MANAGER ---
from controllers.manager.analytics_controller import manager_analytics_bp
from controllers.manager.closing_controller import closing_bp
from controllers.manager.projects_controller import manager_projects_bp
from controllers.manager.validation_controller import validation_bp

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
app.register_blueprint(tickets_bp)

# REGISTRAMOS LOS NUEVOS DE MANAGER
app.register_blueprint(manager_analytics_bp)
app.register_blueprint(closing_bp)
app.register_blueprint(manager_projects_bp)
app.register_blueprint(validation_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)