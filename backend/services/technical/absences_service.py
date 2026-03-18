from database.db import db
from models.absences import Absences
from sqlalchemy import extract


def get_monthly_absences(month, year):
    try:
        absences = Absences.query.filter(
            extract("month", Absences.fecha) == month,
            extract("year", Absences.fecha) == year,
        ).all()

        return format_absences(absences)
    except Exception as e:
        print(f"Error al obtener ausencias: {e}")
        return []


def get_annual_absences(year):
    try:
        absences = Absences.query.filter(
            extract("year", Absences.fecha) == year,
        ).all()

        return format_absences(absences)
    except Exception as e:
        print(f"Error al obtener resumen anual de ausencias: {e}")
        return []


def format_absences(absences):
    return [
        {
            "date": a.fecha.strftime("%Y-%m-%d") if a.fecha else None,
            "type": a.tipo,
            "comment": a.comentario or "",
            "userId": a.usuario_id,
            "name": a.usuario.nombre if a.usuario else "Desconocido",
            "initials": (
                "".join([n[0] for n in a.usuario.nombre.split()[:2]]).upper()
                if a.usuario
                else "XX"
            ),
        }
        for a in absences
    ]


def save_absences(user_id, dates, type, comment=""):
    try:
        for date in dates:
            exists = Absences.query.filter_by(
                usuario_id=user_id, fecha=date
            ).first()
            if not exists:
                new_absence = Absences(
                    usuario_id=user_id, fecha=date, tipo=type, comentario=comment
                )
                db.session.add(new_absence)

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error al guardar ausencias: {e}")
        db.session.rollback()
        return False


def delete_absence(user_id, date):
    try:
        absence = Absences.query.filter_by(usuario_id=user_id, fecha=date).first()
        if absence:
            db.session.delete(absence)
            db.session.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar ausencia: {e}")
        db.session.rollback()
        return False