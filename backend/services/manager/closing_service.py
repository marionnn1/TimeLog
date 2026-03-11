import calendar
from datetime import date, datetime
from database.db import db
from models.users import Users
from models.time_entries import TimeEntries
from models.absences import Absences
from models.month_closings import MonthClosings
from sqlalchemy import extract


def get_closing_audit(month):
    try:
        year, month_num = map(int, month.split("-"))

        closing_record = MonthClosings.query.filter_by(anio=year, mes=month_num).first()
        is_month_closed = bool(closing_record.esta_cerrado) if closing_record else False

        _, num_days = calendar.monthrange(year, month_num)

        users = Users.query.filter_by(activo=True).all()

        month_time_entries = TimeEntries.query.filter(
            extract("year", TimeEntries.fecha) == year,
            extract("month", TimeEntries.fecha) == month_num,
            TimeEntries.horas > 0,
        ).all()

        month_absences = Absences.query.filter(
            extract("year", Absences.fecha) == year,
            extract("month", Absences.fecha) == month_num,
        ).all()

        user_data = {
            u.id: {"hours": 0.0, "logged_days": set(), "absence_days": set()}
            for u in users
        }

        for i in month_time_entries:
            if i.usuario_id in user_data and i.fecha:
                user_data[i.usuario_id]["hours"] += float(i.horas)
                user_data[i.usuario_id]["logged_days"].add(i.fecha.day)

        for a in month_absences:
            if a.usuario_id in user_data and a.fecha:
                user_data[a.usuario_id]["absence_days"].add(a.fecha.day)

        audit_users = []
        for u in users:
            data = user_data[u.id]
            actual_hours = data["hours"]
            logged_days = data["logged_days"]
            absence_days = data["absence_days"]

            missing_days = []
            total_work_days = 0

            for day in range(1, num_days + 1):
                current_date = date(year, month_num, day)
                if current_date.weekday() < 5: 
                    total_work_days += 1
                    if day not in logged_days and day not in absence_days:
                        missing_days.append(str(day))

            if len(missing_days) == 0:
                status = "complete"
            elif len(missing_days) == total_work_days and actual_hours == 0:
                status = "empty"
            else:
                status = "incomplete"

            audit_users.append(
                {
                    "id": u.id,
                    "name": u.nombre,
                    "role": u.rol,
                    "actualHours": actual_hours,
                    "status": status,
                    "missingDays": missing_days,
                }
            )

        return {"isMonthClosed": is_month_closed, "users": audit_users}, 200

    except Exception as e:
        print(f"Error en get_closing_audit: {e}")
        return {"error": str(e)}, 500


def toggle_closing_month(month, action):
    try:
        year, month_num = map(int, month.split("-"))

        is_closed = True if action == "close" else False

        record = MonthClosings.query.filter_by(anio=year, mes=month_num).first()

        if record:
            record.esta_cerrado = is_closed
            record.fecha_cierre = datetime.utcnow()
        else:
            new_closing = MonthClosings(
                anio=year,
                mes=month_num,
                esta_cerrado=is_closed,
                fecha_cierre=datetime.utcnow(),
            )
            db.session.add(new_closing)

        db.session.commit()
        
        action_msg = "closed" if action == "close" else "opened"
        return {"message": f"Month {action_msg} successfully"}, 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en toggle_closing_month: {e}")
        return {"error": str(e)}, 500