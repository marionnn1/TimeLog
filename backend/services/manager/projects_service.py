# backend/services/manager/projects_service.py
from database.db import db
from models.projects import Projects
from models.clients import Clients
from models.users import Users
from models.assignments import Assignments
from datetime import datetime
import random


def get_all_projects_data():
    try:
        # 1. Obtener proyectos activos (aquellos sin fecha de desactivación)
        proyectos_db = Projects.query.filter(
            Projects.fecha_desactivacion.is_(None)
        ).all()

        proyectos = []
        for p in proyectos_db:
            equipo = []

            # 2. Aprovechamos la relación para extraer el equipo asignado y activo
            for a in p.asignaciones:
                if a.activo and a.fecha_desactivacion is None and a.usuario:
                    nombres = a.usuario.nombre.split() if a.usuario.nombre else []
                    iniciales = (
                        "".join([n[0] for n in nombres[:2]]).upper()
                        if nombres
                        else "XX"
                    )

                    equipo.append(
                        {
                            "id": a.usuario.id,
                            "nombre": a.usuario.nombre,
                            "rol": a.usuario.rol,
                            "iniciales": iniciales,
                        }
                    )

            proyectos.append(
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "cliente": p.cliente.nombre if p.cliente else "Sin Cliente",
                    "idCliente": (
                        p.cliente.codigo if p.cliente and p.cliente.codigo else ""
                    ),
                    "codigo": p.codigo,
                    "estado": True if p.estado == "Activo" else False,
                    "equipo": equipo,
                }
            )

        # 3. Obtener usuarios disponibles para el desplegable de asignar
        usuarios_db = Users.query.filter_by(activo=True).all()
        usuarios = []
        for u in usuarios_db:
            nombres = u.nombre.split() if u.nombre else []
            iniciales = (
                "".join([n[0] for n in nombres[:2]]).upper() if nombres else "XX"
            )

            usuarios.append(
                {"id": u.id, "nombre": u.nombre, "rol": u.rol, "iniciales": iniciales}
            )

        return {"proyectos": proyectos, "usuariosDisponibles": usuarios}, 200

    except Exception as e:
        print(f"Error en get_all_projects_data: {e}")
        return {"error": str(e)}, 500


def save_project(data, project_id=None):
    try:
        nombre = data.get("nombre")
        cliente_nombre = data.get("cliente")
        cliente_codigo = data.get("idCliente")
        estado_str = "Activo" if data.get("estado") else "Cerrado"
        codigo = data.get("codigo")

        cliente = Clients.query.filter_by(nombre=cliente_nombre).first()

        if cliente:
            if cliente_codigo:
                cliente.codigo = cliente_codigo
        else:
            cliente = Clients(nombre=cliente_nombre, codigo=cliente_codigo)
            db.session.add(cliente)
            db.session.flush()

        if project_id:
            proyecto = Projects.query.get(project_id)
            if not proyecto:
                return {"error": "Proyecto no encontrado"}, 404

            proyecto.nombre = nombre
            proyecto.cliente_id = cliente.id
            proyecto.estado = estado_str
            proyecto.codigo = codigo
        else:
            if not codigo:
                codigo = f"PRJ-{random.randint(100, 999)}"

            nuevo_proyecto = Projects(
                nombre=nombre, cliente_id=cliente.id, estado=estado_str, codigo=codigo
            )
            db.session.add(nuevo_proyecto)

        db.session.commit()
        return {"message": "Proyecto guardado correctamente"}, 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en save_project: {e}")
        return {"error": str(e)}, 500


def soft_delete_project(project_id):
    try:
        proyecto = Projects.query.get(project_id)
        if not proyecto:
            return {"error": "Proyecto no encontrado"}, 404

        proyecto.estado = "Cerrado"
        proyecto.fecha_desactivacion = datetime.utcnow()
        db.session.commit()

        return {"message": "Proyecto eliminado"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error en soft_delete_project: {e}")
        return {"error": str(e)}, 500


def assign_user(proyecto_id, usuario_id):
    try:
        asignacion_existente = Assignments.query.filter_by(
            proyecto_id=proyecto_id, usuario_id=usuario_id, activo=True
        ).first()

        if asignacion_existente:
            return {"error": "El usuario ya está en este proyecto"}, 400

        nueva_asignacion = Assignments(
            proyecto_id=proyecto_id,
            usuario_id=usuario_id,
            activo=True,
            fecha_asignacion=datetime.utcnow(),
        )
        db.session.add(nueva_asignacion)
        db.session.commit()

        return {"message": "Usuario asignado"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error en assign_user: {e}")
        return {"error": str(e)}, 500
