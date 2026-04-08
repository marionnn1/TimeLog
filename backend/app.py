from flask import Flask
from flask_cors import CORS

# --- SEGURIDAD ---
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- SQLALCHEMY IMPORTS ---
from config import SQLALCHEMY_DATABASE_URI
from database.db import db

# --- TECHNICAL ---
from controllers.technical.time_entries_user_controller import time_entries_user_bp
from controllers.technical.myprojects_controller import myprojects_bp
from controllers.technical.absences_controller import absences_bp

# --- ADMIN ---
from controllers.admin.users_controller import users_bp
from controllers.admin.projects_controller import projects_bp
from controllers.admin.audit_controller import audit_bp
from controllers.admin.dashboard_controller import dashboard_bp
from controllers.admin.tickets_controller import tickets_bp

# --- MANAGER ---
from controllers.manager.analytics_controller import manager_analytics_bp
from controllers.manager.closing_controller import closing_bp
from controllers.manager.projects_controller import manager_projects_bp
from controllers.manager.validation_controller import validation_bp

app = Flask(__name__)

# 1. CONFIGURACIÓN EXPLÍCITA DE CORS
# Esto soluciona el error "Response to preflight request doesn't pass access control check"
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://timelog-frontend.agreeablesea-20b4e4bb.spaincentral.azurecontainerapps.io",
            "http://localhost:5173"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 2. CONFIGURACIÓN DE TALISMAN PARA AZURE
# Desactivamos force_https porque Azure gestiona el SSL en el balanceador y
# eliminamos el CSP estricto que suele bloquear las peticiones Preflight en producción.
Talisman(app, 
         force_https=False, 
         content_security_policy=None)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://",
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.before_request
def handle_before_request():
    db.session.rollback()

from errors import register_error_handlers
register_error_handlers(app)

with app.app_context():
    import models

# Registro de Blueprints
app.register_blueprint(users_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(audit_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(time_entries_user_bp)
app.register_blueprint(myprojects_bp)
app.register_blueprint(absences_bp)
app.register_blueprint(tickets_bp)

app.register_blueprint(manager_analytics_bp)
app.register_blueprint(closing_bp)
app.register_blueprint(manager_projects_bp)
app.register_blueprint(validation_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)