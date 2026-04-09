from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import SQLALCHEMY_DATABASE_URI
from database.db import db

# Importación de Blueprints (Admin, Manager, Technical)
from controllers.technical.time_entries_user_controller import time_entries_user_bp
from controllers.technical.myprojects_controller import myprojects_bp
from controllers.technical.absences_controller import absences_bp
from controllers.admin.users_controller import users_bp
from controllers.admin.projects_controller import projects_bp
from controllers.admin.audit_controller import audit_bp
from controllers.admin.dashboard_controller import dashboard_bp
from controllers.admin.tickets_controller import tickets_bp
from controllers.manager.analytics_controller import manager_analytics_bp
from controllers.manager.closing_controller import closing_bp
from controllers.manager.projects_controller import manager_projects_bp
from controllers.manager.validation_controller import validation_bp

app = Flask(__name__)

# 1. CORS EXPLÍCITO PARA PRODUCCIÓN
# Esto soluciona el bloqueo de peticiones OPTIONS y Preflight
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

# 2. CONFIGURACIÓN DE COOKIES Y SEGURIDAD (TALISMAN)
# Soluciona el error "SameSite=none but missing secure attribute"
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None', # Requerido para comunicación entre dominios de Azure
)

Talisman(app, 
         force_https=False, # Azure ya gestiona SSL/HTTPS en el Ingress
         content_security_policy=None) # Evita bloqueos de recursos externos

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://",
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
@app.get("/api")
def get_try():
    try:
        print("Works", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
    

@app.before_request
def handle_before_request():
    db.session.rollback()

from errors import register_error_handlers
register_error_handlers(app)

with app.app_context():
    import models

# Registro de rutas
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