import re
from database.db import db
from models.time_entries import TimeEntries
from models.users import Users
from models.audits import Audits
from models.absences import Absences
from datetime import datetime, date
from sqlalchemy import func
from errors import APIError

def get_max_horas_dia_usuario(usuario_id, fecha_str):
    usuario = Users.query.get(usuario_id)
    if not usuario: return 8.5
    if isinstance(fecha_str, str): fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    else: fecha = fecha_str
    mes = fecha.month
    dia_semana = fecha.weekday()
    if dia_semana >= 5: return 0.0 
    es_verano = (mes == 7 or mes == 8)
    tipo = usuario.tipo_contrato or '40H'
    if tipo == '40H':
        if es_verano: return 7.0
        if dia_semana == 4: return 6.5
        return 8.5
    else:
        if es_verano: return float(usuario.horas_verano or 7.0)
        if dia_semana == 4: return float(usuario.horas_invierno_v or 6.5)
        return float(usuario.horas_invierno_lj or 8.5)

def get_pending_validations():
    solicitudes_db = TimeEntries.query.filter_by(estado="Pendiente").all()
    solicitudes = []
    for s in solicitudes_db:
        usuario_nombre = s.usuario.nombre if s.usuario else "Desconocido"
        nombres = usuario_nombre.split()
        avatar = (nombres[0][0] + (nombres[1][0] if len(nombres) > 1 else "")).upper() if nombres else "XX"
        proyecto_nombre = s.proyecto.nombre if s.proyecto else "Sin Proyecto"
        cliente_nombre = s.proyecto.cliente.nombre if s.proyecto and s.proyecto.cliente else "Interno"
        
        comentario_raw = s.comentario or ""
        horas_solicitadas = float(s.horas) if s.horas is not None else 0.0
        motivo_limpio = comentario_raw

        match = re.search(r'\[Solicita.*?([\d\.]+)h\]\s*-\s*Motivo:\s*(.*)', comentario_raw)
        if match:
            try:
                horas_solicitadas = float(match.group(1))
                motivo_limpio = match.group(2).strip()
            except ValueError:
                pass

        solicitudes.append({
            "id": s.id, "usuario": usuario_nombre, "avatar": avatar,
            "fecha": s.fecha.strftime("%Y-%m-%d") if s.fecha else "",
            "proyecto": proyecto_nombre, "cliente": cliente_nombre,
            "horasActuales": float(s.horas) if s.horas is not None else 0.0,
            "horasSolicitadas": horas_solicitadas, 
            "motivo": motivo_limpio or "Sin motivo especificado",
            "estado": "pendiente"
        })

    hoy = datetime.utcnow().date()
    fechas_conflictivas = db.session.query(Absences.fecha).filter(Absences.tipo == 'vacaciones', Absences.fecha >= hoy).group_by(Absences.fecha).having(func.count(Absences.id) >= 3).all()

    alertas_vacaciones = []
    for fc in fechas_conflictivas:
        fecha_conflictiva = fc.fecha
        ausencias_dia = Absences.query.filter_by(fecha=fecha_conflictiva, tipo='vacaciones').order_by(Absences.id.asc()).all()
        usuarios_ordenados = []
        for aus in ausencias_dia:
            nombre = aus.usuario.nombre if aus.usuario else f"ID: {aus.usuario_id}"
            usuarios_ordenados.append(nombre)
            
        fecha_str = fecha_conflictiva.strftime("%d/%m/%Y") if isinstance(fecha_conflictiva, date) else str(fecha_conflictiva)
        alertas_vacaciones.append({"fecha": fecha_str, "total": len(usuarios_ordenados), "usuarios": usuarios_ordenados})

    return {"solicitudes": solicitudes, "alertas_vacaciones": alertas_vacaciones}

def approve_validation(imputacion_id, nuevas_horas, manager_id=None):
    imputacion = TimeEntries.query.get(imputacion_id)
    if not imputacion: raise APIError("Imputación no encontrada", status_code=404)

    usuario_id = imputacion.usuario_id
    fecha = imputacion.fecha
    horas_float = float(nuevas_horas)

    manager = Users.query.get(manager_id) if manager_id else None
    manager_nombre = manager.nombre if manager else "Manager"

    if horas_float == 0.0:
        db.session.delete(imputacion)
        detalle_log = f"Solicitud {imputacion_id} aprobada y eliminada (0h) por {manager_nombre}"
        nuevo_log = Audits(actor_nombre=manager_nombre, accion="Aprobación Solicitud", gravedad="info", detalle=detalle_log)
        db.session.add(nuevo_log)
        db.session.commit()
        return True

    max_horas = get_max_horas_dia_usuario(usuario_id, fecha)
    otras_imputaciones = TimeEntries.query.filter(
        TimeEntries.usuario_id == usuario_id, TimeEntries.fecha == fecha,
        TimeEntries.id != imputacion_id, TimeEntries.estado != 'Rechazado'
    ).all()
    
    horas_otros_proyectos = sum(float(i.horas) for i in otras_imputaciones)
    
    if (horas_otros_proyectos + horas_float) > max_horas:
        raise APIError(f"No se puede aprobar. El total diario superaría su límite de {max_horas}h.", status_code=400)

    imputacion.horas = horas_float
    imputacion.estado = "Aprobado"
    imputacion.fecha_validacion = datetime.utcnow()
    imputacion.comentario = ""

    detalle_log = f"Solicitud {imputacion_id} aprobada con {horas_float}h por {manager_nombre}"
    nuevo_log = Audits(actor_nombre=manager_nombre, accion="Aprobación Solicitud", gravedad="info", detalle=detalle_log)
    db.session.add(nuevo_log)
    db.session.commit()
    return True

def reject_validation(imputacion_id, motivo_rechazo, manager_id=None):
    imputacion = TimeEntries.query.get(imputacion_id)
    if not imputacion: raise APIError("Imputación no encontrada", status_code=404)

    manager = Users.query.get(manager_id) if manager_id else None
    manager_nombre = manager.nombre if manager else "Manager"

    if float(imputacion.horas) == 0.0:
        db.session.delete(imputacion)
    else:
        imputacion.estado = "Rechazado"
        imputacion.comentario = f"[Rechazado] {motivo_rechazo}"

    detalle_log = f"Solicitud {imputacion_id} rechazada por {manager_nombre}. Motivo: {motivo_rechazo}"
    nuevo_log = Audits(actor_nombre=manager_nombre, accion="Rechazo Solicitud", gravedad="warning", detalle=detalle_log)
    db.session.add(nuevo_log)
    db.session.commit()
    return True