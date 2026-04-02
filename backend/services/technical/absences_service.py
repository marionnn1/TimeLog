from database.db import db
from models.absences import Absences
from models.time_entries import TimeEntries
from models.audits import Audits
from models.users import Users
from sqlalchemy import extract
from datetime import datetime 
from errors import APIError

def obtener_ausencias_mes(mes, anio):
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

def obtener_resumen_anual(anio):
    usuarios = Users.query.filter_by(activo=True).all()
    
    ausencias = Absences.query.filter(extract("year", Absences.fecha) == anio).all()

    resumen = []
    for user in usuarios:
        aus_usuario = [a for a in ausencias if a.usuario_id == user.id]
        
        iniciales = "".join([n[0] for n in user.nombre.split()[:2]]).upper() if user.nombre else "XX"

        resumen.append({
            "userId": user.id,
            "nombre": user.nombre,
            "iniciales": iniciales,
            "dias": [
                {
                    "fecha": a.fecha.strftime("%Y-%m-%d"),
                    "tipo": a.tipo,
                    "comentario": a.comentario
                } for a in sorted(aus_usuario, key=lambda x: x.fecha)
            ]
        })
    
    return sorted(resumen, key=lambda x: x['nombre'])

def contar_ausencias(usuario_id, fecha_inicio, fecha_fin):
    count = Absences.query.filter(
        Absences.usuario_id == usuario_id,
        Absences.fecha >= fecha_inicio,
        Absences.fecha <= fecha_fin
    ).count()
    
    return count

def guardar_ausencias(usuario_id, fechas, tipo, comentario=""):
    if not usuario_id or not fechas:
        raise APIError("Faltan datos obligatorios (usuario o fechas)", status_code=400)

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

# def eliminar_ausencias(usuario_id, fechas):
#     if not usuario_id or not fechas:
#         raise APIError("Faltan datos obligatorios para eliminar", status_code=400)

#     usuario = Users.query.get(usuario_id)
#     usuario_nombre = usuario.nombre if usuario else "Desconocido"
    
#     fechas_eliminadas = []

#     for fecha in fechas:
#         fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date() if isinstance(fecha, str) else fecha
        
#         ausencia = Absences.query.filter_by(usuario_id=usuario_id, fecha=fecha_obj).first()
#         if ausencia:
#             tipo = ausencia.tipo
#             db.session.delete(ausencia)
#             fechas_eliminadas.append(str(fecha_obj))
            
#     if fechas_eliminadas:
#         detalle = f"El usuario {usuario_nombre} eliminó {len(fechas_eliminadas)} días de ausencia ({tipo}): {', '.join(fechas_eliminadas)}"
#         nueva_auditoria = Audits(actor_id=usuario_id, actor_nombre=usuario_nombre, accion='Eliminar Ausencia', gravedad='info', detalle=detalle)
#         db.session.add(nueva_auditoria)
        
#     db.session.commit()
#     return True



def eliminar_ausencias(usuario_id, fecha_inicio, fecha_fin):
    if not usuario_id or not fecha_inicio or not fecha_fin:
        raise APIError("Faltan fechas de inicio o fin para el borrado", status_code=400)

    ausencias_a_borrar = Absences.query.filter(
        Absences.usuario_id == usuario_id,
        Absences.fecha >= fecha_inicio,
        Absences.fecha <= fecha_fin
    ).all()

    if not ausencias_a_borrar:
        return False

    usuario = Users.query.get(usuario_id)
    usuario_nombre = usuario.nombre if usuario else "Desconocido"
    
    Absences.query.filter(
        Absences.usuario_id == usuario_id,
        Absences.fecha >= fecha_inicio,
        Absences.fecha <= fecha_fin
    ).delete(synchronize_session=False)

    cantidad = len(ausencias_a_borrar)
    detalle = (f"El usuario {usuario_nombre} eliminó un rango de {cantidad} días "
                f"desde {fecha_inicio} hasta {fecha_fin}.")
    
    nueva_auditoria = Audits(
        actor_id=usuario_id, 
        actor_nombre=usuario_nombre, 
        accion='Eliminar Rango Ausencias', 
        gravedad='info', 
        detalle=detalle
    )
    
    db.session.add(nueva_auditoria)
    db.session.commit()
    return True