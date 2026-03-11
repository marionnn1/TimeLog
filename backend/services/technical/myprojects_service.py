from database.db import db
from models.time_entries import TimeEntries
from models.projects import Projects
from models.clients import Clients
from models.audits import Audits
from sqlalchemy import func, extract
import traceback
from datetime import datetime, timedelta

def obtener_imputaciones_semana(usuario_id, fecha_lunes):
    try:
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
    except Exception:
        return []

def guardar_imputaciones_lote(usuario_id, filas, fechas_semana):
    try:
        for fila in filas:
            p_id = fila.get('id_proyecto')
            if not p_id: continue
            
            horas = fila.get('horas', [])
            for i in range(7):
                fecha = fechas_semana[i]
                h = float(horas[i]) if i < len(horas) and horas[i] else 0
                
                registro = TimeEntries.query.filter_by(usuario_id=usuario_id, proyecto_id=p_id, fecha=fecha).first()
                
                if registro and registro.estado == 'Aprobado':
                    registro.estado = 'Pendiente'
                    registro.horas = h
                else:
                    if registro:
                        db.session.delete(registro)
                    if h > 0:
                        nuevo = TimeEntries(usuario_id=usuario_id, proyecto_id=p_id, fecha=fecha, horas=h, estado='Borrador')
                        db.session.add(nuevo)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def obtener_analitica_mensual(usuario_id, mes, anio):
    default_data = {"proyectos": [], "totales": {"mes_real": 0, "ano_acumulado": 0, "mes_nombre": ""}}
    try:
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
    except Exception:
        import traceback
        traceback.print_exc()
        return default_data

def obtener_analitica_equipo(mes, anio):
    try:
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
    except Exception:
        traceback.print_exc()
        return []

def obtener_calendario_mensual(usuario_id, mes, anio):
    try:
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
    except Exception as e:
        print("Error en calendario:", e)
        return []

def solicitar_correccion_imputacion(usuario_id, proyecto_id, fecha, nuevas_horas, motivo):
    try:
        registro = TimeEntries.query.filter_by(
            usuario_id=usuario_id, proyecto_id=proyecto_id, fecha=fecha
        ).first()
        
        if registro:
            registro.estado = 'Pendiente'
            registro.horas = nuevas_horas
            registro.comentario = motivo
            
            detalle = f"Usuario {usuario_id} solicita cambiar a {nuevas_horas}h el proyecto {proyecto_id} en {fecha}"
            nueva_auditoria = Audits(actor_nombre='Sistema', accion='Solicitud Corrección', gravedad='warning', detalle=detalle)
            db.session.add(nueva_auditoria)
            
            db.session.commit()
            return True
        return False
    except Exception as e:
        print("Error en solicitar_correccion:", e)
        db.session.rollback()
        return False