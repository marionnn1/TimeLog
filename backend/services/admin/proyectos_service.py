from database.connection import get_db_connection
from services.admin.auditoria_service import registrar_log

def obtener_proyectos():
    conn = get_db_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor()
        # Traemos los datos básicos del proyecto
        query = """
            SELECT p.Id, p.Nombre, c.Nombre as Cliente, p.Estado, p.Tipo
            FROM Proyectos p
            INNER JOIN Clientes c ON p.ClienteId = c.Id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        proyectos = []
        for row in rows:
            p_id = row[0]
            # IMPORTANTE: Buscamos el equipo asignado para este proyecto
            cursor.execute("""
                SELECT u.Id, u.Nombre 
                FROM Asignaciones a
                INNER JOIN Usuarios u ON a.UsuarioId = u.Id
                WHERE a.ProyectoId = ? AND a.Activo = 1
            """, (p_id,))
            
            # Formateamos el equipo para que Vue lo entienda
            equipo = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]
            
            proyectos.append({
                "Id": row[0],
                "Nombre": row[1],
                "Cliente": row[2],
                "Estado": row[3],
                "Tipo": row[4],
                "Equipo": equipo
            })
        return proyectos
    except Exception as e:
        print("Error al obtener proyectos:", e)
        return None
    finally:
        conn.close()

def crear_proyecto(datos):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM Clientes WHERE Nombre = ?", (datos['cliente'],))
        cliente = cursor.fetchone()
        cliente_id = cliente[0] if cliente else 1 

        query = """
            INSERT INTO Proyectos (ClienteId, Nombre, Estado, Tipo, FechaCreacion) 
            VALUES (?, ?, ?, 'Proyecto', GETDATE())
        """
        cursor.execute(query, (cliente_id, datos['nombre'], datos['estado']))
        conn.commit()
        
        # REGISTRO EN AUDITORÍA
        registrar_log(1, 'Admin', 'CREAR_PROYECTO', 'info', f"Se creó el proyecto: {datos['nombre']}.")
        
        return True
    except Exception as e:
        print("Error al crear proyecto:", e)
        return False
    finally:
        conn.close()

def actualizar_proyecto(id_proyecto, datos):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Actualizamos el nombre y el estado del proyecto
        query = "UPDATE Proyectos SET Nombre = ?, Estado = ? WHERE Id = ?"
        cursor.execute(query, (datos['nombre'], datos['estado'], id_proyecto))
        
        # 2. GESTIÓN DE ASIGNACIONES: Borramos las actuales e insertamos las nuevas
        cursor.execute("DELETE FROM Asignaciones WHERE ProyectoId = ?", (id_proyecto,))
        
        usuarios_ids = datos.get('usuarios_ids', [])
        for u_id in usuarios_ids:
            cursor.execute("""
                INSERT INTO Asignaciones (ProyectoId, UsuarioId, Activo) 
                VALUES (?, ?, 1)
            """, (id_proyecto, u_id))
            
        conn.commit()
        
        # REGISTRO EN AUDITORÍA
        registrar_log(1, 'Admin', 'ACTUALIZAR_PROYECTO', 'info', f"Se actualizó el proyecto: {datos['nombre']} y su equipo de trabajo.")
        
        return True
    except Exception as e:
        print("Error al actualizar proyecto:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def cerrar_proyecto(id_proyecto):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = "UPDATE Proyectos SET Estado = 'Cerrado', FechaDesactivacion = GETDATE() WHERE Id = ?"
        cursor.execute(query, (id_proyecto,))
        conn.commit()
        
        # REGISTRO EN AUDITORÍA
        registrar_log(1, 'Admin', 'CERRAR_PROYECTO', 'warning', f"Se ha cerrado el proyecto con ID: {id_proyecto}.")
        
        return True
    except Exception as e:
        print("Error al cerrar proyecto:", e)
        return False
    finally:
        conn.close()

def eliminar_proyecto_fisico(id_proyecto):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # Primero limpiamos las asignaciones para evitar error de clave foránea
        cursor.execute("DELETE FROM Asignaciones WHERE ProyectoId = ?", (id_proyecto,))
        # Ahora borramos el proyecto
        query = "DELETE FROM Proyectos WHERE Id = ?"
        cursor.execute(query, (id_proyecto,))
        conn.commit()
        
        # REGISTRO EN AUDITORÍA
        registrar_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El proyecto con ID {id_proyecto} y todas sus asignaciones fueron eliminados permanentemente de la base de datos.")
        
        return True
    except Exception as e:
        print("Error al eliminar físicamente el proyecto:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def toggle_estado_proyecto(id_proyecto):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Miramos cómo está ahora
        cursor.execute("SELECT Estado, Nombre FROM Proyectos WHERE Id = ?", (id_proyecto,))
        row = cursor.fetchone()
        if not row: return False
        
        estado_actual = row[0]
        nombre_proyecto = row[1]
        nuevo_estado = 'Cerrado' if estado_actual == 'Activo' else 'Activo'
        
        # 2. Lo cambiamos
        cursor.execute("UPDATE Proyectos SET Estado = ? WHERE Id = ?", (nuevo_estado, id_proyecto))
        conn.commit()
        
        # 3. Dejamos rastro en auditoría
        registrar_log(1, 'Admin', 'CAMBIO_ESTADO', 'warning' if nuevo_estado == 'Cerrado' else 'info', f"El proyecto '{nombre_proyecto}' ha pasado a estado: {nuevo_estado}.")
        
        return True
    except Exception as e:
        print("Error al cambiar estado del proyecto:", e)
        conn.rollback()
        return False
    finally:
        conn.close()