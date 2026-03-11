from database.connection import get_db_connection
from TimeLog.backend.services.admin.audit_service import register_log

def get_users():
    conn = get_db_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Nombre, OidAzure, Rol, Sede, Activo FROM Usuarios")
        
        # Mapeamos las columnas de la BD a claves en inglés para el Frontend
        columns = ['id', 'name', 'email', 'role', 'location', 'active']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Error al obtener usuarios:", e)
        return None
    finally:
        conn.close()

def create_user(data):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO Usuarios (Nombre, OidAzure, Rol, Sede, Activo, FechaCreacion) 
        VALUES (?, ?, ?, ?, 1, GETDATE())
        """
        # Leemos los datos desde las claves en inglés del JSON enviado por el frontend
        cursor.execute(query, (data['name'], data['email'], data['role'], data['location']))
        conn.commit()
        
        # Registro en auditoría
        register_log(1, 'Admin', 'CREAR_USUARIO', 'info', f"Se ha dado de alta al usuario: {data['name']}.")
        
        return True
    except Exception as e:
        print("Error al crear usuario:", e)
        return False
    finally:
        conn.close()

def update_user(user_id, data):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        query = "UPDATE Usuarios SET Nombre = ?, OidAzure = ?, Rol = ?, Sede = ? WHERE Id = ?"
        cursor.execute(query, (data['name'], data['email'], data['role'], data['location'], user_id))
        conn.commit()
        
        # Registro en auditoría
        register_log(1, 'Admin', 'ACTUALIZAR_USUARIO', 'info', f"Se actualizaron los datos del usuario: {data['name']}.")
        
        return True
    except Exception as e:
        print("Error al actualizar usuario:", e)
        return False
    finally:
        conn.close()

def delete_user(user_id):
    """Baja Lógica"""
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        
        # Rescatamos el nombre del usuario para que el log quede bonito
        cursor.execute("SELECT Nombre FROM Usuarios WHERE Id = ?", (user_id,))
        row = cursor.fetchone()
        name = row[0] if row else f"ID {user_id}"

        # BAJA LÓGICA: No lo borramos de la tabla, solo lo marcamos como inactivo.
        query = "UPDATE Usuarios SET Activo = 0, FechaDesactivacion = GETDATE() WHERE Id = ?"
        cursor.execute(query, (user_id,))
        conn.commit()
        
        register_log(1, 'Admin', 'BAJA_LÓGICA', 'danger', f"El usuario '{name}' fue dado de baja del sistema.")
        
        return True
    except Exception as e:
        print("Error al dar de baja al usuario:", e)
        return False
    finally:
        conn.close()

def toggle_user_status(user_id):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Activo, Nombre FROM Usuarios WHERE Id = ?", (user_id,))
        row = cursor.fetchone()
        if not row: return False
        
        current_status = row[0]
        user_name = row[1]
        new_status = 0 if current_status == 1 else 1 # 0 = Inactivo, 1 = Activo
        
        cursor.execute("UPDATE Usuarios SET Activo = ? WHERE Id = ?", (new_status, user_id))
        conn.commit()
        
        action = 'DESACTIVAR_USUARIO' if new_status == 0 else 'ACTIVAR_USUARIO'
        severity = 'warning' if new_status == 0 else 'info'
        register_log(1, 'Admin', action, severity, f"Se cambió el acceso del usuario '{user_name}'.")
        
        return True
    except Exception as e:
        print("Error al cambiar estado del usuario:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def hard_delete_user(user_id):
    """Borrado Físico Definitivo"""
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT Nombre FROM Usuarios WHERE Id = ?", (user_id,))
        row = cursor.fetchone()
        name = row[0] if row else f"ID {user_id}"

        # LIMPIEZA PREVIA (CRÍTICO)
        cursor.execute("DELETE FROM Asignaciones WHERE UsuarioId = ?", (user_id,))
        
        # BORRADO FÍSICO
        query = "DELETE FROM Usuarios WHERE Id = ?"
        cursor.execute(query, (user_id,))
        conn.commit()
        
        register_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El usuario '{name}' y sus asignaciones fueron borrados físicamente de la base de datos.")
        
        return True
    except Exception as e:
        print("Error al borrar físicamente al usuario:", e)
        conn.rollback() 
        return False
    finally:
        conn.close()