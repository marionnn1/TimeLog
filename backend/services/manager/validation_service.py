from database.connection import get_db_connection

def get_pending_validations():
    conn = get_db_connection()
    if not conn: return {"error": "Could not connect to the database"}, 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.Id, u.Nombre as Usuario, p.Nombre as Proyecto, c.Nombre as Cliente,
                   i.Fecha, i.Horas as HorasActuales, i.Comentario as Motivo
            FROM Imputaciones i
            JOIN Usuarios u ON i.UsuarioId = u.Id
            JOIN Proyectos p ON i.ProyectoId = p.Id
            LEFT JOIN Clientes c ON p.ClienteId = c.Id
            WHERE i.Estado = 'Pendiente'
        """)
        
        requests = []
        for row in cursor.fetchall():
            names = row.Usuario.split()
            avatar = (names[0][0] + (names[1][0] if len(names) > 1 else '')).upper()
            
            requests.append({
                "id": row.Id,
                "user": row.Usuario,
                "avatar": avatar,
                "date": row.Fecha.strftime('%Y-%m-%d'),
                "project": row.Proyecto,
                "client": row.Cliente or 'Internal',
                "currentHours": float(row.HorasActuales),
                "reason": row.Motivo or 'No reason specified',
                "status": 'pending'
            })

        conn.close()
        return requests, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500

def approve_validation(time_entry_id, new_hours):
    conn = get_db_connection()
    if not conn: return {"error": "Could not connect to the database"}, 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Imputaciones
            SET Horas = ?, Estado = 'Aprobado', FechaValidacion = GETDATE()
            WHERE Id = ?
        """, (new_hours, time_entry_id))
        
        conn.commit()
        conn.close()
        return {"message": "Request approved and corrected"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500

def reject_validation(time_entry_id, rejection_reason):
    conn = get_db_connection()
    if not conn: return {"error": "Could not connect to the database"}, 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Imputaciones
            SET Estado = 'Rechazado'
            WHERE Id = ?
        """, (time_entry_id,))
        
        cursor.execute("""
            INSERT INTO Auditoria (ActorNombre, Accion, Gravedad, Detalle)
            VALUES ('Manager', 'Rechazo Solicitud', 'warning', ?)
        """, (f"Solicitud {time_entry_id} rechazada. Motivo: {rejection_reason}",))
        
        conn.commit()
        conn.close()
        return {"message": "Request rejected"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500