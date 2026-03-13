# backend/services/admin/usuarios_service.py
from database.db import db
from models.users import Users
from TimeLog.backend.services.admin.audit_service import registrar_log
from datetime import datetime

def obtener_usuarios():
    try:
        # Hacemos la consulta sobre el modelo Users
        usuarios = Users.query.all()
        return [user.to_dict() for user in usuarios]
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return None

def crear_usuario(datos):
    try:
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
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        db.session.rollback()
        return False

def actualizar_usuario(id_usuario, datos):
    try:
        usuario = Users.query.get(id_usuario)
        if not usuario:
            return False
            
        usuario.nombre = datos['nombre']
        usuario.oid_azure = datos['email']
        usuario.rol = datos['rol']
        usuario.sede = datos['sede']
        
        db.session.commit()
        registrar_log(1, 'Admin', 'ACTUALIZAR_USUARIO', 'info', f"Se actualizaron los datos del usuario: {datos['nombre']}.")
        return True
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        db.session.rollback()
        return False

def eliminar_usuario(id_usuario):
    # Baja Lógica
    try:
        usuario = Users.query.get(id_usuario)
        if not usuario:
            return False

        nombre = usuario.nombre
        usuario.activo = False
        usuario.fecha_desactivacion = datetime.utcnow()
        
        db.session.commit()
        registrar_log(1, 'Admin', 'BAJA_LÓGICA', 'danger', f"El usuario '{nombre}' fue dado de baja del sistema.")
        return True
    except Exception as e:
        print(f"Error al dar de baja al usuario: {e}")
        db.session.rollback()
        return False

def toggle_estado_usuario(id_usuario):
    try:
        usuario = Users.query.get(id_usuario)
        if not usuario:
            return False
            
        usuario.activo = not usuario.activo
        db.session.commit()
        
        accion = 'ACTIVAR_USUARIO' if usuario.activo else 'DESACTIVAR_USUARIO'
        gravedad = 'info' if usuario.activo else 'warning'
        registrar_log(1, 'Admin', accion, gravedad, f"Se cambió el acceso del usuario '{usuario.nombre}'.")
        return True
    except Exception as e:
        print(f"Error al cambiar estado del usuario: {e}")
        db.session.rollback()
        return False

def eliminar_usuario_fisico(id_usuario):
    # Borrado Físico Real
    try:
        usuario = Users.query.get(id_usuario)
        if not usuario:
            return False
            
        nombre = usuario.nombre
        
        db.session.delete(usuario)
        db.session.commit()
        
        registrar_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El usuario '{nombre}' fue borrado físicamente.")
        return True
    except Exception as e:
        print(f"Error al borrar físicamente al usuario: {e}")
        db.session.rollback()
        return False