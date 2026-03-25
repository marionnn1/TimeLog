import re
from database.db import db
from models.time_entries import TimeEntries
from models.users import Users
from models.audits import Audits
from datetime import datetime
from utils.exceptions import APIError

def get_max_horas_dia_usuario(usuario_id, fecha_str):
    usuario = Users.query.get(usuario_id)
    if not usuario: return 8.5
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if isinstance(fecha_str, str) else fecha_str
    mes, dia_semana = fecha.month, fecha.weekday()
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

        comentario_raw = s.comentario or ""
        horas_solicitadas = float(s.horas) if s.horas is not None else 0.0
        motivo_limpio = comentario_raw

        match = re.search(r'\[Solicita.*?([\d\.]+)h\]\s*-\s*Motivo:\s*(.*)', comentario_raw)
        if match:
            try:
                horas_solicitadas, motivo_limpio = float(match.group(1)), match.group(2).strip()
            except ValueError: pass

        solicitudes.append({
            "id": s.id, "usuario": usuario_nombre, "avatar": avatar,
            "fecha": s.fecha.strftime("%Y-%m-%d") if s.fecha else "",
            "proyecto": s.proyecto.nombre if s.proyecto else "Sin Proyecto",
            "cliente": s.proyecto.cliente.nombre if s.proyecto and s.proyecto.cliente else "Interno",
            "horasActuales": float(s.horas) if s.horas is not None else 0.0,
            "horasSolicitadas": horas_solicitadas, "motivo": motivo_limpio or "Sin motivo", "estado": "pendiente",
        })
    return solicitudes

def approve_validation(imputacion_id, nuevas_horas):
    imputacion = TimeEntries.query.get(imputacion_id)
    if not imputacion: raise APIError("Imputación no encontrada", 404)

    max_horas = get_max_horas_dia_usuario(imputacion.usuario_id, imputacion.fecha)
    otras_imputaciones = TimeEntries.query.filter(
        TimeEntries.usuario_id == imputacion.usuario_id, TimeEntries.fecha == imputacion.fecha,
        TimeEntries.id != imputacion_id, TimeEntries.estado != 'Rechazado'
    ).all()
    
    horas_otros_proyectos = sum(float(i.horas) for i in otras_imputaciones)
    if (horas_otros_proyectos + float(nuevas_horas)) > max_horas:
        raise APIError(f"El total diario superaría el límite de {max_horas}h.", 400)

    imputacion.horas = nuevas_horas
    imputacion.estado = "Aprobado"
    imputacion.fecha_validacion = datetime.utcnow()
    imputacion.comentario = ""
    db.session.commit()
    return True

def reject_validation(imputacion_id, motivo_rechazo):
    imputacion = TimeEntries.query.get(imputacion_id)
    if not imputacion: raise APIError("Imputación no encontrada", 404)

    if float(imputacion.horas) == 0.0:
        db.session.delete(imputacion)
    else:
        imputacion.estado = "Rechazado"
        imputacion.comentario = f"[Rechazado] {motivo_rechazo}"

    db.session.add(Audits(actor_nombre="Manager", accion="Rechazo Solicitud", gravedad="warning", detalle=f"Solicitud {imputacion_id} rechazada. Motivo: {motivo_rechazo}"))
    db.session.commit()
    return True