from database.connection import get_db_connection
from services.auditoria_service import registrar_log

def obtener_imputaciones_semana(usuario_id, lunes):
    """Obtiene las horas registradas por un usuario para los 7 días de una semana."""
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        # Consultamos las imputaciones cruzando con Proyectos y Clientes para tener los nombres
        query = """
            SELECT i.ProyectoId, p.Nombre as Proyecto, c.Nombre as Cliente, i.Fecha, i.Horas
            FROM Imputaciones i
            INNER JOIN Proyectos p ON i.ProyectoId = p.Id
            INNER JOIN Clientes c ON p.ClienteId = c.Id
            WHERE i.UsuarioId = ? AND i.Fecha >= ? AND i.Fecha < DATEADD(day, 7, ?)
        """
        cursor.execute(query, (usuario_id, lunes, lunes))
        columnas = [column[0] for column in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error al obtener imputaciones: {e}")
        return None
    finally:
        conn.close()

def guardar_imputaciones_lote(usuario_id, filas, fechas_semana):
    """Guarda o actualiza las horas de la semana en lote para evitar múltiples peticiones."""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        for fila in filas:
            proyecto_id = fila.get('id_proyecto')
            horas = fila.get('horas') # Lista de 7 valores (Lunes a Domingo)
            
            for i in range(7):
                fecha = fechas_semana[i]
                h = float(horas[i]) if horas[i] else 0
                
                # Borrado previo para sobrescribir el registro (Estrategia de Sincronización)
                cursor.execute("DELETE FROM Imputaciones WHERE UsuarioId = ? AND ProyectoId = ? AND Fecha = ?", 
                               (usuario_id, proyecto_id, fecha))
                
                if h > 0:
                    cursor.execute("""
                        INSERT INTO Imputaciones (UsuarioId, ProyectoId, Fecha, Horas, Estado)
                        VALUES (?, ?, ?, ?, 'Borrador')
                    """, (usuario_id, proyecto_id, fecha, h))
        
        conn.commit()
        registrar_log(usuario_id, 'Usuario', 'SYNC_IMPUTACIONES', 'info', "Sincronización semanal de horas realizada.")
        return True
    except Exception as e:
        print(f"Error al guardar lote de imputaciones: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()