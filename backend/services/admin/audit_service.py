from database.connection import get_db_connection

def get_logs():
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT Id, FORMAT(Fecha, 'dd/MM/yyyy HH:mm:ss') as Fecha, 
                   ActorNombre, Accion, Gravedad, Detalle 
            FROM Auditoria 
            ORDER BY Fecha DESC, Id DESC
        """)
        
        columns = ['id', 'date', 'actor', 'action', 'severity', 'detail']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Error al obtener logs:", e)
        return None
    finally:
        conn.close()

def register_log(actor_id, actor_name, action, severity, detail):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO Auditoria (ActorId, ActorNombre, Accion, Gravedad, Detalle) 
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (actor_id, actor_name, action, severity, detail))
        conn.commit()
        return True
    except Exception as e:
        print("Error al guardar log:", e)
        return False
    finally:
        conn.close()