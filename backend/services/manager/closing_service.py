import calendar
from datetime import date, datetime
from database.db import db
from models.users import Users
from models.time_entries import TimeEntries
from models.absences import Absences
from models.month_closings import MonthClosings
from sqlalchemy import extract


def get_closing_audit(mes):
    try:
        anio, mes_num = map(int, mes.split("-"))

        # 1. Comprobar si el mes está cerrado
        registro_cierre = MonthClosings.query.filter_by(anio=anio, mes=mes_num).first()
        mes_cerrado = bool(registro_cierre.esta_cerrado) if registro_cierre else False

        # Total de días del mes seleccionado
        _, num_days = calendar.monthrange(anio, mes_num)

        # 2. Obtener usuarios activos
        usuarios = Users.query.filter_by(activo=True).all()

        # 3. Traer TODAS las imputaciones y ausencias del mes
        imputaciones_mes = TimeEntries.query.filter(
            extract("year", TimeEntries.fecha) == anio,
            extract("month", TimeEntries.fecha) == mes_num,
            TimeEntries.horas > 0,
        ).all()

        ausencias_mes = Absences.query.filter(
            extract("year", Absences.fecha) == anio,
            extract("month", Absences.fecha) == mes_num,
        ).all()

        # Pre-procesamos los datos añadiendo un diccionario de 'proyectos'
        datos_usuarios = {
            u.id: {
                "horas": 0.0, 
                "dias_imputados": set(), 
                "dias_ausencias": set(),
                "proyectos": {} # Agrupación de horas por Cliente y Proyecto
            }
            for u in usuarios
        }

        for i in imputaciones_mes:
            if i.usuario_id in datos_usuarios and i.fecha:
                horas_imp = float(i.horas)
                datos_usuarios[i.usuario_id]["horas"] += horas_imp
                datos_usuarios[i.usuario_id]["dias_imputados"].add(i.fecha.day)

                # Obtener nombres de proyecto y cliente
                p_nombre = i.proyecto.nombre if i.proyecto else "Sin Proyecto"
                c_nombre = i.proyecto.cliente.nombre if i.proyecto and i.proyecto.cliente else "Sin Cliente"
                
                # Clave compuesta por Cliente y Proyecto
                key_proy = (c_nombre, p_nombre)

                # Sumar horas a ese proyecto específico
                if key_proy not in datos_usuarios[i.usuario_id]["proyectos"]:
                    datos_usuarios[i.usuario_id]["proyectos"][key_proy] = 0.0
                datos_usuarios[i.usuario_id]["proyectos"][key_proy] += horas_imp

        for a in ausencias_mes:
            if a.usuario_id in datos_usuarios and a.fecha:
                datos_usuarios[a.usuario_id]["dias_ausencias"].add(a.fecha.day)

        # 4. Construimos la respuesta evaluando a cada usuario
        usuarios_auditoria = []
        for u in usuarios:
            datos = datos_usuarios[u.id]
            horas_reales = datos["horas"]
            dias_imputados = datos["dias_imputados"]
            dias_ausencias = datos["dias_ausencias"]
            
            # Formatear el desglose como una lista de objetos separados
            desglose_proyectos = [
                {"cliente": k[0], "proyecto": k[1], "horas": v} 
                for k, v in datos["proyectos"].items()
            ]

            dias_faltantes = []
            dias_laborables_totales = 0

            for day in range(1, num_days + 1):
                current_date = date(anio, mes_num, day)
                if current_date.weekday() < 5:  # 0-4 representan Lunes a Viernes
                    dias_laborables_totales += 1
                    if day not in dias_imputados and day not in dias_ausencias:
                        dias_faltantes.append(str(day))

            # Determinar el estado del usuario
            if len(dias_faltantes) == 0:
                estado = "completo"
            elif len(dias_faltantes) == dias_laborables_totales and horas_reales == 0:
                estado = "vacio"
            else:
                estado = "incompleto"

            usuarios_auditoria.append(
                {
                    "id": u.id,
                    "nombre": u.nombre,
                    "rol": u.rol,
                    "horasReales": horas_reales,
                    "estado": estado,
                    "diasFaltantes": dias_faltantes,
                    "desgloseProyectos": desglose_proyectos # Mandamos la lista limpia
                }
            )

        return {"mesCerrado": mes_cerrado, "usuarios": usuarios_auditoria}, 200

    except Exception as e:
        print(f"Error en get_closing_audit: {e}")
        return {"error": str(e)}, 500


def toggle_closing_month(mes, accion):
    try:
        anio, mes_num = map(int, mes.split("-"))
        esta_cerrado = True if accion == "cerrar" else False

        registro = MonthClosings.query.filter_by(anio=anio, mes=mes_num).first()

        if registro:
            registro.esta_cerrado = esta_cerrado
            registro.fecha_cierre = datetime.utcnow()
        else:
            nuevo_cierre = MonthClosings(
                anio=anio,
                mes=mes_num,
                esta_cerrado=esta_cerrado,
                fecha_cierre=datetime.utcnow(),
            )
            db.session.add(nuevo_cierre)

        db.session.commit()
        return {"message": f"Mes {accion} correctamente"}, 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en toggle_closing_month: {e}")
        return {"error": str(e)}, 500