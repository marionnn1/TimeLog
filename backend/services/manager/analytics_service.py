from database.db import db
from models.time_entries import TimeEntries
from models.projects import Projects
from models.users import Users
from models.absences import Absences
from sqlalchemy import func, extract, and_

def get_analytics_data(month):
    try:
        year, month_num = month.split("-")

        projects_query = (
            db.session.query(
                Projects.nombre.label("nombre"),
                func.sum(TimeEntries.horas).label("total_horas"),
            )
            .join(TimeEntries.proyecto)
            .filter(
                extract("year", TimeEntries.fecha) == year,
                extract("month", TimeEntries.fecha) == month_num,
            )
            .group_by(Projects.nombre)
            .all()
        )

        project_stats = []
        total_logged_hours = 0

        for p in projects_query:
            hours = float(p.total_horas or 0)
            total_logged_hours += hours
            project_stats.append(
                {
                    "name": p.nombre,
                    "hours": hours,
                    "color": "bg-blue-500",
                    "contributors": [],
                }
            )

        employees_query = (
            db.session.query(
                Users.id,
                Users.nombre,
                Users.rol,
                func.sum(TimeEntries.horas).label("horas_imputadas"),
            )
            .outerjoin(
                TimeEntries,
                and_(
                    Users.id == TimeEntries.usuario_id,
                    extract("year", TimeEntries.fecha) == year,
                    extract("month", TimeEntries.fecha) == month_num,
                ),
            )
            .filter(Users.activo == True)
            .group_by(Users.id, Users.nombre, Users.rol)
            .all()
        )

        employee_workload = []
        total_theoretical_capacity = 0

        for u in employees_query:
            capacity = 160
            total_theoretical_capacity += capacity

            names = u.nombre.split() if u.nombre else []
            avatar = (
                (names[0][0] + (names[1][0] if len(names) > 1 else "")).upper()
                if names
                else "XX"
            )

            employee_workload.append(
                {
                    "name": u.nombre,
                    "hours": float(u.horas_imputadas or 0),
                    "capacity": capacity,
                    "role": u.rol,
                    "avatar": avatar,
                    "trend": "equal",
                }
            )

        absences_db = Absences.query.filter(
            extract("year", Absences.fecha) == year,
            extract("month", Absences.fecha) == month_num,
        ).all()

        absences = []
        for a in absences_db:
            absences.append(
                {
                    "date": a.fecha.strftime("%Y-%m-%d") if a.fecha else "",
                    "name": a.usuario.nombre if a.usuario else "Desconocido",
                    "type": a.tipo,
                    "userId": a.usuario_id,
                }
            )

        return {
            "totalLoggedHours": total_logged_hours,
            "totalTheoreticalCapacity": total_theoretical_capacity,
            "projectStats": project_stats,
            "employeeWorkload": employee_workload,
            "absences": absences,
        }, 200

    except Exception as e:
        print(f"Error en analytics_service: {e}")
        return {"error": str(e)}, 500