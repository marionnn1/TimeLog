from flask import Flask
from flask_cors import CORS

# --- SQLALCHEMY IMPORTS ---
from config import SQLALCHEMY_DATABASE_URI
from database.db import db

# --- TECHNICAL ---
from TimeLog.backend.controllers.technical.time_entries_user_controller import time_entries_user_bp
from controllers.technical.myprojects_controller import myprojects_bp
from TimeLog.backend.controllers.technical.absences_controller import absences_bp

# --- ADMIN ---
from TimeLog.backend.controllers.admin.users_controller import users_bp
from TimeLog.backend.controllers.admin.projects_controller import projects_bp
from TimeLog.backend.controllers.admin.audit_controller import audit_bp
from controllers.admin.dashboard_controller import dashboard_bp
from controllers.admin.tickets_controller import tickets_bp

# --- MANAGER ---
from controllers.manager.analytics_controller import manager_analytics_bp
from controllers.manager.closing_controller import closing_bp
from controllers.manager.projects_controller import manager_projects_bp
from controllers.manager.validation_controller import validation_bp

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN SQLALCHEMY ---
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Importamos los modelos dentro del contexto de la app
with app.app_context():
    from models.users import Users
    from models.clients import Clients
    from models.projects import Projects
    from models.assignments import Assignments
    from models.time_entries import TimeEntries
    from models.absences import Absences
    from models.month_closings import MonthClosings
    from models.audits import Audits
    from models.logs import Logs

# --- REGISTRO DE BLUEPRINTS ---
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)