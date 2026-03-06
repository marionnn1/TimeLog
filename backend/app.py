from flask import Flask
from flask_cors import CORS

# 1. IMPORTAMOS TODOS LOS CONTROLADORES
from controllers.admin.usuarios_controller import usuarios_bp
from controllers.admin.proyectos_controller import proyectos_bp
from controllers.admin.auditoria_controller import auditoria_bp
from controllers.admin.dashboard_controller import dashboard_bp

from controllers.manager.analytics_controller import manager_analytics_bp
from controllers.manager.closing_controller import closing_bp
from controllers.manager.validation_controller import validation_bp
from controllers.manager.projects_controller import manager_projects_bp

app = Flask(__name__)
CORS(app)

# 2. REGISTRAMOS TODOS LOS CONTROLADORES
app.register_blueprint(usuarios_bp)
app.register_blueprint(proyectos_bp)
app.register_blueprint(auditoria_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(manager_analytics_bp)
app.register_blueprint(closing_bp)
app.register_blueprint(validation_bp)
app.register_blueprint(manager_projects_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)