from database.connection import get_db_connection

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
        # BAJA LÓGICA: No lo borramos de la tabla, solo lo marcamos como inactivo y registramos la fecha.
        query = "UPDATE Usuarios SET Activo = 0, FechaDesactivacion = GETDATE() WHERE Id = ?"
        cursor.execute(query, (id_usuario,))
        conn.commit()
        return True
    except Exception as e:
        print("Error al dar de baja al usuario:", e)
        return False
    finally:
        conn.close()