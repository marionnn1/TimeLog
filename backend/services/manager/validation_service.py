from database.connection import get_db_connection

def get_pending_validations():
    conn = get_db_connection()
    if not conn: return {"error": "No se pudo conectar a la base de datos"}, 500

    try:
        cursor = conn.cursor()
        # Buscamos imputaciones que estén en estado 'Pendiente'
        cursor.execute("""
            SELECT i.Id, u.Nombre as Usuario, p.Nombre as Proyecto, c.Nombre as Cliente,
                   i.Fecha, i.Horas as HorasActuales, i.Comentario as Motivo
            FROM Imputaciones i
            JOIN Usuarios u ON i.UsuarioId = u.Id
            JOIN Proyectos p ON i.ProyectoId = p.Id
            LEFT JOIN Clientes c ON p.ClienteId = c.Id
            WHERE i.Estado = 'Pendiente'
        """)
        
        solicitudes = []
        for row in cursor.fetchall():
            # Sacamos las iniciales para el avatar
            nombres = row.Usuario.split()
            avatar = (nombres[0][0] + (nombres[1][0] if len(nombres) > 1 else '')).upper()
            
            solicitudes.append({
                "id": row.Id,
                "usuario": row.Usuario,
                "avatar": avatar,
                "fecha": row.Fecha.strftime('%Y-%m-%d'),
                "proyecto": row.Proyecto,
                "cliente": row.Cliente or 'Interno',
                "horasActuales": float(row.HorasActuales),
                "motivo": row.Motivo or 'Sin motivo especificado',
                "estado": 'pendiente'
            })

        conn.close()
        return solicitudes, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500

def approve_validation(imputacion_id, nuevas_horas):
    conn = get_db_connection()
    if not conn: return {"error": "No se pudo conectar a la base de datos"}, 500

    try:
        cursor = conn.cursor()
        # Aprobamos la imputación y le ponemos las horas corregidas
        cursor.execute("""
            UPDATE Imputaciones
            SET Horas = ?, Estado = 'Aprobado', FechaValidacion = GETDATE()
            WHERE Id = ?
        """, (nuevas_horas, imputacion_id))
        
        conn.commit()
        conn.close()
        return {"message": "Solicitud aprobada y corregida"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500

def reject_validation(imputacion_id, motivo_rechazo):
    conn = get_db_connection()
    if not conn: return {"error": "No se pudo conectar a la base de datos"}, 500

    try:
        cursor = conn.cursor()
        # Marcamos como rechazada
        cursor.execute("""
            UPDATE Imputaciones
            SET Estado = 'Rechazado'
            WHERE Id = ?
        """, (imputacion_id,))
        
        # Dejamos un log en la auditoría para que quede constancia del motivo
        cursor.execute("""
            INSERT INTO Auditoria (ActorNombre, Accion, Gravedad, Detalle)
            VALUES ('Manager', 'Rechazo Solicitud', 'warning', ?)
        """, (f"Solicitud {imputacion_id} rechazada. Motivo: {motivo_rechazo}",))
        
        conn.commit()
        conn.close()
        return {"message": "Solicitud rechazada"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500