from database.db import db
from datetime import datetime

class TimeEntries(db.Model):
    __tablename__ = 'Imputaciones'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    usuario_id = db.Column('UsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)
    proyecto_id = db.Column('ProyectoId', db.Integer, db.ForeignKey('Proyectos.Id'), nullable=True)
    fecha = db.Column('Fecha', db.Date, nullable=False)
    horas = db.Column('Horas', db.Numeric(4, 2), nullable=False)
    comentario = db.Column('Comentario', db.String(None)) 
    estado = db.Column('Estado', db.String(20), default='Borrador') 
    
    validado_por = db.Column('ValidadoPorUsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)
    fecha_validacion = db.Column('FechaValidacion', db.DateTime, nullable=True)
    fecha_creacion = db.Column('FechaCreacion', db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Users', foreign_keys=[usuario_id], backref='imputaciones', lazy=True)
    validador = db.relationship('Users', foreign_keys=[validado_por], lazy=True)
    proyecto = db.relationship('Projects', backref='imputaciones', lazy=True)