from database.connection import get_db_connection
import traceback
from datetime import datetime

def get_weekly_time_entries(user_id, monday_date):
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT i.ProyectoId, p.Nombre as ProyectoNombre, c.Nombre as ClienteNombre, i.Fecha, i.Horas
            FROM Imputaciones i
            INNER JOIN Proyectos p ON i.ProyectoId = p.Id
            INNER JOIN Clientes c ON p.ClienteId = c.Id
            WHERE i.UsuarioId = ? AND i.Fecha >= ? AND i.Fecha <= DATEADD(day, 6, ?)
        """
        cursor.execute(query, (user_id, monday_date, monday_date))
        
        rows = cursor.fetchall()
        return [{
            "projectId": row.ProyectoId,
            "projectName": row.ProyectoNombre,
            "clientName": row.ClienteNombre,
            "date": row.Fecha.strftime('%Y-%m-%d') if row.Fecha else None,
            "hours": float(row.Horas)
        } for row in rows]
    except Exception:
        return []
    finally:
        conn.close()

def save_time_entries_batch(user_id, rows, week_dates):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        for row in rows:
            p_id = row.get('projectId')
            if not p_id: continue
            
            for i in range(7):
                date = week_dates[i]
                h = float(row.get('hours')[i] or 0)
                
                cursor.execute("SELECT Estado FROM Imputaciones WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?", 
                               (user_id, p_id, date))
                db_row = cursor.fetchone()
                
                if db_row and db_row.Estado == 'Aprobado':
                    cursor.execute("""
                        UPDATE Imputaciones SET Estado = 'Pendiente', Horas = ? 
                        WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?
                    """, (h, user_id, p_id, date))
                else:
                    cursor.execute("DELETE FROM Imputaciones WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?", 
                                   (user_id, p_id, date))
                    if h > 0:
                        cursor.execute("INSERT INTO Imputaciones (UsuarioId, ProyectoId, Fecha, Horas, Estado) VALUES (?, ?, ?, ?, 'Borrador')", 
                                       (user_id, p_id, date, h))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_monthly_analytics(user_id, month, year):
    conn = get_db_connection()
    default_data = {
        "projects": [], 
        "totals": {"monthActual": 0, "yearAccumulated": 0, "monthName": ""}
    }
    if not conn: return default_data
    
    try:
        cursor = conn.cursor()
        
        query_p = """
            SELECT p.Nombre, c.Nombre, SUM(i.Horas)
            FROM Imputaciones i
            INNER JOIN Proyectos p ON i.ProyectoId = p.Id
            INNER JOIN Clientes c ON p.ClienteId = c.Id
            WHERE i.UsuarioId = ? AND MONTH(i.Fecha) = ? AND YEAR(i.Fecha) = ?
            GROUP BY p.Nombre, c.Nombre
        """
        cursor.execute(query_p, (user_id, month, year))
        rows = cursor.fetchall()

        cursor.execute("SELECT SUM(Horas) FROM Imputaciones WHERE UsuarioId = ? AND YEAR(Fecha) = ?", (user_id, year))
        year_total = float(cursor.fetchone()[0] or 0)

        cursor.execute("SELECT SUM(Horas) FROM Imputaciones WHERE UsuarioId = ? AND MONTH(Fecha) = ? AND YEAR(Fecha) = ?", (user_id, month, year))
        month_total = float(cursor.fetchone()[0] or 0)

        projects_data = []
        for r in rows:
            actual_val = float(r[2] or 0)
            weekly_assigned = 10.0 
            monthly_goal = weekly_assigned * 4
            
            projects_data.append({
                "project": r[0],
                "client": r[1],
                "actual": actual_val,
                "weeklyAssigned": weekly_assigned,
                "monthlyGoal": monthly_goal,
                "percentage": round((actual_val / monthly_goal) * 100, 1) if monthly_goal > 0 else 0
            })

        return {
            "projects": projects_data,
            "totals": {
                "monthActual": month_total,
                "yearAccumulated": year_total,
                "monthName": f"Month {month} / {year}"
            }
        }
    except Exception:
        traceback.print_exc()
        return default_data
    finally:
        conn.close()

def get_team_analytics(month, year):
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                u.Id as UsuarioId, u.Nombre as UsuarioNombre, u.Apellidos as UsuarioApellidos,
                p.Nombre as Proyecto, c.Nombre as Cliente,
                SUM(i.Horas) as HorasReales
            FROM Imputaciones i
            INNER JOIN Usuarios u ON i.UsuarioId = u.Id
            INNER JOIN Proyectos p ON i.ProyectoId = p.Id
            INNER JOIN Clientes c ON p.ClienteId = c.Id
            WHERE MONTH(i.Fecha) = ? AND YEAR(i.Fecha) = ?
            GROUP BY u.Id, u.Nombre, u.Apellidos, p.Nombre, c.Nombre
            ORDER BY u.Nombre, p.Nombre
        """
        cursor.execute(query, (month, year))
        rows = cursor.fetchall()

        team_data = {}
        for r in rows:
            u_id = r[0]
            if u_id not in team_data:
                team_data[u_id] = {
                    "id": u_id,
                    "fullName": f"{r[1]} {r[2]}",
                    "totalMonth": 0.0,
                    "projects": []
                }
            
            hours = float(r[5] or 0)
            team_data[u_id]["projects"].append({
                "project": r[3],
                "client": r[4],
                "hours": hours
            })
            team_data[u_id]["totalMonth"] += hours

        return list(team_data.values())
    except Exception:
        traceback.print_exc()
        return []
    finally:
        conn.close()

def get_monthly_calendar(user_id, month, year):
    from database.connection import get_db_connection
    conn = get_db_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                DAY(i.Fecha) as dia,
                c.Nombre as cliente,
                p.Id as proyecto_id,
                p.Nombre as proyecto,
                SUM(i.Horas) as horas
            FROM Imputaciones i
            INNER JOIN Proyectos p ON i.ProyectoId = p.Id
            INNER JOIN Clientes c ON p.ClienteId = c.Id
            WHERE i.UsuarioId = ? AND MONTH(i.Fecha) = ? AND YEAR(i.Fecha) = ?
            GROUP BY DAY(i.Fecha), c.Nombre, p.Id, p.Nombre
        """
        cursor.execute(query, (user_id, month, year))
        rows = cursor.fetchall()
        
        data = []
        for r in rows:
            data.append({
                "day": r[0],
                "client": r[1],
                "projectId": r[2],
                "project": r[3],
                "hours": float(r[4])
            })
        return data
    except Exception as e:
        print("Error en obtener_calendario_mensual:", e)
        return []
    finally:
        conn.close()

def request_time_entry_correction(user_id, project_id, date, new_hours, reason):
    from database.connection import get_db_connection
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Imputaciones
            SET Estado = 'Pendiente', Horas = ?, Comentario = ?
            WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?
        """, (new_hours, reason, user_id, project_id, date))
        
        conn.commit()
        
        cursor.execute("""
            INSERT INTO Auditoria (ActorNombre, Accion, Gravedad, Detalle)
            VALUES ('Sistema', 'Solicitud Corrección', 'warning', ?)
        """, (f"Usuario {user_id} solicita cambiar a {new_hours}h el proyecto {project_id} en {date}",))
        conn.commit()
        
        return True
    except Exception as e:
        print("Error en solicitar_correccion:", e)
        conn.rollback()
        return False
    finally:
        conn.close()