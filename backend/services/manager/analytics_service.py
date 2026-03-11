from database.connection import get_db_connection

def get_analytics_data(mes):
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}, 500

    try:
        cursor = conn.cursor()
        
        # El mes viene en formato 'YYYY-MM' (ej: '2026-02')
        anio, mes_num = mes.split('-')

        # 1. Total horas y Estadísticas por Proyecto
        cursor.execute("""
            SELECT p.Nombre, ISNULL(SUM(i.Horas), 0) as Horas
            FROM Imputaciones i
            JOIN Proyectos p ON i.ProyectoId = p.Id
            WHERE YEAR(i.Fecha) = ? AND MONTH(i.Fecha) = ?
            GROUP BY p.Nombre
        """, (anio, mes_num))
        
        proyectos_stats = []
        total_horas_imputadas = 0
        
        for row in cursor.fetchall():
            horas = float(row.Horas)
            total_horas_imputadas += horas
            proyectos_stats.append({
                "nombre": row.Nombre,
                "horas": horas,
                "color": "bg-blue-500", # Por ahora estático, se podría hacer dinámico
                "contributors": [] # Se podría sacar con otra query si se desea exactitud
            })

        # 2. Carga de Empleados (Horas imputadas por usuario activo)
        cursor.execute("""
            SELECT u.Id, u.Nombre, u.Rol, ISNULL(SUM(i.Horas), 0) as HorasImputadas
            FROM Usuarios u
            LEFT JOIN Imputaciones i ON u.Id = i.UsuarioId 
                AND YEAR(i.Fecha) = ? AND MONTH(i.Fecha) = ?
            WHERE u.Activo = 1
            GROUP BY u.Id, u.Nombre, u.Rol
        """, (anio, mes_num))
        
        carga_empleados = []
        total_capacidad_teorica = 0
        
        for row in cursor.fetchall():
            # Capacidad teórica aproximada (160h/mes). 
            # En un futuro podrías calcular esto exacto usando los campos HorasInvierno_L_J de Usuarios y los días hábiles del mes.
            capacidad = 160 
            total_capacidad_teorica += capacidad
            
            # Extraemos las iniciales para el avatar (Ej: 'Mario León' -> 'ML')
            nombres = row.Nombre.split()
            avatar = (nombres[0][0] + (nombres[1][0] if len(nombres) > 1 else '')).upper()

            carga_empleados.append({
                "nombre": row.Nombre,
                "horas": float(row.HorasImputadas),
                "capacidad": capacidad,
                "rol": row.Rol,
                "avatar": avatar,
                "trend": "equal"
            })

        # 3. Ausencias del mes
        cursor.execute("""
            SELECT a.Fecha, u.Nombre, a.Tipo, u.Id as userId
            FROM Ausencias a
            JOIN Usuarios u ON a.UsuarioId = u.Id
            WHERE YEAR(a.Fecha) = ? AND MONTH(a.Fecha) = ?
        """, (anio, mes_num))
        
        ausencias = []
        for row in cursor.fetchall():
            ausencias.append({
                "date": row.Fecha.strftime('%Y-%m-%d'),
                "nombre": row.Nombre,
                "type": row.Tipo,
                "userId": row.userId
            })

        conn.close()

        # Construimos el JSON de respuesta esperado por el frontend
        return {
            "totalHorasImputadas": total_horas_imputadas,
            "totalCapacidadTeorica": total_capacidad_teorica,
            "proyectosStats": proyectos_stats,
            "cargaEmpleados": carga_empleados,
            "ausencias": ausencias
        }, 200

    except Exception as e:
        print(f"Error en analytics_service: {e}")
        if conn:
            conn.close()
        return {"error": str(e)}, 500