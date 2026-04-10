import calendar
from datetime import date
from database.db import db
from models.time_entries import TimeEntries
from models.projects import Projects
from models.clients import Clients
from models.users import Users
from models.absences import Absences
from sqlalchemy import func, extract, and_
from errors import APIError

def get_max_horas_dia_usuario(usuario, fecha):
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

        distribucion_query = (
            db.session.query(
                Users.id.label("usuario_id"),
                Users.nombre.label("usuario_nombre"),
                Users.rol.label("usuario_rol"),
                Users.foto.label("usuario_foto"), # AÑADIDO: Extraer la foto
                Projects.id.label("proyecto_id"),
                Projects.nombre.label("proyecto_nombre"),
                Clients.nombre.label("cliente_nombre"),
                func.sum(TimeEntries.horas).label("horas_proyecto")
            )
            .join(TimeEntries.proyecto)
            .outerjoin(Clients, Projects.cliente_id == Clients.id)
            .join(TimeEntries.usuario)
            .filter(
                extract("year", TimeEntries.fecha) == anio,
                extract("month", TimeEntries.fecha) == mes_num,
                Users.activo == True
            )
            .group_by(Users.id, Users.nombre, Users.rol, Users.foto, Projects.id, Projects.nombre, Clients.nombre)
            .all()
        )

        desglose_por_empleado = {}
        jerarquia_clientes = {}
        total_horas_imputadas = 0

        for row in distribucion_query:
            uid = row.usuario_id
            horas = float(row.horas_proyecto)
            total_horas_imputadas += horas
            
            c_nombre = row.cliente_nombre or "Proyectos Internos / Sin Cliente"
            p_nombre = row.proyecto_nombre

            if uid not in desglose_por_empleado:
                desglose_por_empleado[uid] = {}
            
            if c_nombre not in desglose_por_empleado[uid]:
                desglose_por_empleado[uid][c_nombre] = {
                    "cliente": c_nombre,
                    "horas_totales": 0,
                    "proyectos": []
                }
            
            desglose_por_empleado[uid][c_nombre]["horas_totales"] += horas
            desglose_por_empleado[uid][c_nombre]["proyectos"].append({
                "nombre": p_nombre,
                "horas": horas
            })

            if c_nombre not in jerarquia_clientes:
                jerarquia_clientes[c_nombre] = {"cliente": c_nombre, "horas_totales": 0, "proyectos": {}}
            
            if p_nombre not in jerarquia_clientes[c_nombre]["proyectos"]:
                jerarquia_clientes[c_nombre]["proyectos"][p_nombre] = {"nombre": p_nombre, "horas_totales": 0, "usuarios": []}

            nombres = row.usuario_nombre.split() if row.usuario_nombre else []
            avatar = ((nombres[0][0] + (nombres[1][0] if len(nombres) > 1 else "")).upper() if nombres else "XX")

            jerarquia_clientes[c_nombre]["horas_totales"] += horas
            jerarquia_clientes[c_nombre]["proyectos"][p_nombre]["horas_totales"] += horas

            jerarquia_clientes[c_nombre]["proyectos"][p_nombre]["usuarios"].append({
                "usuario_id": row.usuario_id,
                "nombre": row.usuario_nombre,
                "rol": row.usuario_rol,
                "avatar": avatar,
                "foto": row.usuario_foto, # AÑADIDO: Pasamos la foto a la vista
                "horas": horas
            })

        clientes_stats = []
        for c_nombre, c_data in jerarquia_clientes.items():
            proyectos_list = []
            for p_nombre, p_data in c_data["proyectos"].items():
                p_data["usuarios"].sort(key=lambda x: x["horas"], reverse=True) 
                proyectos_list.append(p_data)
            
            proyectos_list.sort(key=lambda x: x["horas_totales"], reverse=True) 
            c_data["proyectos"] = proyectos_list
            clientes_stats.append(c_data)
            
        clientes_stats.sort(key=lambda x: x["horas_totales"], reverse=True) 

        empleados_query = (
            db.session.query(
                Users.id,
                Users.nombre,
                Users.rol,
                Users.foto, # AÑADIDO: Extraer la foto
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
            .group_by(Users.id, Users.nombre, Users.rol, Users.foto)
            .all()
        )

        carga_empleados = []
        total_capacidad_teorica = 0

        for u in empleados_query:
            usuario_obj = Users.query.get(u.id)
            capacidad = calcular_objetivo_mensual(usuario_obj, anio, mes_num)
            total_capacidad_teorica += capacidad

            nombres = u.nombre.split() if u.nombre else []
            avatar = ((nombres[0][0] + (nombres[1][0] if len(nombres) > 1 else "")).upper() if nombres else "XX")

            clientes_empleado = list(desglose_por_empleado.get(u.id, {}).values())
            clientes_empleado.sort(key=lambda x: x["horas_totales"], reverse=True)
            for c in clientes_empleado:
                c["proyectos"].sort(key=lambda x: x["horas"], reverse=True)

            carga_empleados.append({
                "nombre": u.nombre,
                "horas": float(u.horas_imputadas or 0),
                "capacidad": capacidad, 
                "rol": u.rol,
                "avatar": avatar,
                "foto": u.foto, # AÑADIDO: Pasamos la foto a la vista
                "trend": "equal",
                "desglose_clientes": clientes_empleado
            })

        return {
            "totalHorasImputadas": total_horas_imputadas,
            "totalCapacidadTeorica": total_capacidad_teorica, 
            "clientesStats": clientes_stats,
            "cargaEmpleados": carga_empleados
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error en analytics_service: {e}")
        raise APIError(str(e), status_code=500)