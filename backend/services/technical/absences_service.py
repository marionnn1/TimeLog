from database.db import db
from models.absences import Absences
from models.time_entries import TimeEntries
from models.audits import Audits
from models.users import Users
from sqlalchemy import extract
from datetime import datetime 


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
        usuario = Users.query.get(usuario_id)
        usuario_nombre = usuario.nombre if usuario else "Desconocido"
        
        fechas_guardadas = []

        for f in fechas:
            fecha_obj = datetime.strptime(f, "%Y-%m-%d").date() if isinstance(f, str) else f
            
            imputaciones = TimeEntries.query.filter_by(usuario_id=usuario_id, fecha=fecha_obj).all()
            for imputacion in imputaciones:
                db.session.delete(imputacion)
            
            existe = Absences.query.filter_by(usuario_id=usuario_id, fecha=fecha_obj).first()
            if not existe:
                nueva_ausencia = Absences(usuario_id=usuario_id, fecha=fecha_obj, tipo=tipo, comentario=comentario)
                db.session.add(nueva_ausencia)
                fechas_guardadas.append(str(fecha_obj))

        if fechas_guardadas:
            detalle = f"El usuario {usuario_nombre} registró {len(fechas_guardadas)} días de ausencia ({tipo}): {', '.join(fechas_guardadas)}"
            nueva_auditoria = Audits(actor_id=usuario_id, actor_nombre=usuario_nombre, accion='Registro Ausencia', gravedad='info', detalle=detalle)
            db.session.add(nueva_auditoria)

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error al guardar ausencias: {e}")
        db.session.rollback()
        return False

def eliminar_ausencias(usuario_id, fechas):
    try:
        from models.users import Users
        from models.audits import Audits
        
        usuario = Users.query.get(usuario_id)
        usuario_nombre = usuario.nombre if usuario else "Desconocido"
        
        fechas_eliminadas = []

        for fecha in fechas:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date() if isinstance(fecha, str) else fecha
            
            ausencia = Absences.query.filter_by(usuario_id=usuario_id, fecha=fecha_obj).first()
            if ausencia:
                tipo = ausencia.tipo
                db.session.delete(ausencia)
                fechas_eliminadas.append(str(fecha_obj))
                
        if fechas_eliminadas:
            detalle = f"El usuario {usuario_nombre} eliminó {len(fechas_eliminadas)} días de ausencia ({tipo}): {', '.join(fechas_eliminadas)}"
            nueva_auditoria = Audits(actor_id=usuario_id, actor_nombre=usuario_nombre, accion='Eliminar Ausencia', gravedad='info', detalle=detalle)
            db.session.add(nueva_auditoria)
            
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar ausencias: {e}")
        db.session.rollback()
        return False