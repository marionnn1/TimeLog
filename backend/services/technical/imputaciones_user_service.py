from database.db import db
from models.time_entries import TimeEntries
from services.admin.auditoria_service import registrar_log
from datetime import datetime, timedelta


def obtener_imputaciones_semana(usuario_id, lunes):
    try:
        if isinstance(lunes, str):
            lunes = datetime.strptime(lunes, "%Y-%m-%d").date()
        domingo = lunes + timedelta(days=6)

        # Filtramos por rango de fechas
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
    except Exception as e:
        print(f"Error al obtener imputaciones: {e}")
        return None


def guardar_imputaciones_lote(usuario_id, filas, fechas_semana):
    try:
        for fila in filas:
            proyecto_id = fila.get("id_proyecto")
            horas = fila.get("horas", [])

            for i in range(7):
                fecha = fechas_semana[i]
                h = float(horas[i]) if i < len(horas) and horas[i] else 0

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
    except Exception as e:
        print(f"Error al guardar lote: {e}")
        db.session.rollback()
        return False
