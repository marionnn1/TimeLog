from database.db import db
from models.projects import Projects
from models.clients import Clients
from models.users import Users
from models.assignments import Assignments
from datetime import datetime
import random

def get_all_projects_data():
    try:
        proyectos_db = Projects.query.filter(Projects.fecha_desactivacion.is_(None)).all()
        proyectos = []
        for p in proyectos_db:
            equipo = []
            for a in p.asignaciones:
                if a.activo and a.fecha_desactivacion is None and a.usuario:
                    nombres = a.usuario.nombre.split() if a.usuario.nombre else []
                    iniciales = "".join([n[0] for n in nombres[:2]]).upper() if nombres else "XX"
                    equipo.append({"id": a.usuario.id, "nombre": a.usuario.nombre, "rol": a.usuario.rol, "iniciales": iniciales})

            proyectos.append({
                "id": p.id,
                "nombre": p.nombre,
                "cliente": p.cliente.nombre if p.cliente else "Sin Cliente",
                "idCliente": (p.cliente.codigo if p.cliente and p.cliente.codigo else ""),
                "codigo": p.codigo,
                "estado": True if p.estado == "Activo" else False,
                "equipo": equipo,
            })

        usuarios_db = Users.query.filter_by(activo=True).all()
        usuarios = []
        for u in usuarios_db:
            nombres = u.nombre.split() if u.nombre else []
            iniciales = "".join([n[0] for n in nombres[:2]]).upper() if nombres else "XX"
            usuarios.append({"id": u.id, "nombre": u.nombre, "rol": u.rol, "iniciales": iniciales})

        clientes_db = Clients.query.all()
        clientes_list = [{"id": c.id, "nombre": c.nombre, "codigo": c.codigo} for c in clientes_db]

        return {"proyectos": proyectos, "usuariosDisponibles": usuarios, "clientesDisponibles": clientes_list}, 200

    except Exception as e:
        print(f"Error en get_all_projects_data: {e}")
        return {"error": str(e)}, 500

def save_client(data):
    try:
        nombre = data.get("nombre")
        codigo = data.get("codigo")
        if not nombre:
            return {"error": "El nombre del cliente es obligatorio"}, 400

        existente = Clients.query.filter_by(nombre=nombre).first()
        if existente:
            return {"error": "Este cliente ya existe en la base de datos"}, 400

        nuevo_cliente = Clients(nombre=nombre, codigo=codigo)
        db.session.add(nuevo_cliente)
        db.session.commit()
        return {"message": "Cliente creado correctamente"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def update_client(client_id, data):
    try:
        cliente = Clients.query.get(client_id)
        if not cliente:
            return {"error": "Cliente no encontrado"}, 404

        cliente.nombre = data.get("nombre", cliente.nombre)
        cliente.codigo = data.get("codigo", cliente.codigo)
        db.session.commit()
        return {"message": "Cliente actualizado correctamente"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def delete_client(client_id):
    try:
        cliente = Clients.query.get(client_id)
        if not cliente:
            return {"error": "Cliente no encontrado"}, 404

        proyectos_activos = Projects.query.filter_by(cliente_id=client_id).count()
        if proyectos_activos > 0:
            return {"error": "No puedes eliminar un cliente que tiene proyectos asignados"}, 400

        db.session.delete(cliente)
        db.session.commit()
        return {"message": "Cliente eliminado correctamente"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def save_project(data, project_id=None):
    try:
        nombre = data.get("nombre")
        cliente_nombre = data.get("cliente")
        cliente_codigo = data.get("idCliente")
        estado_str = "Activo" if data.get("estado") else "Cerrado"
        codigo = data.get("codigo")
        usuarios_ids = data.get("usuarios_ids", []) 

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
            
            Assignments.query.filter_by(proyecto_id=project_id).delete()
            for u_id in usuarios_ids:
                nueva_asignacion = Assignments(proyecto_id=project_id, usuario_id=u_id, activo=True, fecha_asignacion=datetime.utcnow())
                db.session.add(nueva_asignacion)
        else:
            if not codigo:
                codigo = f"PRJ-{random.randint(100, 999)}"

            nuevo_proyecto = Projects(
                nombre=nombre, cliente_id=cliente.id, estado=estado_str, codigo=codigo
            )
            db.session.add(nuevo_proyecto)
            db.session.flush()
            
            for u_id in usuarios_ids:
                nueva_asignacion = Assignments(proyecto_id=nuevo_proyecto.id, usuario_id=u_id, activo=True, fecha_asignacion=datetime.utcnow())
                db.session.add(nueva_asignacion)

        db.session.commit()
        return {"message": "Proyecto guardado correctamente"}, 200

    except Exception as e:
        db.session.rollback()
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
        return {"error": str(e)}, 500

def assign_user(proyecto_id, usuario_id):
    try:
        asignacion_existente = Assignments.query.filter_by(
            proyecto_id=proyecto_id, usuario_id=usuario_id, activo=True
        ).first()

        if asignacion_existente:
            return {"error": "El usuario ya está en este proyecto"}, 400

        nueva_asignacion = Assignments(
            proyecto_id=proyecto_id, usuario_id=usuario_id, activo=True, fecha_asignacion=datetime.utcnow()
        )
        db.session.add(nueva_asignacion)
        db.session.commit()
        return {"message": "Usuario asignado"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    
def unassign_user(proyecto_id, usuario_id):
    try:
        asignacion = Assignments.query.filter_by(
            proyecto_id=proyecto_id, usuario_id=usuario_id, activo=True
        ).first()

        if not asignacion:
            return {"error": "El usuario no está activo en este proyecto"}, 404

        asignacion.activo = False
        asignacion.fecha_desactivacion = datetime.utcnow()
        db.session.commit()
        return {"message": "Usuario quitado del proyecto"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500