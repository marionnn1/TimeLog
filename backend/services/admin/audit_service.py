from database.db import db
from models.audits import Audits

def get_logs():
    try:
        logs = Audits.query.order_by(Audits.fecha.desc(), Audits.id.desc()).all()

        return [
            {
                "id": log.id,
                "date": log.fecha.strftime("%d/%m/%Y %H:%M:%S") if log.fecha else "",
                "actor": log.actor_nombre,
                "action": log.accion,
                "severity": log.gravedad,
                "detail": log.detalle,
            }
            for log in logs
        ]
    except Exception as e:
        print(f"Error al obtener logs: {e}")
        return None

def register_log(actor_id, actor_name, action, severity, detail):
    try:
        nuevo_log = Audits(
            actor_id=actor_id,
            actor_nombre=actor_name,
            accion=action,
            gravedad=severity,
            detalle=detail,
        )
        db.session.add(nuevo_log)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error al guardar log: {e}")
        db.session.rollback()
        return False