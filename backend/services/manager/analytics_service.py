from database.db import db
from models.time_entries import TimeEntries
from models.projects import Projects
from models.users import Users
from models.absences import Absences
from sqlalchemy import func, extract, and_


def get_analytics_data(mes):
    try:
        anio, mes_num = mes.split("-")

        proyectos_query = (
            db.session.query(
                Projects.nombre.label("nombre"),
                func.sum(TimeEntries.horas).label("total_horas"),
            )
            .join(TimeEntries.proyecto)
            .filter(
                extract("year", TimeEntries.fecha) == anio,
                extract("month", TimeEntries.fecha) == mes_num,
            )
            .group_by(Projects.nombre)
            .all()
        )

        proyectos_stats = []
        total_horas_imputadas = 0

        for p in proyectos_query:
            horas = float(p.total_horas or 0)
            total_horas_imputadas += horas
            proyectos_stats.append(
                {
                    "nombre": p.nombre,
                    "horas": horas,
                    "color": "bg-blue-500",
                    "contributors": [],
                }
            )

        # 2. Carga de Empleados (LEFT JOIN con condiciones)
        empleados_query = (
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
                    extract("year", TimeEntries.fecha) == anio,
                    extract("month", TimeEntries.fecha) == mes_num,
                ),
            )
            .filter(Users.activo == True)
            .group_by(Users.id, Users.nombre, Users.rol)
            .all()
        )

        carga_empleados = []
        total_capacidad_teorica = 0

        for u in empleados_query:
            # Capacidad teórica aproximada (160h/mes)
            capacidad = 160
            total_capacidad_teorica += capacidad

            nombres = u.nombre.split() if u.nombre else []
            avatar = (
                (nombres[0][0] + (nombres[1][0] if len(nombres) > 1 else "")).upper()
                if nombres
                else "XX"
            )

            carga_empleados.append(
                {
                    "nombre": u.nombre,
                    "horas": float(u.horas_imputadas or 0),
                    "capacidad": capacidad,
                    "rol": u.rol,
                    "avatar": avatar,
                    "trend": "equal",
                }
            )

        ausencias_db = Absences.query.filter(
            extract("year", Absences.fecha) == anio,
            extract("month", Absences.fecha) == mes_num,
        ).all()

        ausencias = []
        for a in ausencias_db:
            ausencias.append(
                {
                    "date": a.fecha.strftime("%Y-%m-%d") if a.fecha else "",
                    "nombre": a.usuario.nombre if a.usuario else "Desconocido",
                    "type": a.tipo,
                    "userId": a.usuario_id,
                }
            )

        return {
            "totalHorasImputadas": total_horas_imputadas,
            "totalCapacidadTeorica": total_capacidad_teorica,
            "proyectosStats": proyectos_stats,
            "cargaEmpleados": carga_empleados,
            "ausencias": ausencias,
        }, 200

    except Exception as e:
        print(f"Error en analytics_service: {e}")
        return {"error": str(e)}, 500
