from database.connection import get_db_connection
import random

def get_all_projects_data():
    conn = get_db_connection()
    if not conn: return {"error": "DB error"}, 500

    try:
        cursor = conn.cursor()
        
        # 1. Obtener proyectos activos con sus clientes
        cursor.execute("""
            SELECT p.Id, p.Nombre, p.Codigo, p.Estado, c.Nombre as Cliente, c.Codigo as IdCliente
            FROM Proyectos p
            LEFT JOIN Clientes c ON p.ClienteId = c.Id
            WHERE p.FechaDesactivacion IS NULL
        """)
        
        proyectos = []
        for row in cursor.fetchall():
            proyectos.append({
                "id": row.Id,
                "nombre": row.Nombre,
                "cliente": row.Cliente or "Sin Cliente",
                "idCliente": row.IdCliente or "",
                "codigo": row.Codigo,
                "estado": True if row.Estado == 'Activo' else False,
                "equipo": []
            })

        # 2. Obtener las asignaciones de equipo para cada proyecto
        cursor.execute("""
            SELECT a.ProyectoId, u.Id, u.Nombre, u.Rol
            FROM Asignaciones a
            JOIN Usuarios u ON a.UsuarioId = u.Id
            WHERE a.Activo = 1 AND a.FechaDesactivacion IS NULL
        """)
        
        asignaciones = cursor.fetchall()
        for p in proyectos:
            p["equipo"] = [{
                "id": a.Id,
                "nombre": a.Nombre,
                "rol": a.Rol,
                "iniciales": "".join([n[0] for n in a.Nombre.split()[:2]]).upper()
            } for a in asignaciones if a.ProyectoId == p["id"]]

        # 3. Obtener usuarios disponibles para el desplegable de asignar
        cursor.execute("SELECT Id, Nombre, Rol FROM Usuarios WHERE Activo = 1")
        usuarios = []
        for row in cursor.fetchall():
            usuarios.append({
                "id": row.Id,
                "nombre": row.Nombre,
                "rol": row.Rol,
                "iniciales": "".join([n[0] for n in row.Nombre.split()[:2]]).upper()
            })

        conn.close()
        return {"proyectos": proyectos, "usuariosDisponibles": usuarios}, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500


def save_project(data, project_id=None):
    conn = get_db_connection()
    if not conn: return {"error": "DB error"}, 500

    try:
        cursor = conn.cursor()
        nombre = data.get('nombre')
        cliente_nombre = data.get('cliente')
        cliente_codigo = data.get('idCliente')
        estado_str = 'Activo' if data.get('estado') else 'Cerrado'
        codigo = data.get('codigo')

        # Gestionar el Cliente (Buscar si existe, si no, crearlo)
        cursor.execute("SELECT Id FROM Clientes WHERE Nombre = ?", (cliente_nombre,))
        cliente = cursor.fetchone()
        
        if cliente:
            cliente_id = cliente.Id
        else:
            cursor.execute("INSERT INTO Clientes (Nombre, Codigo) OUTPUT INSERTED.Id VALUES (?, ?)", 
                           (cliente_nombre, cliente_codigo))
            cliente_id = cursor.fetchone().Id

        if project_id:
            # Actualizar
            cursor.execute("""
                UPDATE Proyectos 
                SET Nombre = ?, ClienteId = ?, Estado = ?, Codigo = ?
                WHERE Id = ?
            """, (nombre, cliente_id, estado_str, codigo, project_id))
        else:
            # Crear nuevo (generamos un código si viene vacío)
            if not codigo: codigo = f"PRJ-{random.randint(100, 999)}"
            cursor.execute("""
                INSERT INTO Proyectos (Nombre, ClienteId, Estado, Codigo)
                VALUES (?, ?, ?, ?)
            """, (nombre, cliente_id, estado_str, codigo))

        conn.commit()
        conn.close()
        return {"message": "Proyecto guardado correctamente"}, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500

def soft_delete_project(project_id):
    conn = get_db_connection()
    if not conn: return {"error": "DB error"}, 500
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Proyectos SET FechaDesactivacion = GETDATE(), Estado = 'Cerrado' WHERE Id = ?", (project_id,))
        conn.commit()
        conn.close()
        return {"message": "Proyecto eliminado"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500

def assign_user(proyecto_id, usuario_id):
    conn = get_db_connection()
    if not conn: return {"error": "DB error"}, 500
    try:
        cursor = conn.cursor()
        # Verificar si ya está asignado
        cursor.execute("SELECT Id FROM Asignaciones WHERE ProyectoId = ? AND UsuarioId = ?", (proyecto_id, usuario_id))
        if cursor.fetchone():
            return {"error": "El usuario ya está en este proyecto"}, 400
            
        cursor.execute("INSERT INTO Asignaciones (ProyectoId, UsuarioId) VALUES (?, ?)", (proyecto_id, usuario_id))
        conn.commit()
        conn.close()
        return {"message": "Usuario asignado"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500