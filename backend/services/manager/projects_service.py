from database.db import db
from models.projects import Projects
from models.clients import Clients
from models.users import Users
from models.assignments import Assignments
from models.time_entries import TimeEntries
from datetime import datetime
import random
from errors import APIError

def get_all_projects_data():
    proyectos_db = Projects.query.all()
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
            "estado": p.estado,
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

    return {"proyectos": proyectos, "usuariosDisponibles": usuarios, "clientesDisponibles": clientes_list}

def save_client(data):
    nombre = data.get("nombre")
    codigo = data.get("codigo")
    if not nombre: raise APIError("El nombre del cliente es obligatorio", status_code=400)

    existente = Clients.query.filter_by(nombre=nombre).first()
    if existente: raise APIError("Este cliente ya existe en la base de datos", status_code=400)

    nuevo_cliente = Clients(nombre=nombre, codigo=codigo)
    db.session.add(nuevo_cliente)
    db.session.commit()
    return True

def update_client(client_id, data):
    cliente = Clients.query.get(client_id)
    if not cliente: raise APIError("Cliente no encontrado", status_code=404)

    cliente.nombre = data.get("nombre", cliente.nombre)
    cliente.codigo = data.get("codigo", cliente.codigo)
    db.session.commit()
    return True

def delete_client(client_id):
    cliente = Clients.query.get(client_id)
    if not cliente: raise APIError("Cliente no encontrado", status_code=404)

    proyectos_activos = Projects.query.filter_by(cliente_id=client_id).count()
    if proyectos_activos > 0:
        raise APIError("No puedes eliminar un cliente que tiene proyectos asignados", status_code=400)

    db.session.delete(cliente)
    db.session.commit()
    return True

def save_project(data, project_id=None):
    nombre = data.get("nombre")
    cliente_nombre = data.get("cliente")
    cliente_codigo = data.get("idCliente")
    estado_str = data.get("estado", "Activo")
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
        if not proyecto: raise APIError("Proyecto no encontrado", status_code=404)

        proyecto.nombre = nombre
        proyecto.cliente_id = cliente.id
        proyecto.estado = estado_str
        proyecto.codigo = codigo
        
        Assignments.query.filter_by(proyecto_id=project_id).delete()
        for u_id in usuarios_ids:
            nueva_asignacion = Assignments(proyecto_id=project_id, usuario_id=u_id, activo=True, fecha_asignacion=datetime.utcnow())
            db.session.add(nueva_asignacion)
    else:
        if not codigo: codigo = f"PRJ-{random.randint(100, 999)}"

        nuevo_proyecto = Projects(nombre=nombre, cliente_id=cliente.id, estado=estado_str, codigo=codigo)
        db.session.add(nuevo_proyecto)
        db.session.flush()
        
        for u_id in usuarios_ids:
            nueva_asignacion = Assignments(proyecto_id=nuevo_proyecto.id, usuario_id=u_id, activo=True, fecha_asignacion=datetime.utcnow())
            db.session.add(nueva_asignacion)

    db.session.commit()
    return True

def eliminar_proyecto_fisico(project_id):
    proyecto = Projects.query.get(project_id)
    if not proyecto: raise APIError("Proyecto no encontrado", status_code=404)

    imputaciones_count = TimeEntries.query.filter_by(proyecto_id=project_id).count()
    
    if imputaciones_count > 0:
        raise APIError(
            f"El proyecto '{proyecto.nombre}' ya tiene {imputaciones_count} registros de horas. "
            "No se puede eliminar físicamente para no alterar el histórico. Por favor, usa la opción Cerrar o Desactivar.", 
            status_code=400
        )

    Assignments.query.filter_by(proyecto_id=project_id).delete()
    db.session.delete(proyecto)
    db.session.commit()
    return True

def cambiar_estado_proyecto(project_id, nuevo_estado):
    proyecto = Projects.query.get(project_id)
    if not proyecto: raise APIError("Proyecto no encontrado", status_code=404)
    
    proyecto.estado = nuevo_estado
    proyecto.fecha_desactivacion = datetime.utcnow() if nuevo_estado in ['Cerrado', 'Inactivo'] else None
        
    db.session.commit()
    return True

def assign_user(proyecto_id, usuario_id):
    asignacion_existente = Assignments.query.filter_by(
        proyecto_id=proyecto_id, usuario_id=usuario_id, activo=True
    ).first()

    if asignacion_existente: raise APIError("El usuario ya está en este proyecto", status_code=400)

    nueva_asignacion = Assignments(proyecto_id=proyecto_id, usuario_id=usuario_id, activo=True, fecha_asignacion=datetime.utcnow())
    db.session.add(nueva_asignacion)
    db.session.commit()
    return True
    
def unassign_user(proyecto_id, usuario_id):
    asignacion = Assignments.query.filter_by(proyecto_id=proyecto_id, usuario_id=usuario_id, activo=True).first()

    if not asignacion: raise APIError("El usuario no está activo en este proyecto", status_code=404)

    asignacion.activo = False
    asignacion.fecha_desactivacion = datetime.utcnow()
    db.session.commit()
    return True