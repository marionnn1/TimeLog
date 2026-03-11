from database.db import db
from datetime import datetime

class Audits(db.Model):
    __tablename__ = 'Auditoria'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column('Fecha', db.DateTime, default=datetime.utcnow)
    actor_id = db.Column('ActorId', db.Integer, nullable=True) 
    actor_nombre = db.Column('ActorNombre', db.String(100), nullable=False)
    accion = db.Column('Accion', db.String(50), nullable=False)
    gravedad = db.Column('Gravedad', db.String(20), default='info')
    detalle = db.Column('Detalle', db.String(None), nullable=False)