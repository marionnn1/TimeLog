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
        
        # 3. Tickets (A 0 hasta que hagamos la tabla)
        tickets_pendientes = 0
        tickets_totales = 0
        
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