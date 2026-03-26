from database.db import db
from models.time_entries import TimeEntries
from models.projects import Projects
from models.clients import Clients
from models.audits import Audits
from models.users import Users
from models.assignments import Assignments
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from errors import APIError

def obtener_imputaciones_semana(usuario_id, fecha_lunes):
    if isinstance(fecha_lunes, str):
        fecha_lunes = datetime.strptime(fecha_lunes, '%Y-%m-%d').date()
    fecha_domingo = fecha_lunes + timedelta(days=6)
    
    imputaciones = TimeEntries.query.filter(
        TimeEntries.usuario_id == usuario_id,
        TimeEntries.fecha >= fecha_lunes,
        TimeEntries.fecha <= fecha_domingo
    ).all()
    
    return [{
        "ProyectoId": i.proyecto_id,
        "ProyectoNombre": i.proyecto.nombre if i.proyecto else "",
        "ClienteNombre": i.proyecto.cliente.nombre if i.proyecto and i.proyecto.cliente else "",
        "Fecha": i.fecha.strftime('%Y-%m-%d'),
        "Horas": float(i.horas)
    } for i in imputaciones]

def guardar_imputaciones_lote(usuario_id, filas, fechas_semana):
    proyectos_enviados = [fila.get('id_proyecto') for fila in filas if fila.get('id_proyecto')]

    query_borrar = TimeEntries.query.filter(
        TimeEntries.usuario_id == usuario_id,
        TimeEntries.fecha.in_(fechas_semana)
    )
    
    if proyectos_enviados:
        query_borrar = query_borrar.filter(~TimeEntries.proyecto_id.in_(proyectos_enviados))
    
    entradas_borrar = query_borrar.all()
    for e in entradas_borrar:
        if e.estado != 'Aprobado': 
            db.session.delete(e)

    for fila in filas:
        p_id = fila.get('id_proyecto')
        if not p_id: continue
        
        horas = fila.get('horas', [])
        for i in range(7):
            fecha = fechas_semana[i]
            h = float(horas[i]) if i < len(horas) and horas[i] else 0
            
            registro = TimeEntries.query.filter_by(usuario_id=usuario_id, proyecto_id=p_id, fecha=fecha).first()
            
            if h == 0:
                if registro and registro.estado != 'Aprobado':
                    db.session.delete(registro)
                continue
            
            if registro and registro.estado == 'Aprobado':
                if float(registro.horas) != h:
                    registro.estado = 'Pendiente'
                    registro.horas = h
            else:
                if registro:
                    registro.horas = h
                else:
                    nuevo = TimeEntries(usuario_id=usuario_id, proyecto_id=p_id, fecha=fecha, horas=h, estado='Borrador')
                    db.session.add(nuevo)
    
    db.session.commit()
    return True

def obtener_analitica_mensual(usuario_id, mes, anio):
    total_ano = db.session.query(func.sum(TimeEntries.horas)).filter(
        TimeEntries.usuario_id == usuario_id, extract('year', TimeEntries.fecha) == anio
    ).scalar() or 0
    
    total_mes = db.session.query(func.sum(TimeEntries.horas)).filter(
        TimeEntries.usuario_id == usuario_id, 
        extract('month', TimeEntries.fecha) == mes, 
        extract('year', TimeEntries.fecha) == anio
    ).scalar() or 0

    agrupado = db.session.query(
        Projects.nombre.label('proyecto'),
        Clients.nombre.label('cliente'),
        func.sum(TimeEntries.horas).label('total_horas')
    ).join(TimeEntries.proyecto).join(Projects.cliente).filter(
        TimeEntries.usuario_id == usuario_id,
        extract('month', TimeEntries.fecha) == mes,
        extract('year', TimeEntries.fecha) == anio
    ).group_by(Projects.nombre, Clients.nombre).all()

    proyectos_data = []
    for r in agrupado:
        proyectos_data.append({
            "proyecto": r.proyecto,
            "cliente": r.cliente,
            "real": float(r.total_horas),
            "asignado_semanal": 0,
            "objetivo_mensual": 0,
            "porcentaje": 0 
        })

    return {
        "proyectos": proyectos_data,
        "totales": {
            "mes_real": float(total_mes),
            "ano_acumulado": float(total_ano),
            "mes_nombre": f"Mes {mes} / {anio}"
        }
    }

def obtener_analitica_equipo(mes, anio):
    imputaciones = TimeEntries.query.filter(
        extract('month', TimeEntries.fecha) == mes,
        extract('year', TimeEntries.fecha) == anio
    ).all()

    equipo_data = {}
    for i in imputaciones:
        u_id = i.usuario_id
        if not i.usuario or not i.proyecto: continue

        if u_id not in equipo_data:
            equipo_data[u_id] = {
                "id": u_id,
                "nombre_completo": i.usuario.nombre,
                "total_mes": 0.0,
                "proyectos_dict": {}
            }
        
        p_nombre = i.proyecto.nombre
        c_nombre = i.proyecto.cliente.nombre if i.proyecto.cliente else "Sin Cliente"
        horas = float(i.horas)
        
        equipo_data[u_id]["total_mes"] += horas
        
        if p_nombre not in equipo_data[u_id]["proyectos_dict"]:
            equipo_data[u_id]["proyectos_dict"][p_nombre] = {"proyecto": p_nombre, "cliente": c_nombre, "horas": 0.0}
        
        equipo_data[u_id]["proyectos_dict"][p_nombre]["horas"] += horas

    for u_id in equipo_data:
        equipo_data[u_id]["proyectos"] = list(equipo_data[u_id].pop("proyectos_dict").values())

    return sorted(list(equipo_data.values()), key=lambda x: x["nombre_completo"])

def obtener_calendario_mensual(usuario_id, mes, anio):
    agrupado = db.session.query(
        extract('day', TimeEntries.fecha).label('dia'),
        Clients.nombre.label('cliente'),
        Projects.id.label('proyecto_id'),
        Projects.nombre.label('proyecto'),
        func.sum(TimeEntries.horas).label('horas')
    ).join(TimeEntries.proyecto).join(Projects.cliente).filter(
        TimeEntries.usuario_id == usuario_id,
        extract('month', TimeEntries.fecha) == mes,
        extract('year', TimeEntries.fecha) == anio
    ).group_by(
        extract('day', TimeEntries.fecha), Clients.nombre, Projects.id, Projects.nombre
    ).all()
    
    return [{
        "dia": int(r.dia),
        "cliente": r.cliente,
        "proyecto_id": r.proyecto_id,
        "proyecto": r.proyecto,
        "horas": float(r.horas)
    } for r in agrupado]

def get_max_horas_dia_usuario(usuario_id, fecha_str):
    usuario = Users.query.get(usuario_id)
    if not usuario: return 8.5
    
    if isinstance(fecha_str, str):
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    else:
        fecha = fecha_str
        
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

def solicitar_correccion_imputacion(usuario_id, proyecto_id, fecha, nuevas_horas, motivo):
    usuario = Users.query.get(usuario_id)
    if not usuario:
        raise APIError("Usuario no encontrado", status_code=404)
        
    nombre_actor = usuario.nombre
    max_horas = get_max_horas_dia_usuario(usuario_id, fecha)
    
    otras_imputaciones = TimeEntries.query.filter(
        TimeEntries.usuario_id == usuario_id,
        TimeEntries.fecha == fecha,
        TimeEntries.proyecto_id != proyecto_id,
        TimeEntries.estado != 'Rechazado'
    ).all()
    
    horas_otros_proyectos = sum(float(i.horas) for i in otras_imputaciones)
    
    if (horas_otros_proyectos + float(nuevas_horas)) > max_horas:
        raise APIError(f"Límite diario superado. Tu jornada es de {max_horas}h y ya tienes {horas_otros_proyectos}h en otros proyectos.", status_code=400)

    registro = TimeEntries.query.filter_by(
        usuario_id=usuario_id, proyecto_id=proyecto_id, fecha=fecha
    ).first()
    
    if registro:
        registro.estado = 'Pendiente'
        registro.comentario = f"[Solicita cambio a {nuevas_horas}h] - Motivo: {motivo}"
    else:
        nuevo_registro = TimeEntries(
            usuario_id=usuario_id,
            proyecto_id=proyecto_id,
            fecha=fecha,
            horas=0,
            estado='Pendiente',
            comentario=f"[Solicita añadir {nuevas_horas}h] - Motivo: {motivo}"
        )
        db.session.add(nuevo_registro)
        
    detalle = f"Usuario {nombre_actor} (ID:{usuario_id}) solicita imputar {nuevas_horas}h al proyecto {proyecto_id} en {fecha}"
    nueva_auditoria = Audits(
        actor_id=usuario_id, 
        actor_nombre=nombre_actor, 
        accion='Solicitud Corrección', 
        gravedad='warning', 
        detalle=detalle
    )
    db.session.add(nueva_auditoria)
    
    db.session.commit()
    return True

def obtener_jornada(usuario_id):
    user = Users.query.get(usuario_id)
    if not user:
        raise APIError("Usuario no encontrado", status_code=404)
        
    return {
        "tipoContrato": user.tipo_contrato or '40H',
        "horasInviernoLJ": float(user.horas_invierno_lj) if user.horas_invierno_lj else 8.5,
        "horasInviernoV": float(user.horas_invierno_v) if user.horas_invierno_v else 6.5,
        "horasVerano": float(user.horas_verano) if user.horas_verano else 7.0
    }

def actualizar_jornada(usuario_id, datos):
    user = Users.query.get(usuario_id)
    if not user:
        raise APIError("Usuario no encontrado", status_code=404)
    
    user.tipo_contrato = datos.get('tipoContrato', '40H')
    user.horas_invierno_lj = datos.get('horasInviernoLJ', 8.5)
    user.horas_invierno_v = datos.get('horasInviernoV', 6.5)
    user.horas_verano = datos.get('horasVerano', 7.0)

    db.session.commit()
    return True
    
def obtener_proyectos_asignados(usuario_id):
    asignaciones = Assignments.query.filter_by(usuario_id=usuario_id, activo=True).all()
    
    resultado = []
    for a in asignaciones:
        p = a.proyecto
        if p and p.estado == 'Activo':
            resultado.append({
                "Id": p.id,
                "Nombre": p.nombre,
                "Cliente": p.cliente.nombre if p.cliente else "Sin Cliente",
                "Estado": p.estado
            })
    return sorted(resultado, key=lambda x: (x['Cliente'], x['Nombre']))