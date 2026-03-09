from database.connection import get_db_connection
from services.admin.auditoria_service import registrar_log

def obtener_usuarios():
    conn = get_db_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Nombre, OidAzure, Rol, Sede, Activo FROM Usuarios")
        columnas = [column[0] for column in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Error al obtener usuarios:", e)
        return None
    finally:
        conn.close()

def crear_usuario(datos):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO Usuarios (Nombre, OidAzure, Rol, Sede, Activo, FechaCreacion) 
        VALUES (?, ?, ?, ?, 1, GETDATE())
        """
        cursor.execute(query, (datos['nombre'], datos['email'], datos['rol'], datos['sede']))
        conn.commit()
        
        # <--- 2. AÑADIDO: Registro en auditoría
        registrar_log(1, 'Admin', 'CREAR_USUARIO', 'info', f"Se ha dado de alta al usuario: {datos['nombre']}.")
        
        return True
    except Exception as e:
        print("Error al crear usuario:", e)
        return False
    finally:
        conn.close()

def actualizar_usuario(id_usuario, datos):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        query = "UPDATE Usuarios SET Nombre = ?, OidAzure = ?, Rol = ?, Sede = ? WHERE Id = ?"
        cursor.execute(query, (datos['nombre'], datos['email'], datos['rol'], datos['sede'], id_usuario))
        conn.commit()
        
        # <--- 3. AÑADIDO: Registro en auditoría
        registrar_log(1, 'Admin', 'ACTUALIZAR_USUARIO', 'info', f"Se actualizaron los datos del usuario: {datos['nombre']}.")
        
        return True
    except Exception as e:
        print("Error al actualizar usuario:", e)
        return False
    finally:
        conn.close()

def eliminar_usuario(id_usuario):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        
        # Rescatamos el nombre del usuario para que el log quede bonito
        cursor.execute("SELECT Nombre FROM Usuarios WHERE Id = ?", (id_usuario,))
        row = cursor.fetchone()
        nombre = row[0] if row else f"ID {id_usuario}"

        # BAJA LÓGICA: No lo borramos de la tabla, solo lo marcamos como inactivo y registramos la fecha.
        query = "UPDATE Usuarios SET Activo = 0, FechaDesactivacion = GETDATE() WHERE Id = ?"
        cursor.execute(query, (id_usuario,))
        conn.commit()
        
        # <--- 4. AÑADIDO: Registro en auditoría
        registrar_log(1, 'Admin', 'BAJA_LÓGICA', 'danger', f"El usuario '{nombre}' fue dado de baja del sistema.")
        
        return True
    except Exception as e:
        print("Error al dar de baja al usuario:", e)
        return False
    finally:
        conn.close()

def toggle_estado_usuario(id_usuario):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Activo, Nombre FROM Usuarios WHERE Id = ?", (id_usuario,))
        row = cursor.fetchone()
        if not row: return False
        
        estado_actual = row[0]
        nombre_usuario = row[1]
        nuevo_estado = 0 if estado_actual == 1 else 1 # 0 = Inactivo, 1 = Activo
        
        cursor.execute("UPDATE Usuarios SET Activo = ? WHERE Id = ?", (nuevo_estado, id_usuario))
        conn.commit()
        
        accion = 'DESACTIVAR_USUARIO' if nuevo_estado == 0 else 'ACTIVAR_USUARIO'
        gravedad = 'warning' if nuevo_estado == 0 else 'info'
        registrar_log(1, 'Admin', accion, gravedad, f"Se cambió el acceso del usuario '{nombre_usuario}'.")
        
        return True
    except Exception as e:
        print("Error al cambiar estado del usuario:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def eliminar_usuario(id_usuario):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Rescatamos el nombre del usuario para que el log quede bonito
        cursor.execute("SELECT Nombre FROM Usuarios WHERE Id = ?", (id_usuario,))
        row = cursor.fetchone()
        nombre = row[0] if row else f"ID {id_usuario}"

        # 2. LIMPIEZA PREVIA (CRÍTICO): 
        # Borramos al usuario de los equipos de los proyectos para que SQL Server nos deje borrarlo a él
        cursor.execute("DELETE FROM Asignaciones WHERE UsuarioId = ?", (id_usuario,))
        
        # Nota: Si en el futuro tienes una tabla de "Imputaciones" u "Horas", 
        # tendrías que poner otro DELETE aquí antes de borrar al usuario.

        # 3. BORRADO FÍSICO 100% REAL DE LA TABLA USUARIOS
        query = "DELETE FROM Usuarios WHERE Id = ?"
        cursor.execute(query, (id_usuario,))
        conn.commit()
        
        # 4. Registro en auditoría
        from services.auditoria_service import registrar_log
        registrar_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El usuario '{nombre}' y sus asignaciones fueron borrados físicamente de la base de datos.")
        
        return True
    except Exception as e:
        print("Error al borrar físicamente al usuario:", e)
        conn.rollback() # Deshacemos si algo falla a medias
        return False
    finally:
        conn.close()

def obtener_usuarios():
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        # IMPORTANTE: Seleccionar el Id
        cursor.execute("SELECT Id, Nombre, Rol, Sede, Activo, OidAzure FROM Usuarios") 
        columnas = [column[0] for column in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()