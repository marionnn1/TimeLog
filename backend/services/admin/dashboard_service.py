from database.connection import get_db_connection

def obtener_estadisticas():
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        
        # 1. Contar Usuarios Totales
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        total_usuarios = cursor.fetchone()[0]
        
        # 2. Contar Proyectos Activos
        cursor.execute("SELECT COUNT(*) FROM Proyectos WHERE Estado = 'Activo'")
        proyectos_activos = cursor.fetchone()[0]
        
        # 3. Tickets Pendientes (Solicitudes de corrección en estado 'Pendiente')
        cursor.execute("SELECT COUNT(*) FROM Imputaciones WHERE Estado = 'Pendiente'")
        row_pendientes = cursor.fetchone()
        tickets_pendientes = row_pendientes[0] if row_pendientes else 0
        
        # 4. Tickets Totales (Contamos todas las imputaciones que han pasado por algún estado de revisión: Pendientes, Aprobados o Rechazados)
        cursor.execute("SELECT COUNT(*) FROM Imputaciones WHERE Estado != 'Borrador'")
        row_totales = cursor.fetchone()
        tickets_totales = row_totales[0] if row_totales else 0
        
        return {
            "totalUsuarios": total_usuarios,
            "proyectosActivos": proyectos_activos,
            "ticketsPendientes": tickets_pendientes,
            "ticketsTotales": tickets_totales
        }
    except Exception as e:
        print("Error al obtener estadísticas del dashboard:", e)
        return None
    finally:
        conn.close()