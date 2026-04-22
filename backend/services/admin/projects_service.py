from database.db import db
from models.projects import Projects
from models.clients import Clients
from models.assignments import Assignments
from models.users import Users
from models.time_entries import TimeEntries
from services.admin.audit_service import registrar_log
from sqlalchemy import text
from datetime import datetime
from errors import APIError

def generar_prefijo(nombre):
    """Genera un acrónimo de 1 a 3 letras basado en el nombre"""
    if not nombre: return "XXX"
    palabras = nombre.upper().replace("-", " ").replace("_", " ").split()
    if not palabras: return "XXX"
    
    if len(palabras) == 1:
        return palabras[0][:3]
    else:
        return "".join([p[0] for p in palabras])[:3]

def obtener_proyectos():
    proyectos = Projects.query.all()
    resultado = []
    for p in proyectos:
        equipo = []
        for a in p.asignaciones:
            if a.activo and a.usuario:
                equipo.append({"id": a.usuario.id, "nombre": a.usuario.nombre, "foto": getattr(a.usuario, 'foto', None)})
        
        resultado.append({
            "Id": p.id,
            "Nombre": p.nombre,
            "Cliente": p.cliente.nombre if p.cliente else "Sin Cliente",
            "Estado": p.estado,
            "Tipo": p.tipo,
            "Equipo": equipo
        })
    return resultado

def obtener_clientes():
    clientes = Clients.query.all()
    return [{"id": c.id, "nombre": c.nombre, "codigo": c.codigo} for c in clientes]

def crear_cliente(datos):
    nombre = datos.get('nombre')
    if not nombre: raise APIError("El nombre es obligatorio", status_code=400)
    if Clients.query.filter_by(nombre=nombre).first():
        raise APIError("El cliente ya existe", status_code=400)
        
    nuevo_cliente = Clients(nombre=nombre, estado=True, fecha_creacion=datetime.utcnow())
    db.session.add(nuevo_cliente)
    db.session.flush()
    
    prefijo = generar_prefijo(nuevo_cliente.nombre)
    nuevo_cliente.codigo = f"{prefijo}-{nuevo_cliente.id:03d}"

    db.session.commit()
    registrar_log('Crear Cliente', 'info', f"Se creó el cliente: {nombre} ({nuevo_cliente.codigo}).")
    return True

def actualizar_cliente(id_cliente, datos):
    cliente = Clients.query.get(id_cliente)
    if not cliente: raise APIError("Cliente no encontrado", status_code=404)
    
    cliente.nombre = datos.get('nombre', cliente.nombre)
    db.session.commit()
    registrar_log('Actualizar Cliente', 'info', f"Se actualizó el cliente ID {id_cliente}.")
    return True

def eliminar_cliente(id_cliente):
    cliente = Clients.query.get(id_cliente)
    if not cliente: raise APIError("Cliente no encontrado", status_code=404)
    
    proyectos_activos = Projects.query.filter_by(cliente_id=id_cliente).count()
    if proyectos_activos > 0:
        raise APIError("No puedes eliminar un cliente que tiene proyectos asignados", status_code=400)
        
    db.session.delete(cliente)
    db.session.commit()
    registrar_log('Eliminar Cliente', 'warning', f"Se eliminó el cliente ID {id_cliente}.")
    return True

def crear_proyecto(datos):
    nombre_cliente = datos.get('cliente', 'Cliente Genérico')
    cliente = Clients.query.filter_by(nombre=nombre_cliente).first()
    
    if not cliente:
        cliente = Clients(nombre=nombre_cliente, estado=True, fecha_creacion=datetime.utcnow())
        db.session.add(cliente)
        db.session.flush()
        prefijo_cli = generar_prefijo(cliente.nombre)
        cliente.codigo = f"{prefijo_cli}-{cliente.id:03d}"
        db.session.flush()

    nuevo_proyecto = Projects(
        cliente_id=cliente.id, nombre=datos.get('nombre'), estado=datos.get('estado', 'Activo'),
        tipo='Proyecto', fecha_creacion=datetime.utcnow()
    )
    db.session.add(nuevo_proyecto)
    db.session.flush() 

    if cliente.codigo and '-' in cliente.codigo:
        prefijo_proyecto = cliente.codigo.split('-')[0]
    else:
        prefijo_proyecto = generar_prefijo(cliente.nombre)

    nuevo_proyecto.codigo = f"{prefijo_proyecto}-P{nuevo_proyecto.id:03d}"

    usuarios_ids = datos.get('usuarios_ids', [])
    for u_id in usuarios_ids:
        nueva_asignacion = Assignments(proyecto_id=nuevo_proyecto.id, usuario_id=u_id, activo=True, fecha_asignacion=datetime.utcnow())
        db.session.add(nueva_asignacion)

    db.session.commit()
    registrar_log('Crear Proyecto', 'info', f"Se creó el proyecto: {datos.get('nombre')} ({nuevo_proyecto.codigo}).")
    return True

def actualizar_proyecto(id_proyecto, datos):
    proyecto = Projects.query.get(id_proyecto)
    if not proyecto: raise APIError("Proyecto no encontrado", status_code=404)

    nombre_cliente = datos.get('cliente', 'Cliente Genérico')
    cliente = Clients.query.filter_by(nombre=nombre_cliente).first()
    if not cliente:
        cliente = Clients(nombre=nombre_cliente, estado=True, fecha_creacion=datetime.utcnow())
        db.session.add(cliente)
        db.session.flush()
        prefijo_cli = generar_prefijo(cliente.nombre)
        cliente.codigo = f"{prefijo_cli}-{cliente.id:03d}"

    proyecto.nombre = datos.get('nombre')
    proyecto.estado = datos.get('estado')
    proyecto.cliente_id = cliente.id

    Assignments.query.filter_by(proyecto_id=id_proyecto).delete()
    
    usuarios_ids = datos.get('usuarios_ids', [])
    for u_id in usuarios_ids:
        nueva_asignacion = Assignments(proyecto_id=id_proyecto, usuario_id=u_id, activo=True, fecha_asignacion=datetime.utcnow())
        db.session.add(nueva_asignacion)
        
    db.session.commit()
    registrar_log('Actualizar Proyecto', 'info', f"Se actualizó el proyecto: {datos.get('nombre')} y su equipo.")
    return True

def eliminar_proyecto_fisico(id_proyecto):
    proyecto = Projects.query.get(id_proyecto)
    if not proyecto: raise APIError("Proyecto no encontrado", status_code=404)
    
    imputaciones_count = TimeEntries.query.filter_by(proyecto_id=id_proyecto).count()
    
    if imputaciones_count > 0:
        raise APIError(
            f"El proyecto '{proyecto.nombre}' ya tiene {imputaciones_count} registros de horas. "
            "No se puede eliminar físicamente para no alterar el histórico. Por favor, usa la opción Cerrar o Desactivar.", 
            status_code=400
        )

    Assignments.query.filter_by(proyecto_id=id_proyecto).delete()
    db.session.delete(proyecto)
    db.session.commit()
    
    registrar_log('Borrado Físico', 'danger', f"El proyecto '{proyecto.nombre}' con ID {id_proyecto} fue eliminado de la BD.")
    return True

def cambiar_estado_proyecto(id_proyecto, nuevo_estado):
    proyecto = Projects.query.get(id_proyecto)
    if not proyecto: raise APIError("Proyecto no encontrado", status_code=404)
    
    proyecto.estado = nuevo_estado
    proyecto.fecha_desactivacion = datetime.utcnow() if nuevo_estado in ['Cerrado', 'Inactivo'] else None
        
    db.session.commit()
    registrar_log('Cambio Estado', 'warning' if nuevo_estado != 'Activo' else 'info', f"El proyecto '{proyecto.nombre}' ha pasado a estado: {nuevo_estado}.")
    return True