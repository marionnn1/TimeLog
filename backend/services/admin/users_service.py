from database.db import db
from models.users import Users
from services.admin.audit_service import registrar_log
from datetime import datetime
from errors import APIError
import requests
import base64

def obtener_usuarios():
    usuarios = Users.query.all()
    return [
        {
            "Id": u.id,
            "Nombre": u.nombre,
            "OidAzure": u.oid_azure,
            "Rol": u.rol,
            "Sede": u.sede,
            "Activo": u.activo,
            "Foto": getattr(u, 'foto', None) # <--- ¡AQUÍ FALTABA ESTO!
        }
        for u in usuarios
    ]

def crear_usuario(datos):
    nuevo_usuario = Users(
        nombre=datos["nombre"],
        oid_azure=datos["email"],
        rol=datos["rol"],
        sede=datos["sede"],
        activo=True,
        fecha_creacion=datetime.utcnow(),
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    registrar_log("Crear Usuario", "info", f"Se ha dado de alta al usuario: {datos['nombre']}.")
    return True

def actualizar_usuario(id_usuario, datos):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", status_code=404)

    usuario.nombre = datos["nombre"]
    usuario.oid_azure = datos["email"]
    usuario.rol = datos["rol"]
    usuario.sede = datos["sede"]

    db.session.commit()
    registrar_log("Actualizar Usuario", "info", f"Se actualizaron los datos del usuario: {datos['nombre']}.")
    return True

def eliminar_usuario(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", status_code=404)

    nombre = usuario.nombre
    usuario.activo = False
    usuario.fecha_desactivacion = datetime.utcnow()

    db.session.commit()
    registrar_log("Baja Lógica", "danger", f"El usuario '{nombre}' fue dado de baja del sistema.")
    return True

def toggle_estado_usuario(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", status_code=404)

    usuario.activo = not usuario.activo
    db.session.commit()

    accion = "Activar Usuario" if usuario.activo else "Desactivar Usuario"
    gravedad = "info" if usuario.activo else "warning"
    registrar_log(accion, gravedad, f"Se cambió el acceso del usuario '{usuario.nombre}'.")
    return True

def eliminar_usuario_fisico(id_usuario):
    usuario = Users.query.get(id_usuario)
    if not usuario:
        raise APIError("Usuario no encontrado", status_code=404)

    nombre = usuario.nombre
    db.session.delete(usuario)
    db.session.commit()

    registrar_log("Borrado Físico", "danger", f"El usuario '{nombre}' fue borrado físicamente.")
    return True

def descargar_y_guardar_foto_azure(access_token, usuario_bd):
    """
    Descarga la foto de perfil desde Microsoft Graph y la guarda en Base64.
    """
    if not access_token:
        return False
        
    url = "https://graph.microsoft.com/v1.0/me/photo/$value"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        respuesta = requests.get(url, headers=headers)
        
        # 200 OK significa que tiene foto configurada
        if respuesta.status_code == 200:
            imagen_b64 = base64.b64encode(respuesta.content).decode('utf-8')
            # Solo guardamos en BD si la foto ha cambiado (para ahorrar operaciones en la BD)
            if getattr(usuario_bd, 'foto', None) != imagen_b64:
                usuario_bd.foto = imagen_b64
                db.session.commit()
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error al descargar la foto de Azure: {e}")
        return False

def sincronizar_usuario(datos):
    from models.users import Users
    from database.db import db
    from datetime import datetime

    usuario = Users.query.filter_by(oid_azure=datos["oid_azure"]).first()

    if not usuario:
        nuevo_usuario = Users(
            nombre=datos["nombre"],
            oid_azure=datos["oid_azure"],
            rol="tecnico", 
            sede="Remoto",
            activo=True,
            fecha_creacion=datetime.utcnow(),
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        usuario = nuevo_usuario

    if not usuario.activo:
        from errors import APIError
        raise APIError(
            "Tu usuario ha sido desactivado del sistema. Contacta con el administrador.",
            status_code=403,
        )

    access_token = datos.get("access_token")
    if access_token:
        descargar_y_guardar_foto_azure(access_token, usuario)

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "rol": usuario.rol.lower() if usuario.rol else "tecnico",
        "foto": getattr(usuario, 'foto', None),
        "iniciales": (
            "".join([n[0] for n in usuario.nombre.split()[:2]]).upper()
            if usuario.nombre
            else "XX"
        ),
    }