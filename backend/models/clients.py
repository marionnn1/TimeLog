from database.db import db
from datetime import datetime

class Clients(db.Model):
    __tablename__ = 'Clientes'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column('Nombre', db.String(100), nullable=False)
    codigo = db.Column('Codigo', db.String(50))
    
    estado = db.Column('Estado', db.Boolean, default=True) 
    fecha_creacion = db.Column('FechaCreacion', db.DateTime, default=datetime.utcnow)
    fecha_desactivacion = db.Column('FechaDesactivacion', db.DateTime, nullable=True)
    desactivado_por = db.Column('DesactivadoPorUsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)

    proyectos = db.relationship('Projects', backref='cliente', lazy=True)

    def to_dict(self):
        return {
            "Id": self.id,
            "Nombre": self.nombre,
            "Codigo": self.codigo,
            "Estado": self.estado
        }