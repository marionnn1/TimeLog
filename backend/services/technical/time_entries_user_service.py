from database.connection import get_db_connection
from TimeLog.backend.services.admin.audit_service import register_log

def get_weekly_time_entries(user_id, monday_date):
    """Obtiene las horas registradas por un usuario para los 7 días de una semana."""
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        query = """
            SELECT i.ProyectoId, p.Nombre as Proyecto, c.Nombre as Cliente, i.Fecha, i.Horas
            FROM Imputaciones i
            INNER JOIN Proyectos p ON i.ProyectoId = p.Id
            INNER JOIN Clientes c ON p.ClienteId = c.Id
            WHERE i.UsuarioId = ? AND i.Fecha >= ? AND i.Fecha < DATEADD(day, 7, ?)
        """
        cursor.execute(query, (user_id, monday_date, monday_date))
        
        columns = ['projectId', 'project', 'client', 'date', 'hours']
        
        result = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if row_dict['date']:
                row_dict['date'] = row_dict['date'].strftime('%Y-%m-%d')
            result.append(row_dict)
        return result
    except Exception as e:
        print(f"Error al obtener imputaciones: {e}")
        return None
    finally:
        conn.close()

def save_time_entries_batch(user_id, rows, week_dates):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        for row in rows:
            project_id = row.get('projectId')
            hours = row.get('hours')
            
            for i in range(7):
                date = week_dates[i]
                h = float(hours[i]) if hours[i] else 0
                
                cursor.execute("SELECT Estado FROM Imputaciones WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?", 
                               (user_id, project_id, date))
                db_row = cursor.fetchone()
                
                if db_row and db_row.Estado == 'Aprobado':
                    cursor.execute("""
                        UPDATE Imputaciones 
                        SET Estado = 'Pendiente', Horas = ? 
                        WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?
                    """, (h, user_id, project_id, date))
                else:
                    cursor.execute("DELETE FROM Imputaciones WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?", 
                                   (user_id, project_id, date))
                    if h > 0:
                        cursor.execute("""
                            INSERT INTO Imputaciones (UsuarioId, ProyectoId, Fecha, Horas, Estado)
                            VALUES (?, ?, ?, ?, 'Borrador')
                        """, (user_id, project_id, date, h))
        
        conn.commit()
        register_log(user_id, 'User', 'SYNC_IMPUTACIONES', 'info', "Sincronización semanal realizada.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()