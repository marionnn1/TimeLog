import calendar
from datetime import date
from database.db import db
from models.time_entries import TimeEntries
from models.projects import Projects
from models.users import Users
from models.absences import Absences
from sqlalchemy import func, extract, and_
from errors import APIError

def get_max_horas_dia_usuario(usuario, fecha):
    """Calcula las horas que debe trabajar un usuario en un día concreto según su contrato"""
    if not usuario: return 8.5
    
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

def calcular_objetivo_mensual(usuario, anio, mes):
    """Calcula las horas laborables totales de un mes específico para un usuario"""
    _, num_dias = calendar.monthrange(anio, mes)
    total_horas = 0.0
    for dia in range(1, num_dias + 1):
        fecha_iter = date(anio, mes, dia)
        total_horas += get_max_horas_dia_usuario(usuario, fecha_iter)
    return total_horas

def get_analytics_data(mes):
    try:
        anio_str, mes_str = mes.split("-")
        anio = int(anio_str)
        mes_num = int(mes_str)

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

        distribucion_query = (
            db.session.query(
                Users.id.label("usuario_id"),
                Projects.nombre.label("proyecto_nombre"),
                func.sum(TimeEntries.horas).label("horas_proyecto")
            )
            .join(TimeEntries.proyecto)
            .join(TimeEntries.usuario)
            .filter(
                extract("year", TimeEntries.fecha) == anio,
                extract("month", TimeEntries.fecha) == mes_num,
                Users.activo == True
            )
            .group_by(Users.id, Projects.id, Projects.nombre)
            .all()
        )

        desglose_por_empleado = {}
        for row in distribucion_query:
            uid = row.usuario_id
            if uid not in desglose_por_empleado:
                desglose_por_empleado[uid] = []
            
            desglose_por_empleado[uid].append({
                "proyecto": row.proyecto_nombre,
                "horas": float(row.horas_proyecto)
            })

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
            usuario_obj = Users.query.get(u.id)
            capacidad = calcular_objetivo_mensual(usuario_obj, anio, mes_num)
            
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
                    # Añadimos el desglose aquí:
                    "desglose_proyectos": desglose_por_empleado.get(u.id, [])
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
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error en analytics_service: {e}")
        raise APIError(str(e), status_code=500)