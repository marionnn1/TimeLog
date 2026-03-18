from database.db import db
from models.time_entries import TimeEntries
from services.admin.audit_service import register_log
from datetime import datetime, timedelta


def get_weekly_time_entries(user_id, monday_date):
    try:
        if isinstance(monday_date, str):
            monday_date = datetime.strptime(monday_date, "%Y-%m-%d").date()
        sunday_date = monday_date + timedelta(days=6)

        time_entries = TimeEntries.query.filter(
            TimeEntries.usuario_id == user_id,
            TimeEntries.fecha >= monday_date,
            TimeEntries.fecha <= sunday_date,
        ).all()

        return [
            {
                "projectId": i.proyecto_id,
                "project": i.proyecto.nombre if i.proyecto else "Sin Proyecto",
                "client": (
                    i.proyecto.cliente.nombre
                    if i.proyecto and i.proyecto.cliente
                    else "Sin Cliente"
                ),
                "date": i.fecha.strftime("%Y-%m-%d"),
                "hours": float(i.horas),
            }
            for i in time_entries
        ]
    except Exception as e:
        print(f"Error al obtener imputaciones: {e}")
        return None


def save_time_entries_batch(user_id, rows, week_dates):
    try:
        for row in rows:
            project_id = row.get("projectId")
            hours = row.get("hours", [])

            for i in range(7):
                date = week_dates[i]
                h = float(hours[i]) if i < len(hours) and hours[i] else 0

                record = TimeEntries.query.filter_by(
                    usuario_id=user_id, proyecto_id=project_id, fecha=date
                ).first()

                if record and record.estado == "Aprobado":
                    record.estado = "Pendiente"
                    record.horas = h
                else:
                    if record:
                        db.session.delete(record)
                    if h > 0:
                        new_entry = TimeEntries(
                            usuario_id=user_id,
                            proyecto_id=project_id,
                            fecha=date,
                            horas=h,
                            estado="Borrador",
                        )
                        db.session.add(new_entry)

        db.session.commit()
        register_log(
            user_id,
            "User",
            "SYNC_IMPUTACIONES",
            "info",
            "Sincronización semanal realizada.",
        )
        return True
    except Exception as e:
        print(f"Error al guardar lote: {e}")
        db.session.rollback()
        return False