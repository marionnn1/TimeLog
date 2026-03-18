from database.db import db
from models.time_entries import TimeEntries
from models.audits import Audits
from datetime import datetime


def get_pending_validations():
    try:
        requests_db = TimeEntries.query.filter_by(estado="Pendiente").all()

        requests = []
        for s in requests_db:
            user_name = s.usuario.nombre if s.usuario else "Desconocido"

            names = user_name.split()
            avatar = (
                (names[0][0] + (names[1][0] if len(names) > 1 else "")).upper()
                if names
                else "XX"
            )

            project_name = s.proyecto.nombre if s.proyecto else "Sin Proyecto"
            client_name = (
                s.proyecto.cliente.nombre
                if s.proyecto and s.proyecto.cliente
                else "Interno"
            )

            requests.append(
                {
                    "id": s.id,
                    "user": user_name,
                    "avatar": avatar,
                    "date": s.fecha.strftime("%Y-%m-%d") if s.fecha else "",
                    "project": project_name,
                    "client": client_name,
                    "currentHours": float(s.horas),
                    "reason": s.comentario or "Sin motivo especificado",
                    "status": "pending",
                }
            )

        return requests, 200
    except Exception as e:
        print(f"Error al obtener validaciones pendientes: {e}")
        return {"error": str(e)}, 500


def approve_validation(time_entry_id, new_hours):
    try:
        time_entry = TimeEntries.query.get(time_entry_id)
        if not time_entry:
            return {"error": "Time entry not found"}, 404

        time_entry.horas = new_hours
        time_entry.estado = "Aprobado"
        time_entry.fecha_validacion = datetime.utcnow()

        db.session.commit()
        return {"message": "Request approved and corrected"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al aprobar validación: {e}")
        return {"error": str(e)}, 500


def reject_validation(time_entry_id, rejection_reason):
    try:
        time_entry = TimeEntries.query.get(time_entry_id)
        if not time_entry:
            return {"error": "Time entry not found"}, 404

        time_entry.estado = "Rechazado"

        detalle_log = f"Solicitud {time_entry_id} rechazada. Motivo: {rejection_reason}"
        nuevo_log = Audits(
            actor_nombre="Manager",
            accion="Rechazo Solicitud",
            gravedad="warning",
            detalle=detalle_log,
        )
        db.session.add(nuevo_log)

        db.session.commit()
        return {"message": "Request rejected"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al rechazar validación: {e}")
        return {"error": str(e)}, 500