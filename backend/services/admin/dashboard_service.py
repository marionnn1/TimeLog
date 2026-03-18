from database.db import db
from models.users import Users
from models.projects import Projects
from models.time_entries import TimeEntries

def get_statistics():
    try:
        total_users = Users.query.count()
        
        active_projects = Projects.query.filter_by(estado='Activo').count()
        
        pending_tickets = TimeEntries.query.filter_by(estado='Pendiente').count()
        
        total_tickets = TimeEntries.query.filter(TimeEntries.estado != 'Borrador').count()
        
        return {
            "totalUsers": total_users,
            "activeProjects": active_projects,
            "pendingTickets": pending_tickets,
            "totalTickets": total_tickets
        }
    except Exception as e:
        print(f"Error al obtener estadísticas del dashboard: {e}")
        return None