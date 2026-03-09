from database.connection import get_db_connection

def obtener_ausencias_mes(mes, anio):
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT a.Fecha, a.Tipo, a.Comentario, u.Id, u.Nombre
            FROM Ausencias a
            INNER JOIN Usuarios u ON a.UsuarioId = u.Id
            WHERE MONTH(a.Fecha) = ? AND YEAR(a.Fecha) = ?
        """
        cursor.execute(query, (mes, anio))
        
        # Formateamos los datos para enviarlos al Frontend
        return [{
            "fecha": row[0].strftime('%Y-%m-%d') if row[0] else None, 
            "tipo": row[1], 
            "comentario": row[2] or "",
            "userId": row[3], 
            "nombre": row[4],
            "iniciales": "".join([n[0] for n in row[4].split()[:2]]).upper() if row[4] else "XX"
        } for row in cursor.fetchall()]
    except Exception as e:
        print("Error al obtener ausencias:", e)
        return []
    finally:
        conn.close()

def guardar_ausencias(usuario_id, fechas, tipo, comentario=""):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        for fecha in fechas:
            # Evitamos duplicados si el usuario ya pidió ese día
            cursor.execute("SELECT Id FROM Ausencias WHERE UsuarioId = ? AND Fecha = ?", (usuario_id, fecha))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Ausencias (UsuarioId, Fecha, Tipo, Comentario) 
                    VALUES (?, ?, ?, ?)
                """, (usuario_id, fecha, tipo, comentario))
        conn.commit()
        return True
    except Exception as e:
        print("Error al guardar ausencias:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def eliminar_ausencia(usuario_id, fecha):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Ausencias WHERE UsuarioId = ? AND Fecha = ?", (usuario_id, fecha))
        conn.commit()
        return True
    except Exception as e:
        print("Error al eliminar ausencia:", e)
        conn.rollback()
        return False
    finally:
        conn.close()