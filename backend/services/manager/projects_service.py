from database.db import db
from models.projects import Projects
from models.clients import Clients
from models.users import Users
from models.assignments import Assignments
from datetime import datetime
import random


def get_all_projects_data():
    try:
        projects_db = Projects.query.filter(
            Projects.fecha_desactivacion.is_(None)
        ).all()

        projects = []
        for p in projects_db:
            team = []

            for a in p.asignaciones:
                if a.activo and a.fecha_desactivacion is None and a.usuario:
                    names = a.usuario.nombre.split() if a.usuario.nombre else []
                    initials = (
                        "".join([n[0] for n in names[:2]]).upper()
                        if names
                        else "XX"
                    )

                    team.append(
                        {
                            "id": a.usuario.id,
                            "name": a.usuario.nombre,
                            "role": a.usuario.rol,
                            "initials": initials,
                        }
                    )

            projects.append(
                {
                    "id": p.id,
                    "name": p.nombre,
                    "client": p.cliente.nombre if p.cliente else "Sin Cliente",
                    "clientId": (
                        p.cliente.codigo if p.cliente and p.cliente.codigo else ""
                    ),
                    "code": p.codigo,
                    "status": True if p.estado == "Activo" else False,
                    "team": team,
                }
            )

        users_db = Users.query.filter_by(activo=True).all()
        available_users = []
        for u in users_db:
            names = u.nombre.split() if u.nombre else []
            initials = (
                "".join([n[0] for n in names[:2]]).upper() if names else "XX"
            )

            available_users.append(
                {"id": u.id, "name": u.nombre, "role": u.rol, "initials": initials}
            )

        return {"projects": projects, "availableUsers": available_users}, 200

    except Exception as e:
        print(f"Error en get_all_projects_data: {e}")
        return {"error": str(e)}, 500


def save_project(data, project_id=None):
    try:
        name = data.get("name")
        client_name = data.get("client")
        client_code = data.get("clientId")
        status_str = "Activo" if data.get("status") else "Cerrado"
        code = data.get("code")

        client = Clients.query.filter_by(nombre=client_name).first()

        if client:
            if client_code:
                client.codigo = client_code
        else:
            client = Clients(nombre=client_name, codigo=client_code)
            db.session.add(client)
            db.session.flush()

        if project_id:
            project = Projects.query.get(project_id)
            if not project:
                return {"error": "Project not found"}, 404

            project.nombre = name
            project.cliente_id = client.id
            project.estado = status_str
            project.codigo = code
        else:
            if not code:
                code = f"PRJ-{random.randint(100, 999)}"

            new_project = Projects(
                nombre=name, cliente_id=client.id, estado=status_str, codigo=code
            )
            db.session.add(new_project)

        db.session.commit()
        return {"message": "Project saved successfully"}, 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en save_project: {e}")
        return {"error": str(e)}, 500


def soft_delete_project(project_id):
    try:
        project = Projects.query.get(project_id)
        if not project:
            return {"error": "Project not found"}, 404

        project.estado = "Cerrado"
        project.fecha_desactivacion = datetime.utcnow()
        db.session.commit()

        return {"message": "Project deleted"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error en soft_delete_project: {e}")
        return {"error": str(e)}, 500


def assign_user(project_id, user_id):
    try:
        existing_assignment = Assignments.query.filter_by(
            proyecto_id=project_id, usuario_id=user_id, activo=True
        ).first()

        if existing_assignment:
            return {"error": "The user is already assigned to this project"}, 400

        new_assignment = Assignments(
            proyecto_id=project_id,
            usuario_id=user_id,
            activo=True,
            fecha_asignacion=datetime.utcnow(),
        )
        db.session.add(new_assignment)
        db.session.commit()

        return {"message": "User assigned"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error en assign_user: {e}")
        return {"error": str(e)}, 500