import calendar
from datetime import date, datetime
from database.db import db
from models.users import Users
from models.time_entries import TimeEntries
from models.absences import Absences
from models.month_closings import MonthClosings
from sqlalchemy import extract
from models.audits import Audits
from errors import APIError

def get_closing_audit(mes):
    anio, mes_num = map(int, mes.split("-"))

    registro_cierre = MonthClosings.query.filter_by(anio=anio, mes=mes_num).first()
    mes_cerrado = bool(registro_cierre.esta_cerrado) if registro_cierre else False
    _, num_days = calendar.monthrange(anio, mes_num)
    usuarios = Users.query.filter_by(activo=True).all()
    
    imputaciones_mes = TimeEntries.query.filter(
        extract("year", TimeEntries.fecha) == anio,
        extract("month", TimeEntries.fecha) == mes_num,
        TimeEntries.horas > 0,
    ).all()

    ausencias_mes = Absences.query.filter(
        extract("year", Absences.fecha) == anio,
        extract("month", Absences.fecha) == mes_num,
    ).all()

    datos_usuarios = {
        u.id: {"horas": 0.0, "horas_por_dia": {}, "dias_ausencias": set(), "proyectos": {}}
        for u in usuarios
    }

    for i in imputaciones_mes:
        if i.usuario_id in datos_usuarios and i.fecha:
            horas_imp = float(i.horas)
            datos_usuarios[i.usuario_id]["horas"] += horas_imp

            day = datetime.strptime(i.fecha.split('T')[0], "%Y-%m-%d").day if isinstance(i.fecha, str) else i.fecha.day
            datos_usuarios[i.usuario_id]["horas_por_dia"][day] = datos_usuarios[i.usuario_id]["horas_por_dia"].get(day, 0.0) + horas_imp

            p_nombre = i.proyecto.nombre if i.proyecto else "Sin Proyecto"
            c_nombre = i.proyecto.cliente.nombre if i.proyecto and i.proyecto.cliente else "Sin Cliente"

            key_proy = (c_nombre, p_nombre)

            if key_proy not in datos_usuarios[i.usuario_id]["proyectos"]:
                datos_usuarios[i.usuario_id]["proyectos"][key_proy] = 0.0
            datos_usuarios[i.usuario_id]["proyectos"][key_proy] += horas_imp

    for a in ausencias_mes:
        if a.usuario_id in datos_usuarios and a.fecha:
            day = datetime.strptime(a.fecha.split('T')[0], "%Y-%m-%d").day if isinstance(a.fecha, str) else a.fecha.day
            datos_usuarios[a.usuario_id]["dias_ausencias"].add(day)

    usuarios_auditoria = []
    for u in usuarios:
        datos = datos_usuarios[u.id]
        horas_reales = datos["horas"]
        horas_por_dia = datos["horas_por_dia"]
        dias_ausencias = datos["dias_ausencias"]

        desglose_proyectos = [{"cliente": k[0], "proyecto": k[1], "horas": v} for k, v in datos["proyectos"].items()]

        dias_faltantes = []
        dias_laborables_totales = 0

        for day in range(1, num_days + 1):
            current_date = date(anio, mes_num, day)

            alta_date = None
            if u.fecha_alta:
                if isinstance(u.fecha_alta, str):
                    alta_date = datetime.strptime(u.fecha_alta.split('T')[0], "%Y-%m-%d").date()
                else:
                    alta_date = u.fecha_alta.date() if hasattr(u.fecha_alta, 'date') else u.fecha_alta
                    
            if alta_date and current_date < alta_date:
                continue
                
            baja_date = None
            if u.fecha_desactivacion:
                if isinstance(u.fecha_desactivacion, str):
                    baja_date = datetime.strptime(u.fecha_desactivacion.split('T')[0], "%Y-%m-%d").date()
                else:
                    baja_date = u.fecha_desactivacion.date() if hasattr(u.fecha_desactivacion, 'date') else u.fecha_desactivacion
                    
            if baja_date and current_date > baja_date:
                continue

            if current_date.weekday() < 5: 
                dias_laborables_totales += 1
                if day not in dias_ausencias:
                    
                    horas_imputadas_hoy = horas_por_dia.get(day, 0.0)
                    mes_verano = mes_num in [7, 8] 
                    es_viernes = current_date.weekday() == 4
                    if mes_verano:
                        horas_esperadas = float(u.horas_verano if getattr(u, 'horas_verano', None) is not None else 7.0)
                    elif es_viernes:
                        horas_esperadas = float(u.horas_invierno_v if getattr(u, 'horas_invierno_v', None) is not None else 6.5)
                    else:
                        horas_esperadas = float(u.horas_invierno_lj if getattr(u, 'horas_invierno_lj', None) is not None else 8.5)
                    if horas_imputadas_hoy < (horas_esperadas - 0.01):
                        dias_faltantes.append(str(day))
        if len(dias_faltantes) == 0:
            estado = "completo"
        elif len(dias_faltantes) == dias_laborables_totales and horas_reales == 0:
            estado = "vacio"
        else:
            estado = "incompleto"

        usuarios_auditoria.append({
            "id": u.id, "nombre": u.nombre, "rol": u.rol,
            "foto": getattr(u, 'foto', None),
            "horasReales": horas_reales, "estado": estado,
            "diasFaltantes": dias_faltantes, "desgloseProyectos": desglose_proyectos 
        })

    return {"mesCerrado": mes_cerrado, "usuarios": usuarios_auditoria}

def toggle_closing_month(mes, accion, manager_id=None):
    anio, mes_num = map(int, mes.split("-"))
    esta_cerrado = True if accion == "cerrar" else False

    manager = Users.query.get(manager_id) if manager_id else None
    manager_nombre = manager.nombre if manager else "Sistema/Admin"

    registro = MonthClosings.query.filter_by(anio=anio, mes=mes_num).first()

    if registro:
        registro.esta_cerrado = esta_cerrado
        registro.fecha_cierre = datetime.utcnow()
    else:
        nuevo_cierre = MonthClosings(anio=anio, mes=mes_num, esta_cerrado=esta_cerrado, fecha_cierre=datetime.utcnow())
        db.session.add(nuevo_cierre)

    accion_str = "Cierre de Mes" if esta_cerrado else "Reapertura de Mes"
    detalle = f"El usuario {manager_nombre} (ID:{manager_id}) ha {'cerrado' if esta_cerrado else 'reabierto'} el mes {mes}"
    nueva_auditoria = Audits(actor_id=manager_id, actor_nombre=manager_nombre, accion=accion_str, gravedad='warning', detalle=detalle)
    db.session.add(nueva_auditoria)

    db.session.commit()
    return True