from database.connection import get_db_connection
from TimeLog.backend.services.admin.audit_service import register_log

def get_projects():
    conn = get_db_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT p.Id, p.Nombre, c.Nombre as Cliente, p.Estado, p.Tipo
            FROM Proyectos p
            INNER JOIN Clientes c ON p.ClienteId = c.Id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        projects = []
        for row in rows:
            p_id = row[0]
            cursor.execute("""
                SELECT u.Id, u.Nombre 
                FROM Asignaciones a
                INNER JOIN Usuarios u ON a.UsuarioId = u.Id
                WHERE a.ProyectoId = ? AND a.Activo = 1
            """, (p_id,))
            
            team = [{"id": r[0], "name": r[1]} for r in cursor.fetchall()]
            
            # Diccionario estandarizado al inglés para el frontend
            projects.append({
                "id": row[0],
                "name": row[1],
                "client": row[2],
                "status": row[3],
                "type": row[4],
                "team": team
            })
        return projects
    except Exception as e:
        print("Error al obtener proyectos:", e)
        return None
    finally:
        conn.close()

def create_project(data):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # 1. BUSCAR O CREAR EL CLIENTE AUTOMÁTICAMENTE
        client_name = data.get('client', 'Cliente Genérico')
        cursor.execute("SELECT Id FROM Clientes WHERE Nombre = ?", (client_name,))
        client = cursor.fetchone()
        
        if client:
            client_id = client[0]
        else:
            cursor.execute("INSERT INTO Clientes (Nombre, Estado, FechaCreacion) OUTPUT INSERTED.Id VALUES (?, 1, GETDATE())", (client_name,))
            client_id = cursor.fetchone()[0]

        # 2. INSERTAR EL PROYECTO Y OBTENER SU NUEVO ID
        query = """
            INSERT INTO Proyectos (ClienteId, Nombre, Estado, Tipo, FechaCreacion) 
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, 'Proyecto', GETDATE())
        """
        cursor.execute(query, (client_id, data.get('name'), data.get('status', 'Activo')))
        new_project_id = cursor.fetchone()[0]
        
        # 3. GUARDAR EL EQUIPO ASIGNADO (NUEVO)
        user_ids = data.get('user_ids', [])
        for u_id in user_ids:
            cursor.execute("""
                INSERT INTO Asignaciones (ProyectoId, UsuarioId, Activo) 
                VALUES (?, ?, 1)
            """, (new_project_id, u_id))

        conn.commit()
        register_log(1, 'Admin', 'CREAR_PROYECTO', 'info', f"Se creó el proyecto: {data.get('name')}.")
        return True
    except Exception as e:
        print("Error al crear proyecto:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def update_project(project_id, data):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # 1. BUSCAR O CREAR EL CLIENTE AUTOMÁTICAMENTE
        client_name = data.get('client', 'Cliente Genérico')
        cursor.execute("SELECT Id FROM Clientes WHERE Nombre = ?", (client_name,))
        client = cursor.fetchone()
        
        if client:
            client_id = client[0]
        else:
            cursor.execute("INSERT INTO Clientes (Nombre, Estado, FechaCreacion) OUTPUT INSERTED.Id VALUES (?, 1, GETDATE())", (client_name,))
            client_id = cursor.fetchone()[0]

        # 2. ACTUALIZAR LOS DATOS BÁSICOS
        query = "UPDATE Proyectos SET Nombre = ?, Estado = ?, ClienteId = ? WHERE Id = ?"
        cursor.execute(query, (data.get('name'), data.get('status'), client_id, project_id))
        
        # 3. GESTIÓN DE ASIGNACIONES (Borrar y reescribir)
        cursor.execute("DELETE FROM Asignaciones WHERE ProyectoId = ?", (project_id,))
        
        user_ids = data.get('user_ids', [])
        for u_id in user_ids:
            cursor.execute("""
                INSERT INTO Asignaciones (ProyectoId, UsuarioId, Activo) 
                VALUES (?, ?, 1)
            """, (project_id, u_id))
            
        conn.commit()
        register_log(1, 'Admin', 'ACTUALIZAR_PROYECTO', 'info', f"Se actualizó el proyecto: {data.get('name')} y su equipo.")
        return True
    except Exception as e:
        print("Error al actualizar proyecto:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def close_project(project_id):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = "UPDATE Proyectos SET Estado = 'Cerrado', FechaDesactivacion = GETDATE() WHERE Id = ?"
        cursor.execute(query, (project_id,))
        conn.commit()
        register_log(1, 'Admin', 'CERRAR_PROYECTO', 'warning', f"Se ha cerrado el proyecto con ID: {project_id}.")
        return True
    except Exception as e:
        print("Error al cerrar proyecto:", e)
        return False
    finally:
        conn.close()

def hard_delete_project(project_id):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Limpiamos las imputaciones (horas) para evitar error de clave foránea
        cursor.execute("DELETE FROM Imputaciones WHERE ProyectoId = ?", (project_id,))
        
        # 2. Limpiamos las asignaciones de equipo
        cursor.execute("DELETE FROM Asignaciones WHERE ProyectoId = ?", (project_id,))
        
        # 3. Borramos el proyecto
        query = "DELETE FROM Proyectos WHERE Id = ?"
        cursor.execute(query, (project_id,))
        
        conn.commit()
        register_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El proyecto con ID {project_id} fue eliminado de la base de datos.")
        return True
    except Exception as e:
        print("Error al eliminar físicamente el proyecto:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def toggle_project_status(project_id):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Estado, Nombre FROM Proyectos WHERE Id = ?", (project_id,))
        row = cursor.fetchone()
        if not row: return False
        
        current_status = row[0]
        project_name = row[1]
        new_status = 'Cerrado' if current_status == 'Activo' else 'Activo'
        
        cursor.execute("UPDATE Proyectos SET Estado = ? WHERE Id = ?", (new_status, project_id))
        conn.commit()
        
        register_log(1, 'Admin', 'CAMBIO_ESTADO', 'warning' if new_status == 'Cerrado' else 'info', f"El proyecto '{project_name}' ha pasado a estado: {new_status}.")
        return True
    except Exception as e:
        print("Error al cambiar estado del proyecto:", e)
        conn.rollback()
        return False
    finally:
        conn.close()