from database.connection import get_db_connection

def get_closing_audit(mes):
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}, 500

    try:
        cursor = conn.cursor()
        anio, mes_num = mes.split('-')

        # 1. Comprobar si el mes está cerrado en la tabla CierreMes
        cursor.execute("""
            SELECT EstaCerrado FROM CierreMes 
            WHERE Anio = ? AND Mes = ?
        """, (anio, mes_num))
        
        row = cursor.fetchone()
        mes_cerrado = bool(row.EstaCerrado) if row else False

        # 2. Obtener horas imputadas por usuario para ese mes
        cursor.execute("""
            SELECT u.Id, u.Nombre, u.Rol, ISNULL(SUM(i.Horas), 0) as HorasReales
            FROM Usuarios u
            LEFT JOIN Imputaciones i ON u.Id = i.UsuarioId 
                AND YEAR(i.Fecha) = ? AND MONTH(i.Fecha) = ?
            WHERE u.Activo = 1
            GROUP BY u.Id, u.Nombre, u.Rol
        """, (anio, mes_num))
        
        usuarios_auditoria = []
        for row in cursor.fetchall():
            horas_reales = float(row.HorasReales)
            horas_teoricas = 160  # Esto se podría calcular en el futuro según festivos
            
            # Lógica simple de estado
            estado = 'vacio'
            dias_faltantes = []
            if horas_reales >= horas_teoricas:
                estado = 'completo'
            elif horas_reales > 0:
                estado = 'incompleto'
                dias_faltantes = ['Días pendientes'] # Lógica simplificada de momento
                
            usuarios_auditoria.append({
                "id": row.Id,
                "nombre": row.Nombre,
                "rol": row.Rol,
                "horasReales": horas_reales,
                "horasTeoricas": horas_teoricas,
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

        # Buscamos si ya existe un registro para este mes/año
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