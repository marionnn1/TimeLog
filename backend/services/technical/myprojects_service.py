from database.db import db
from models.time_entries import TimeEntries
from models.projects import Projects
from models.clients import Clients
from models.audits import Audits
from sqlalchemy import func, extract
import traceback
from datetime import datetime, timedelta

def get_weekly_time_entries(user_id, monday_date):
    try:
        if isinstance(monday_date, str):
            monday_date = datetime.strptime(monday_date, '%Y-%m-%d').date()
        sunday_date = monday_date + timedelta(days=6)
        
        time_entries = TimeEntries.query.filter(
            TimeEntries.usuario_id == user_id,
            TimeEntries.fecha >= monday_date,
            TimeEntries.fecha <= sunday_date
        ).all()
        
        return [{
            "projectId": i.proyecto_id,
            "projectName": i.proyecto.nombre if i.proyecto else "",
            "clientName": i.proyecto.cliente.nombre if i.proyecto and i.proyecto.cliente else "",
            "date": i.fecha.strftime('%Y-%m-%d'),
            "hours": float(i.horas)
        } for i in time_entries]
    except Exception:
        return []

def save_time_entries_batch(user_id, rows, week_dates):
    try:
        for row in rows:
            # Leemos las claves en inglés enviadas desde el frontend
            p_id = row.get('projectId')
            if not p_id: continue
            
            hours = row.get('hours', [])
            for i in range(7):
                date = week_dates[i]
                h = float(hours[i]) if i < len(hours) and hours[i] else 0
                
                record = TimeEntries.query.filter_by(usuario_id=user_id, proyecto_id=p_id, fecha=date).first()
                
                if record and record.estado == 'Aprobado':
                    record.estado = 'Pendiente'
                    record.horas = h
                else:
                    if record:
                        db.session.delete(record)
                    if h > 0:
                        new_entry = TimeEntries(usuario_id=user_id, proyecto_id=p_id, fecha=date, horas=h, estado='Borrador')
                        db.session.add(new_entry)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def get_monthly_analytics(user_id, month, year):
    default_data = {"projects": [], "totals": {"monthActual": 0, "yearAccumulated": 0, "monthName": ""}}
    try:
        year_total = db.session.query(func.sum(TimeEntries.horas)).filter(
            TimeEntries.usuario_id == user_id, extract('year', TimeEntries.fecha) == year
        ).scalar() or 0
        
        month_total = db.session.query(func.sum(TimeEntries.horas)).filter(
            TimeEntries.usuario_id == user_id, 
            extract('month', TimeEntries.fecha) == month, 
            extract('year', TimeEntries.fecha) == year
        ).scalar() or 0

        grouped = db.session.query(
            Projects.nombre.label('proyecto'),
            Clients.nombre.label('cliente'),
            func.sum(TimeEntries.horas).label('total_horas')
        ).join(TimeEntries.proyecto).join(Projects.cliente).filter(
            TimeEntries.usuario_id == user_id,
            extract('month', TimeEntries.fecha) == month,
            extract('year', TimeEntries.fecha) == year
        ).group_by(Projects.nombre, Clients.nombre).all()

        projects_data = []
        for r in grouped:
            projects_data.append({
                "project": r.proyecto,
                "client": r.cliente,
                "actual": float(r.total_horas),
                "weeklyAssigned": 0,
                "monthlyGoal": 0,
                "percentage": 0 
            })

        return {
            "projects": projects_data,
            "totals": {
                "monthActual": float(month_total),
                "yearAccumulated": float(year_total),
                "monthName": f"Month {month} / {year}"
            }
        }
    except Exception:
        import traceback
        traceback.print_exc()
        return default_data

def get_team_analytics(month, year):
    try:
        time_entries = TimeEntries.query.filter(
            extract('month', TimeEntries.fecha) == month,
            extract('year', TimeEntries.fecha) == year
        ).all()

        team_data = {}
        for i in time_entries:
            u_id = i.usuario_id
            if not i.usuario or not i.proyecto: continue

            if u_id not in team_data:
                team_data[u_id] = {
                    "id": u_id,
                    "fullName": i.usuario.nombre,
                    "totalMonth": 0.0,
                    "projects_dict": {}
                }
            
            p_name = i.proyecto.nombre
            c_name = i.proyecto.cliente.nombre if i.proyecto.cliente else "Sin Cliente"
            hours = float(i.horas)
            
            team_data[u_id]["totalMonth"] += hours
            
            if p_name not in team_data[u_id]["projects_dict"]:
                team_data[u_id]["projects_dict"][p_name] = {"project": p_name, "client": c_name, "hours": 0.0}
            
            team_data[u_id]["projects_dict"][p_name]["hours"] += hours

        for u_id in team_data:
            team_data[u_id]["projects"] = list(team_data[u_id].pop("projects_dict").values())

        return sorted(list(team_data.values()), key=lambda x: x["fullName"])
    except Exception:
        import traceback
        traceback.print_exc()
        return []

def get_monthly_calendar(user_id, month, year):
    try:
        grouped = db.session.query(
            extract('day', TimeEntries.fecha).label('dia'),
            Clients.nombre.label('cliente'),
            Projects.id.label('proyecto_id'),
            Projects.nombre.label('proyecto'),
            func.sum(TimeEntries.horas).label('horas')
        ).join(TimeEntries.proyecto).join(Projects.cliente).filter(
            TimeEntries.usuario_id == user_id,
            extract('month', TimeEntries.fecha) == month,
            extract('year', TimeEntries.fecha) == year
        ).group_by(
            extract('day', TimeEntries.fecha), Clients.nombre, Projects.id, Projects.nombre
        ).all()
        
        return [{
            "day": int(r.dia),
            "client": r.cliente,
            "projectId": r.proyecto_id,
            "project": r.proyecto,
            "hours": float(r.horas)
        } for r in grouped]
    except Exception as e:
        print("Error en calendario:", e)
        return []

def request_time_entry_correction(user_id, project_id, date, new_hours, reason):
    try:
        record = TimeEntries.query.filter_by(
            usuario_id=user_id, proyecto_id=project_id, fecha=date
        ).first()
        
        if record:
            record.estado = 'Pendiente'
            record.horas = new_hours
            record.comentario = reason
            
            detail = f"Usuario {user_id} solicita cambiar a {new_hours}h el proyecto {project_id} en {date}"
            new_audit = Audits(actor_nombre='Sistema', accion='Solicitud Corrección', gravedad='warning', detalle=detail)
            db.session.add(new_audit)
            
            db.session.commit()
            return True
        return False
    except Exception as e:
        print("Error en solicitar_correccion:", e)
        db.session.rollback()
        return False