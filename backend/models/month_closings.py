from database.db import db
from datetime import datetime

class MonthClosings(db.Model):
    __tablename__ = 'CierreMes'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    anio = db.Column('Anio', db.Integer, nullable=False)
    mes = db.Column('Mes', db.Integer, nullable=False)
    esta_cerrado = db.Column('EstaCerrado', db.Boolean, default=True) 
    fecha_cierre = db.Column('FechaCierre', db.DateTime, default=datetime.utcnow)
    cerrado_por = db.Column('CerradoPorUsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)

    usuario = db.relationship('Users', backref='cierres', lazy=True)