from database.db import db
from models.projects import Projects
from models.clients import Clients
from models.assignments import Assignments
from models.users import Users
from TimeLog.backend.services.admin.audit_service import register_log
from sqlalchemy import text
from datetime import datetime

def get_projects():
    try:
        proyectos = Projects.query.all()
        
        resultado = []
        for p in proyectos:
            equipo = []
            for a in p.asignaciones:
                if a.activo and a.usuario:
                    equipo.append({"id": a.usuario.id, "name": a.usuario.nombre})
            
            resultado.append({
                "id": p.id,
                "name": p.nombre,
                "client": p.cliente.nombre if p.cliente else "Sin Cliente",
                "status": p.estado,
                "type": p.tipo,
                "team": equipo
            })
        return resultado
    except Exception as e:
        print(f"Error al obtener proyectos: {e}")
        return None

def create_project(data):
    try:
        nombre_cliente = data.get('client', 'Cliente Genérico')
        cliente = Clients.query.filter_by(nombre=nombre_cliente).first()
        
        if not cliente:
            cliente = Clients(nombre=nombre_cliente, estado=True, fecha_creacion=datetime.utcnow())
            db.session.add(cliente)
            db.session.flush()

        nuevo_proyecto = Projects(
            cliente_id=cliente.id,
            nombre=data.get('name'),
            estado=data.get('status', 'Activo'),
            tipo='Proyecto',
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(nuevo_proyecto)
        db.session.flush() 

        usuarios_ids = data.get('user_ids', [])
        for u_id in usuarios_ids:
            nueva_asignacion = Assignments(
                proyecto_id=nuevo_proyecto.id,
                usuario_id=u_id,
                activo=True,
                fecha_asignacion=datetime.utcnow()
            )
            db.session.add(nueva_asignacion)

        db.session.commit()
        register_log(1, 'Admin', 'CREAR_PROYECTO', 'info', f"Se creó el proyecto: {data.get('name')}.")
        return True
    except Exception as e:
        print(f"Error al crear proyecto: {e}")
        db.session.rollback()
        return False

def update_project(project_id, data):
    try:
        proyecto = Projects.query.get(project_id)
        if not proyecto: return False

        nombre_cliente = data.get('client', 'Cliente Genérico')
        cliente = Clients.query.filter_by(nombre=nombre_cliente).first()
        
        if not cliente:
            cliente = Clients(nombre=nombre_cliente, estado=True, fecha_creacion=datetime.utcnow())
            db.session.add(cliente)
            db.session.flush()

        proyecto.nombre = data.get('name')
        proyecto.estado = data.get('status')
        proyecto.cliente_id = cliente.id

        Assignments.query.filter_by(proyecto_id=project_id).delete()
        
        usuarios_ids = data.get('user_ids', [])
        for u_id in usuarios_ids:
            nueva_asignacion = Assignments(
                proyecto_id=project_id,
                usuario_id=u_id,
                activo=True,
                fecha_asignacion=datetime.utcnow()
            )
            db.session.add(nueva_asignacion)
            
        db.session.commit()
        register_log(1, 'Admin', 'ACTUALIZAR_PROYECTO', 'info', f"Se actualizó el proyecto: {data.get('name')} y su equipo.")
        return True
    except Exception as e:
        print(f"Error al actualizar proyecto: {e}")
        db.session.rollback()
        return False

def close_project(project_id):
    try:
        proyecto = Projects.query.get(project_id)
        if not proyecto: return False
        
        proyecto.estado = 'Cerrado'
        proyecto.fecha_desactivacion = datetime.utcnow()
        db.session.commit()
        
        register_log(1, 'Admin', 'CERRAR_PROYECTO', 'warning', f"Se ha cerrado el proyecto con ID: {project_id}.")
        return True
    except Exception as e:
        print(f"Error al cerrar proyecto: {e}")
        db.session.rollback()
        return False

def hard_delete_project(project_id):
    try:
        proyecto = Projects.query.get(project_id)
        if not proyecto: return False
        
        db.session.execute(text("DELETE FROM Imputaciones WHERE ProyectoId = :id"), {"id": project_id})
        
        Assignments.query.filter_by(proyecto_id=project_id).delete()
        
        db.session.delete(proyecto)
        db.session.commit()
        
        register_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El proyecto con ID {project_id} fue eliminado de la base de datos.")
        return True
    except Exception as e:
        print(f"Error al eliminar físicamente el proyecto: {e}")
        db.session.rollback()
        return False

def toggle_project_status(project_id):
    try:
        proyecto = Projects.query.get(project_id)
        if not proyecto: return False
        
        nuevo_estado = 'Cerrado' if proyecto.estado == 'Activo' else 'Activo'
        proyecto.estado = nuevo_estado
        
        if nuevo_estado == 'Cerrado':
            proyecto.fecha_desactivacion = datetime.utcnow()
        else:
            proyecto.fecha_desactivacion = None
            
        db.session.commit()
        
        register_log(1, 'Admin', 'CAMBIO_ESTADO', 'warning' if nuevo_estado == 'Cerrado' else 'info', f"El proyecto '{proyecto.nombre}' ha pasado a estado: {nuevo_estado}.")
        return True
    except Exception as e:
        print(f"Error al cambiar estado del proyecto: {e}")
        db.session.rollback()
        return False