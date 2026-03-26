import urllib.parse
from flask import request, has_request_context
from database.db import db
from models.audits import Audits
from errors import APIError

def obtener_logs():
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

def registrar_log(actor_id, actor_nombre, accion, gravedad, detalle):
    if has_request_context():
        header_id = request.headers.get('X-User-Id')
        header_name = request.headers.get('X-User-Name')
        if header_id: actor_id = header_id
        if header_name: actor_nombre = urllib.parse.unquote(header_name) 

    if not actor_nombre:
        actor_nombre = "Sistema"

    nuevo_log = Audits(
        actor_id=actor_id,
        actor_nombre=actor_nombre,
        accion=accion,
        gravedad=gravedad,
        detalle=detalle,
    )
    db.session.add(nuevo_log)
    db.session.commit()
    return True