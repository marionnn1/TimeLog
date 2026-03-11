from database.db import db
from models.users import Users
from models.projects import Projects
from models.time_entries import TimeEntries

def obtener_estadisticas():
    try:
        total_usuarios = Users.query.count()
        
        proyectos_activos = Projects.query.filter_by(estado='Activo').count()
        
        tickets_pendientes = TimeEntries.query.filter_by(estado='Pendiente').count()
        
        tickets_totales = TimeEntries.query.filter(TimeEntries.estado != 'Borrador').count()
        
        return {
            "totalUsuarios": total_usuarios,
            "proyectosActivos": proyectos_activos,
            "ticketsPendientes": tickets_pendientes,
            "ticketsTotales": tickets_totales
        }
    except Exception as e:
        print(f"Error al obtener estadísticas del dashboard: {e}")
        return None