from database.connection import get_db_connection

def get_monthly_absences(month, year):
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
        cursor.execute(query, (month, year))
        
        return [{
            "date": row[0].strftime('%Y-%m-%d') if row[0] else None, 
            "type": row[1], 
            "comment": row[2] or "",
            "userId": row[3], 
            "name": row[4],
            "initials": "".join([n[0] for n in row[4].split()[:2]]).upper() if row[4] else "XX"
        } for row in cursor.fetchall()]
    except Exception as e:
        print("Error al obtener ausencias:", e)
        return []
    finally:
        conn.close()

def save_absences(user_id, dates, type, comment=""):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        for date in dates:
            cursor.execute("SELECT Id FROM Ausencias WHERE UsuarioId = ? AND Fecha = ?", (user_id, date))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Ausencias (UsuarioId, Fecha, Tipo, Comentario) 
                    VALUES (?, ?, ?, ?)
                """, (user_id, date, type, comment))
        conn.commit()
        return True
    except Exception as e:
        print("Error al guardar ausencias:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_absence(user_id, date):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Ausencias WHERE UsuarioId = ? AND Fecha = ?", (user_id, date))
        conn.commit()
        return True
    except Exception as e:
        print("Error al eliminar ausencia:", e)
        conn.rollback()
        return False
    finally:
        conn.close()