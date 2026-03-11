import calendar
from datetime import date
from database.connection import get_db_connection

def get_closing_audit(month):
    conn = get_db_connection()
    if not conn:
        return {"error": "Could not connect to the database"}, 500

    try:
        cursor = conn.cursor()
        year, month_num = map(int, month.split('-'))

        cursor.execute("""
            SELECT EstaCerrado FROM CierreMes 
            WHERE Anio = ? AND Mes = ?
        """, (year, month_num))
        
        row = cursor.fetchone()
        is_month_closed = bool(row.EstaCerrado) if row else False

        _, num_days = calendar.monthrange(year, month_num)

        cursor.execute("SELECT Id, Nombre, Rol FROM Usuarios WHERE Activo = 1")
        users = cursor.fetchall()

        audit_users = []
        
        for u in users:
            u_id = u.Id

            cursor.execute("""
                SELECT ISNULL(SUM(Horas), 0) FROM Imputaciones 
                WHERE UsuarioId = ? AND YEAR(Fecha) = ? AND MONTH(Fecha) = ?
            """, (u_id, year, month_num))
            actual_hours = float(cursor.fetchone()[0] or 0)
            
            cursor.execute("""
                SELECT DISTINCT DAY(Fecha) FROM Imputaciones
                WHERE UsuarioId = ? AND YEAR(Fecha) = ? AND MONTH(Fecha) = ? AND Horas > 0
            """, (u_id, year, month_num))
            logged_days = {r[0] for r in cursor.fetchall()}

            cursor.execute("""
                SELECT DISTINCT DAY(Fecha) FROM Ausencias
                WHERE UsuarioId = ? AND YEAR(Fecha) = ? AND MONTH(Fecha) = ?
            """, (u_id, year, month_num))
            absence_days = {r[0] for r in cursor.fetchall()}

            missing_days = []
            total_work_days = 0
            
            for day in range(1, num_days + 1):
                current_date = date(year, month_num, day)
                if current_date.weekday() < 5: 
                    total_work_days += 1
                    if day not in logged_days and day not in absence_days:
                        missing_days.append(str(day))
            
            if len(missing_days) == 0:
                status = 'complete'
            elif len(missing_days) == total_work_days and actual_hours == 0:
                status = 'empty'
            else:
                status = 'incomplete'
                      
            audit_users.append({
                "id": u_id,
                "name": u.Nombre,
                "role": u.Rol,
                "actualHours": actual_hours,
                "status": status,
                "missingDays": missing_days
            })

        conn.close()
        return {"isMonthClosed": is_month_closed, "users": audit_users}, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500


def toggle_closing_month(month, action):
    conn = get_db_connection()
    if not conn:
        return {"error": "Could not connect to the database"}, 500

    try:
        cursor = conn.cursor()
        year, month_num = month.split('-')
        
        is_closed = 1 if action == 'close' else 0

        cursor.execute("SELECT Id FROM CierreMes WHERE Anio = ? AND Mes = ?", (year, month_num))
        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                UPDATE CierreMes 
                SET EstaCerrado = ?, FechaCierre = GETDATE()
                WHERE Anio = ? AND Mes = ?
            """, (is_closed, year, month_num))
        else:
            cursor.execute("""
                INSERT INTO CierreMes (Anio, Mes, EstaCerrado)
                VALUES (?, ?, ?)
            """, (year, month_num, is_closed))

        conn.commit()
        conn.close()
        
        action_msg = "closed" if action == 'close' else "opened"
        return {"message": f"Month {action_msg} successfully"}, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500