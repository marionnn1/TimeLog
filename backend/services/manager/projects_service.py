from database.connection import get_db_connection
import random

def get_all_projects_data():
    conn = get_db_connection()
    if not conn: return {"error": "DB error"}, 500

    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.Id, p.Nombre, p.Codigo, p.Estado, c.Nombre as Cliente, c.Codigo as IdCliente
            FROM Proyectos p
            LEFT JOIN Clientes c ON p.ClienteId = c.Id
            WHERE p.FechaDesactivacion IS NULL
        """)
        
        projects = []
        for row in cursor.fetchall():
            projects.append({
                "id": row.Id,
                "name": row.Nombre,
                "client": row.Cliente or "Sin Cliente",
                "clientId": row.IdCliente or "",
                "code": row.Codigo,
                "status": True if row.Estado == 'Activo' else False,
                "team": []
            })

        cursor.execute("""
            SELECT a.ProyectoId, u.Id, u.Nombre, u.Rol
            FROM Asignaciones a
            JOIN Usuarios u ON a.UsuarioId = u.Id
            WHERE a.Activo = 1 AND a.FechaDesactivacion IS NULL
        """)
        
        assignments = cursor.fetchall()
        for p in projects:
            p["team"] = [{
                "id": a.Id,
                "name": a.Nombre,
                "role": a.Rol,
                "initials": "".join([n[0] for n in a.Nombre.split()[:2]]).upper()
            } for a in assignments if a.ProyectoId == p["id"]]

        cursor.execute("SELECT Id, Nombre, Rol FROM Usuarios WHERE Activo = 1")
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row.Id,
                "name": row.Nombre,
                "role": row.Rol,
                "initials": "".join([n[0] for n in row.Nombre.split()[:2]]).upper()
            })

        conn.close()
        return {"projects": projects, "availableUsers": users}, 200

    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500


def save_project(data, project_id=None):
    conn = get_db_connection()
    if not conn: return {"error": "DB error"}, 500

    try:
        cursor = conn.cursor()
        name = data.get('name')
        client_name = data.get('client')
        client_code = data.get('clientId')
        status_str = 'Activo' if data.get('status') else 'Cerrado'
        code = data.get('code')

        cursor.execute("SELECT Id FROM Clientes WHERE Nombre = ?", (client_name,))
        client = cursor.fetchone()
        
        if client:
            client_id = client.Id

            if client_code:
                cursor.execute("UPDATE Clientes SET Codigo = ? WHERE Id = ?", (client_code, client_id))
        else:
            cursor.execute("INSERT INTO Clientes (Nombre, Codigo) OUTPUT INSERTED.Id VALUES (?, ?)", 
                           (client_name, client_code))
            client_id = cursor.fetchone().Id

        if project_id:
            cursor.execute("""
                UPDATE Proyectos 
                SET Nombre = ?, ClienteId = ?, Estado = ?, Codigo = ?
                WHERE Id = ?
            """, (name, client_id, status_str, code, project_id))
        else:
            if not code: code = f"PRJ-{random.randint(100, 999)}"
            cursor.execute("""
                INSERT INTO Proyectos (Nombre, ClienteId, Estado, Codigo)
                VALUES (?, ?, ?, ?)
            """, (name, client_id, status_str, code))

        conn.commit()
        conn.close()
        return {"message": "Project saved successfully"}, 200

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
        return {"message": "Project deleted"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500


def assign_user(project_id, user_id):
    conn = get_db_connection()
    if not conn: return {"error": "DB error"}, 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM Asignaciones WHERE ProyectoId = ? AND UsuarioId = ?", (project_id, user_id))
        if cursor.fetchone():
            return {"error": "The user is already assigned to this project"}, 400
            
        cursor.execute("INSERT INTO Asignaciones (ProyectoId, UsuarioId) VALUES (?, ?)", (project_id, user_id))
        conn.commit()
        conn.close()
        return {"message": "User assigned"}, 200
    except Exception as e:
        if conn: conn.close()
        return {"error": str(e)}, 500