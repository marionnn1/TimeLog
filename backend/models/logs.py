from database.db import db
from datetime import datetime

class Logs(db.Model):
    __tablename__ = 'Logs'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    fecha = db.Column('Fecha', db.DateTime, default=datetime.utcnow)
    actor_id = db.Column('ActorId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)
    accion = db.Column('Accion', db.String(50), nullable=False) 
    detalle = db.Column('Detalle', db.String(255))
    gravedad = db.Column('Gravedad', db.String(20), default='info')