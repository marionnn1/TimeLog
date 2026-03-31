import urllib.parse
from flask import g, has_request_context
from database.db import db
from models.audits import Audits
from errors import APIError

def obtener_logs():
    """Obtiene todos los registros de auditoría ordenados por fecha descendente."""
    logs = Audits.query.order_by(Audits.fecha.desc(), Audits.id.desc()).all()
    return [
        {
            "id": log.id,
            "fecha": log.fecha.strftime("%d/%m/%Y %H:%M:%S") if log.fecha else "",
            "actor": log.actor_nombre,
            "accion": log.accion,
            "gravedad": log.gravedad,
            "detalle": log.detalle,
        }
        for log in logs
    ]

def registrar_log(accion, gravedad, detalle, actor_id=None, actor_nombre=None):
    """
    Registra una acción en el historial. 
    Prioriza automáticamente al usuario autenticado en el token (g.usuario_actual).
    """
    usuario_sesion = getattr(g, 'usuario_actual', None)

    if usuario_sesion:
        actor_id = usuario_sesion.id
        actor_nombre = usuario_sesion.nombre
    
    if not actor_nombre:
        actor_nombre = "Sistema"

    nuevo_log = Audits(
        actor_id=actor_id,
        actor_nombre=actor_nombre,
        accion=accion,
        gravedad=gravedad,
        detalle=detalle,
    )
    
    try:
        db.session.add(nuevo_log)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar log: {str(e)}")
        return False