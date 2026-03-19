import re
from database.db import db
from models.time_entries import TimeEntries
from models.audits import Audits
from datetime import datetime


def get_pending_validations():
    try:
        solicitudes_db = TimeEntries.query.filter_by(estado="Pendiente").all()

        solicitudes = []
        for s in solicitudes_db:
            usuario_nombre = s.usuario.nombre if s.usuario else "Desconocido"

            nombres = usuario_nombre.split()
            avatar = (
                (nombres[0][0] + (nombres[1][0] if len(nombres) > 1 else "")).upper()
                if nombres
                else "XX"
            )

            proyecto_nombre = s.proyecto.nombre if s.proyecto else "Sin Proyecto"
            cliente_nombre = (
                s.proyecto.cliente.nombre
                if s.proyecto and s.proyecto.cliente
                else "Interno"
            )

            comentario_raw = s.comentario or ""
            horas_solicitadas = float(s.horas) 
            motivo_limpio = comentario_raw

            match = re.search(r'\[Solicita cambio a ([\d\.]+)h\] - Motivo: (.*)', comentario_raw)
            if match:
                try:
                    horas_solicitadas = float(match.group(1))
                    motivo_limpio = match.group(2).strip()
                except ValueError:
                    pass

            solicitudes.append(
                {
                    "id": s.id,
                    "usuario": usuario_nombre,
                    "avatar": avatar,
                    "fecha": s.fecha.strftime("%Y-%m-%d") if s.fecha else "",
                    "proyecto": proyecto_nombre,
                    "cliente": cliente_nombre,
                    "horasActuales": float(s.horas),
                    "horasSolicitadas": horas_solicitadas, 
                    "motivo": motivo_limpio or "Sin motivo especificado",
                    "estado": "pendiente",
                }
            )

        return solicitudes, 200
    except Exception as e:
        print(f"Error al obtener validaciones pendientes: {e}")
        return {"error": str(e)}, 500


def approve_validation(imputacion_id, nuevas_horas):
    try:
        imputacion = TimeEntries.query.get(imputacion_id)
        if not imputacion:
            return {"error": "Imputación no encontrada"}, 404

        imputacion.horas = nuevas_horas
        imputacion.estado = "Aprobado"
        imputacion.fecha_validacion = datetime.utcnow()

        db.session.commit()
        return {"message": "Solicitud aprobada y corregida"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al aprobar validación: {e}")
        return {"error": str(e)}, 500


def reject_validation(imputacion_id, motivo_rechazo):
    try:
        imputacion = TimeEntries.query.get(imputacion_id)
        if not imputacion:
            return {"error": "Imputación no encontrada"}, 404

        imputacion.estado = "Rechazado"

        detalle_log = f"Solicitud {imputacion_id} rechazada. Motivo: {motivo_rechazo}"
        nuevo_log = Audits(
            actor_nombre="Manager",
            accion="Rechazo Solicitud",
            gravedad="warning",
            detalle=detalle_log,
        )
        db.session.add(nuevo_log)

        db.session.commit()
        return {"message": "Solicitud rechazada"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al rechazar validación: {e}")
        return {"error": str(e)}, 500