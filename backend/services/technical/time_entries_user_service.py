from database.db import db
from models.time_entries import TimeEntries
from models.absences import Absences
from services.admin.audit_service import registrar_log
from datetime import datetime, timedelta
from errors import APIError

def obtener_imputaciones_semana(usuario_id, lunes):
    if isinstance(lunes, str):
        lunes = datetime.strptime(lunes, "%Y-%m-%d").date()
    domingo = lunes + timedelta(days=6)

    imputaciones = TimeEntries.query.filter(
        TimeEntries.usuario_id == usuario_id,
        TimeEntries.fecha >= lunes,
        TimeEntries.fecha <= domingo,
    ).all()

    return [
        {
            "ProyectoId": i.proyecto_id,
            "Proyecto": i.proyecto.nombre if i.proyecto else "Sin Proyecto",
            "Cliente": (
                i.proyecto.cliente.nombre
                if i.proyecto and i.proyecto.cliente
                else "Sin Cliente"
            ),
            "Fecha": i.fecha.strftime("%Y-%m-%d"),
            "Horas": float(i.horas),
        }
        for i in imputaciones
    ]

def guardar_imputaciones_lote(usuario_id, filas, fechas_semana):
    if not usuario_id or not filas or not fechas_semana:
        raise APIError("Faltan datos obligatorios para guardar imputaciones", status_code=400)

    ausencias = Absences.query.filter(
        Absences.usuario_id == usuario_id,
        Absences.fecha.in_(fechas_semana),
        Absences.tipo.in_(['vacaciones', 'festivo'])
    ).all()
    
    fechas_bloqueadas = [
        a.fecha.strftime("%Y-%m-%d") if isinstance(a.fecha, datetime) else str(a.fecha) 
        for a in ausencias
    ]

    for fila in filas:
        proyecto_id = fila.get("id_proyecto")
        horas = fila.get("horas", [])

        for i in range(7):
            fecha = fechas_semana[i]
            h = float(horas[i]) if i < len(horas) and horas[i] else 0
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else str(fecha)
            
            if fecha_str in fechas_bloqueadas and h > 0:
                continue  

            registro = TimeEntries.query.filter_by(
                usuario_id=usuario_id, proyecto_id=proyecto_id, fecha=fecha
            ).first()

            if registro and registro.estado == "Aprobado":
                registro.estado = "Pendiente"
                registro.horas = h
            else:
                if registro:
                    db.session.delete(registro)
                if h > 0:
                    nuevo = TimeEntries(
                        usuario_id=usuario_id,
                        proyecto_id=proyecto_id,
                        fecha=fecha,
                        horas=h,
                        estado="Borrador",
                    )
                    db.session.add(nuevo)

    db.session.commit()
    registrar_log(
        usuario_id,
        "Usuario",
        "SYNC_IMPUTACIONES",
        "info",
        "Sincronización semanal realizada.",
    )
    return True