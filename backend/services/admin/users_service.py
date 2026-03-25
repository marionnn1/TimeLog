from database.db import db
from models.users import Users
from services.admin.audit_service import registrar_log
from datetime import datetime
from utils.exceptions import APIError

def obtener_usuarios():
    usuarios = Users.query.all()
    return [user.to_dict() for user in usuarios]

def crear_usuario(datos):
    if not datos.get('nombre') or not datos.get('email'):
        raise APIError("Faltan datos obligatorios (nombre o email)", 400)
        
    existente = Users.query.filter_by(oid_azure=datos['email']).first()
    if existente:
        raise APIError(f"El usuario con email {datos['email']} ya existe", 400)

    nuevo_usuario = Users(
        nombre=datos['nombre'],
        oid_azure=datos['email'],
        rol=datos.get('rol', 'Tecnico'),
        sede=datos.get('sede'),
        activo=True,
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    registrar_log(1, 'Admin', 'CREAR_USUARIO', 'info', f"Se ha dado de alta al usuario: {datos['nombre']}.")
    return True

def actualizar_usuario(id_usuario, datos):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", 404)
        
    usuario.nombre = datos.get('nombre', usuario.nombre)
    usuario.oid_azure = datos.get('email', usuario.oid_azure)
    usuario.rol = datos.get('rol', usuario.rol)
    usuario.sede = datos.get('sede', usuario.sede)
    
    db.session.commit()
    registrar_log(1, 'Admin', 'ACTUALIZAR_USUARIO', 'info', f"Se actualizaron los datos del usuario: {usuario.nombre}.")
    return True

def eliminar_usuario(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", 404)

    nombre = usuario.nombre
    usuario.activo = False
    usuario.fecha_desactivacion = datetime.utcnow()
    
    db.session.commit()
    registrar_log(1, 'Admin', 'BAJA_LÓGICA', 'danger', f"El usuario '{nombre}' fue dado de baja del sistema.")
    return True

def toggle_estado_usuario(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", 404)
        
    usuario.activo = not usuario.activo
    db.session.commit()
    
    accion = 'ACTIVAR_USUARIO' if usuario.activo else 'DESACTIVAR_USUARIO'
    gravedad = 'info' if usuario.activo else 'warning'
    registrar_log(1, 'Admin', accion, gravedad, f"Se cambió el acceso del usuario '{usuario.nombre}'.")
    return True

def eliminar_usuario_fisico(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", 404)
        
    nombre = usuario.nombre
    db.session.delete(usuario)
    db.session.commit()
    
    registrar_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El usuario '{nombre}' fue borrado físicamente.")
    return True