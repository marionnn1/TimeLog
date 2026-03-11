from database.connection import get_db_connection

def get_analytics_data(month):
    conn = get_db_connection()
    if not conn:
        return {"error": "Could not connect to the database"}, 500

    try:
        cursor = conn.cursor()
        
        year, month_num = month.split('-')

        cursor.execute("""
            SELECT p.Nombre, ISNULL(SUM(i.Horas), 0) as Horas
            FROM Imputaciones i
            JOIN Proyectos p ON i.ProyectoId = p.Id
            WHERE YEAR(i.Fecha) = ? AND MONTH(i.Fecha) = ?
            GROUP BY p.Nombre
        """, (year, month_num))
        
        project_stats = []
        total_logged_hours = 0
        
        for row in cursor.fetchall():
            hours = float(row.Horas)
            total_logged_hours += hours
            project_stats.append({
                "name": row.Nombre,
                "hours": hours,
                "color": "bg-blue-500", 
                "contributors": [] 
            })

        cursor.execute("""
            SELECT u.Id, u.Nombre, u.Rol, ISNULL(SUM(i.Horas), 0) as HorasImputadas
            FROM Usuarios u
            LEFT JOIN Imputaciones i ON u.Id = i.UsuarioId 
                AND YEAR(i.Fecha) = ? AND MONTH(i.Fecha) = ?
            WHERE u.Activo = 1
            GROUP BY u.Id, u.Nombre, u.Rol
        """, (year, month_num))
        
        employee_workload = []
        total_theoretical_capacity = 0
        
        for row in cursor.fetchall():
            capacity = 160 
            total_theoretical_capacity += capacity
            
            names = row.Nombre.split()
            avatar = (names[0][0] + (names[1][0] if len(names) > 1 else '')).upper()

            employee_workload.append({
                "name": row.Nombre,
                "hours": float(row.HorasImputadas),
                "capacity": capacity,
                "role": row.Rol,
                "avatar": avatar,
                "trend": "equal"
            })

        cursor.execute("""
            SELECT a.Fecha, u.Nombre, a.Tipo, u.Id as userId
            FROM Ausencias a
            JOIN Usuarios u ON a.UsuarioId = u.Id
            WHERE YEAR(a.Fecha) = ? AND MONTH(a.Fecha) = ?
        """, (year, month_num))
        
        absences = []
        for row in cursor.fetchall():
            absences.append({
                "date": row.Fecha.strftime('%Y-%m-%d'),
                "name": row.Nombre,
                "type": row.Tipo,
                "userId": row.userId
            })

        conn.close()

        return {
            "totalLoggedHours": total_logged_hours,
            "totalTheoreticalCapacity": total_theoretical_capacity,
            "projectStats": project_stats,
            "employeeWorkload": employee_workload,
            "absences": absences
        }, 200

    except Exception as e:
        print(f"Error en analytics_service: {e}")
        if conn:
            conn.close()
        return {"error": str(e)}, 500