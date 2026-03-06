from database.connection import get_db_connection
import traceback
from datetime import datetime

def obtener_imputaciones_semana(usuario_id, fecha_lunes):
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
        cursor.execute(query, (usuario_id, fecha_lunes, fecha_lunes))
        columnas = [column[0] for column in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()

def guardar_imputaciones_lote(usuario_id, filas, fechas_semana):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        for fila in filas:
            p_id = fila.get('id_proyecto')
            if not p_id: continue
            for i in range(7):
                fecha = fechas_semana[i]
                h = float(fila.get('horas')[i] or 0)
                cursor.execute("DELETE FROM Imputaciones WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?", (usuario_id, p_id, fecha))
                if h > 0:
                    cursor.execute("INSERT INTO Imputaciones (UsuarioId, ProyectoId, Fecha, Horas, Estado) VALUES (?, ?, ?, ?, 'Borrador')", (usuario_id, p_id, fecha, h))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def obtener_analitica_mensual(usuario_id, mes, anio):
    conn = get_db_connection()
    default_data = {
        "proyectos": [], 
        "totales": {"mes_real": 0, "ano_acumulado": 0, "mes_nombre": ""}
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
        cursor.execute(query_p, (usuario_id, mes, anio))
        rows = cursor.fetchall()

        cursor.execute("SELECT SUM(Horas) FROM Imputaciones WHERE UsuarioId = ? AND YEAR(Fecha) = ?", (usuario_id, anio))
        total_ano = float(cursor.fetchone()[0] or 0)

        cursor.execute("SELECT SUM(Horas) FROM Imputaciones WHERE UsuarioId = ? AND MONTH(Fecha) = ? AND YEAR(Fecha) = ?", (usuario_id, mes, anio))
        total_mes = float(cursor.fetchone()[0] or 0)

        proyectos_data = []
        for r in rows:
            real_val = float(r[2] or 0)
            asignado_sem = 10.0 
            obj_mensual = asignado_sem * 4
            
            proyectos_data.append({
                "proyecto": r[0],
                "cliente": r[1],
                "real": real_val,
                "asignado_semanal": asignado_sem,
                "objetivo_mensual": obj_mensual,
                "porcentaje": round((real_val / obj_mensual) * 100, 1) if obj_mensual > 0 else 0
            })

        return {
            "proyectos": proyectos_data,
            "totales": {
                "mes_real": total_mes,
                "ano_acumulado": total_ano,
                "mes_nombre": f"Mes {mes} / {anio}"
            }
        }
    except Exception:
        traceback.print_exc()
        return default_data
    finally:
        conn.close()

# --- NUEVA API PARA VER A TODOS LOS USUARIOS ---
def obtener_analitica_equipo(mes, anio):
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
        cursor.execute(query, (mes, anio))
        rows = cursor.fetchall()

        equipo_data = {}
        for r in rows:
            u_id = r[0]
            if u_id not in equipo_data:
                equipo_data[u_id] = {
                    "id": u_id,
                    "nombre_completo": f"{r[1]} {r[2]}",
                    "total_mes": 0.0,
                    "proyectos": []
                }
            
            horas = float(r[5] or 0)
            equipo_data[u_id]["proyectos"].append({
                "proyecto": r[3],
                "cliente": r[4],
                "horas": horas
            })
            equipo_data[u_id]["total_mes"] += horas

        return list(equipo_data.values())
    except Exception:
        traceback.print_exc()
        return []
    finally:
        conn.close()