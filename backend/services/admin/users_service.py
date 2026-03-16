from database.db import db
from models.users import Users
from services.admin.audit_service import register_log
from datetime import datetime

def get_users():
    try:
        users = Users.query.all()
        return [{
            'id': user.id,
            'name': user.nombre,
            'email': user.oid_azure,
            'role': user.rol,
            'location': user.sede,
            'active': user.activo
        } for user in users]
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return None

def create_user(data):
    try:
        new_user = Users(
            nombre=data['name'],
            oid_azure=data['email'],
            rol=data['role'],
            sede=data['location'],
            activo=True,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        
        register_log(1, 'Admin', 'CREAR_USUARIO', 'info', f"Se ha dado de alta al usuario: {data['name']}.")
        return True
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        db.session.rollback()
        return False

def update_user(user_id, data):
    try:
        user = Users.query.get(user_id)
        if not user:
            return False
            
        user.nombre = data['name']
        user.oid_azure = data['email']
        user.rol = data['role']
        user.sede = data['location']
        
        db.session.commit()
        register_log(1, 'Admin', 'ACTUALIZAR_USUARIO', 'info', f"Se actualizaron los datos del usuario: {data['name']}.")
        return True
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        db.session.rollback()
        return False

def delete_user(user_id):
    try:
        user = Users.query.get(user_id)
        if not user:
            return False

        name = user.nombre
        user.activo = False
        user.fecha_desactivacion = datetime.utcnow()
        
        db.session.commit()
        register_log(1, 'Admin', 'BAJA_LÓGICA', 'danger', f"El usuario '{name}' fue dado de baja del sistema.")
        return True
    except Exception as e:
        print(f"Error al dar de baja al usuario: {e}")
        db.session.rollback()
        return False

def toggle_user_status(user_id):
    try:
        user = Users.query.get(user_id)
        if not user:
            return False
            
        user.activo = not user.activo
        db.session.commit()
        
        action = 'ACTIVAR_USUARIO' if user.activo else 'DESACTIVAR_USUARIO'
        severity = 'info' if user.activo else 'warning'
        register_log(1, 'Admin', action, severity, f"Se cambió el acceso del usuario '{user.nombre}'.")
        return True
    except Exception as e:
        print(f"Error al cambiar estado del usuario: {e}")
        db.session.rollback()
        return False

def hard_delete_user(user_id):
    try:
        user = Users.query.get(user_id)
        if not user:
            return False
            
        name = user.nombre
        
        db.session.delete(user)
        db.session.commit()
        
        register_log(1, 'Admin', 'BORRADO_FISICO', 'danger', f"El usuario '{name}' fue borrado físicamente.")
        return True
    except Exception as e:
        print(f"Error al borrar físicamente al usuario: {e}")
        db.session.rollback()
        return False