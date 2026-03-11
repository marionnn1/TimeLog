import calendar
from datetime import date
from database.connection import get_db_connection

def get_closing_audit(mes):
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}, 500

    try:
        cursor = conn.cursor()
        anio, mes_num = map(int, mes.split('-'))

        # 1. Comprobar si el mes está cerrado en la tabla CierreMes
        cursor.execute("""
            SELECT EstaCerrado FROM CierreMes 
            WHERE Anio = ? AND Mes = ?
        """, (anio, mes_num))
        
        row = cursor.fetchone()
        mes_cerrado = bool(row.EstaCerrado) if row else False

        # Total de días del mes seleccionado
        _, num_days = calendar.monthrange(anio, mes_num)

        # 2. Obtener usuarios activos
        cursor.execute("SELECT Id, Nombre, Rol FROM Usuarios WHERE Activo = 1")
        usuarios = cursor.fetchall()

        usuarios_auditoria = []
        
        for u in usuarios:
            u_id = u.Id
            
            # Horas reales totales imputadas en el mes
            cursor.execute("""
                SELECT ISNULL(SUM(Horas), 0) FROM Imputaciones 
                WHERE UsuarioId = ? AND YEAR(Fecha) = ? AND MONTH(Fecha) = ?
            """, (u_id, anio, mes_num))
            horas_reales = float(cursor.fetchone()[0] or 0)
            
            # Días laborables con imputaciones (Horas > 0)
            cursor.execute("""
                SELECT DISTINCT DAY(Fecha) FROM Imputaciones
                WHERE UsuarioId = ? AND YEAR(Fecha) = ? AND MONTH(Fecha) = ? AND Horas > 0
            """, (u_id, anio, mes_num))
            dias_imputados = {r[0] for r in cursor.fetchall()}
            
            # Días con ausencias registradas (vacaciones, festivos, asuntos propios)
            cursor.execute("""
                SELECT DISTINCT DAY(Fecha) FROM Ausencias
                WHERE UsuarioId = ? AND YEAR(Fecha) = ? AND MONTH(Fecha) = ?
            """, (u_id, anio, mes_num))
            dias_ausencias = {r[0] for r in cursor.fetchall()}
            
            # Calcular días faltantes (Lunes a Viernes sin imputaciones ni ausencias)
            dias_faltantes = []
            dias_laborables_totales = 0
            
            for day in range(1, num_days + 1):
                current_date = date(anio, mes_num, day)
                if current_date.weekday() < 5: # 0-4 representan Lunes a Viernes
                    dias_laborables_totales += 1
                    if day not in dias_imputados and day not in dias_ausencias:
                        dias_faltantes.append(str(day))
            
            # Determinar el estado del usuario
            if len(dias_faltantes) == 0:
                estado = 'completo'
            elif len(dias_faltantes) == dias_laborables_totales and horas_reales == 0:
                estado = 'vacio'
            else:
                estado = 'incompleto'
                     
            usuarios_auditoria.append({
                "id": u_id,
                "nombre": u.Nombre,
                "rol": u.Rol,
                "horasReales": horas_reales,
                "estado": estado,
                "diasFaltantes": dias_faltantes
            })

        conn.close()
        return {"mesCerrado": mes_cerrado, "usuarios": usuarios_auditoria}, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500


def toggle_closing_month(mes, accion):
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}, 500

    try:
        cursor = conn.cursor()
        anio, mes_num = mes.split('-')
        esta_cerrado = 1 if accion == 'cerrar' else 0

        cursor.execute("SELECT Id FROM CierreMes WHERE Anio = ? AND Mes = ?", (anio, mes_num))
        existe = cursor.fetchone()

        if existe:
            cursor.execute("""
                UPDATE CierreMes 
                SET EstaCerrado = ?, FechaCierre = GETDATE()
                WHERE Anio = ? AND Mes = ?
            """, (esta_cerrado, anio, mes_num))
        else:
            cursor.execute("""
                INSERT INTO CierreMes (Anio, Mes, EstaCerrado)
                VALUES (?, ?, ?)
            """, (anio, mes_num, esta_cerrado))

        conn.commit()
        conn.close()
        return {"message": f"Mes {accion} correctamente"}, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500