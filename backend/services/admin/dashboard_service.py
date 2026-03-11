from database.connection import get_db_connection

def get_statistics():
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Proyectos WHERE Estado = 'Activo'")
        active_projects = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Imputaciones WHERE Estado = 'Pendiente'")
        row_pending = cursor.fetchone()
        pending_tickets = row_pending[0] if row_pending else 0
        
        cursor.execute("SELECT COUNT(*) FROM Imputaciones WHERE Estado != 'Borrador'")
        row_total = cursor.fetchone()
        total_tickets = row_total[0] if row_total else 0
        
        return {
            "totalUsers": total_users,
            "activeProjects": active_projects,
            "pendingTickets": pending_tickets,
            "totalTickets": total_tickets
        }
    except Exception as e:
        print("Error al obtener estadísticas del dashboard:", e)
        return None
    finally:
        conn.close()