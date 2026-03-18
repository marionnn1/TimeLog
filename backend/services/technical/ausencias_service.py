from database.db import db
from models.absences import Absences
from sqlalchemy import extract


def obtener_ausencias_mes(mes, anio):
    try:
        ausencias = Absences.query.filter(
            extract("month", Absences.fecha) == mes,
            extract("year", Absences.fecha) == anio,
        ).all()

        return [
            {
                "fecha": a.fecha.strftime("%Y-%m-%d") if a.fecha else None,
                "tipo": a.tipo,
                "comentario": a.comentario or "",
                "userId": a.usuario_id,
                "nombre": a.usuario.nombre if a.usuario else "Desconocido",
                "iniciales": (
                    "".join([n[0] for n in a.usuario.nombre.split()[:2]]).upper()
                    if a.usuario
                    else "XX"
                ),
            }
            for a in ausencias
        ]
    except Exception as e:
        print(f"Error al obtener ausencias: {e}")
        return []


def guardar_ausencias(usuario_id, fechas, tipo, comentario=""):
    try:
        for fecha in fechas:
            existe = Absences.query.filter_by(
                usuario_id=usuario_id, fecha=fecha
            ).first()
            if not existe:
                nueva_ausencia = Absences(
                    usuario_id=usuario_id, fecha=fecha, tipo=tipo, comentario=comentario
                )
                db.session.add(nueva_ausencia)

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error al guardar ausencias: {e}")
        db.session.rollback()
        return False


def eliminar_ausencia(usuario_id, fecha):
    try:
        ausencia = Absences.query.filter_by(usuario_id=usuario_id, fecha=fecha).first()
        if ausencia:
            db.session.delete(ausencia)
            db.session.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar ausencia: {e}")
        db.session.rollback()
        return False
