from database.db import db
from models.users import Users
from services.admin.audit_service import registrar_log
from datetime import datetime
from errors import APIError

def obtener_usuarios():
    usuarios = Users.query.all()
    return [{
        "Id": u.id,
        "Nombre": u.nombre,
        "OidAzure": u.oid_azure,
        "Rol": u.rol,
        "Sede": u.sede,
        "Activo": u.activo
    } for u in usuarios]

def crear_usuario(datos):
    nuevo_usuario = Users(
        nombre=datos['nombre'],
        oid_azure=datos['email'],
        rol=datos['rol'],
        sede=datos['sede'],
        activo=True,
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    registrar_log(1, 'Admin', 'CREAR_USUARIO', 'info', f"Se ha dado de alta al usuario: {datos['nombre']}.")
    return True

def actualizar_usuario(id_usuario, datos):
    usuario = Users.query.get(id_usuario)
    if not usuario: raise APIError("Usuario no encontrado", status_code=404)
        
    usuario.nombre = datos['nombre']
    usuario.oid_azure = datos['email']
    usuario.rol = datos['rol']
    usuario.sede = datos['sede']
    
    db.session.commit()
    registrar_log(1, 'Admin', 'ACTUALIZAR_USUARIO', 'info', f"Se actualizaron los datos del usuario: {datos['nombre']}.")
    return True

def eliminar_usuario(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario: raise APIError("Usuario no encontrado", status_code=404)

    nombre = usuario.nombre
    usuario.activo = False
    usuario.fecha_desactivacion = datetime.utcnow()
    
    db.session.commit()
    registrar_log(1, 'Admin', 'BAJA_LÓGICA', 'danger', f"El usuario '{nombre}' fue dado de baja del sistema.")
    return True

def toggle_estado_usuario(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario: raise APIError("Usuario no encontrado", status_code=404)
        
    usuario.activo = not usuario.activo
    db.session.commit()
    
    accion = 'ACTIVAR_USUARIO' if usuario.activo else 'DESACTIVAR_USUARIO'
    gravedad = 'info' if usuario.activo else 'warning'
    registrar_log(1, 'Admin', accion, gravedad, f"Se cambió el acceso del usuario '{usuario.nombre}'.")
    return True

def eliminar_usuario_fisico(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario: raise APIError("Usuario no encontrado", status_code=404)
        
    nombre = usuario.nombre
    db.session.delete(usuario)
    db.session.commit()
    
    registrar_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El usuario '{nombre}' fue borrado físicamente.")
    return True