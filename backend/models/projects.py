from database.db import db
from datetime import datetime

class Projects(db.Model):
    __tablename__ = 'Proyectos'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column('ClienteId', db.Integer, db.ForeignKey('Clientes.Id'), nullable=True)
    nombre = db.Column('Nombre', db.String(100), nullable=False)
    codigo = db.Column('Codigo', db.String(50))
    tipo = db.Column('Tipo', db.String(20), default='Proyecto')
    jefe_proyecto_id = db.Column('JefeProyectoId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)
    
    estado = db.Column('Estado', db.String(20), default='Activo')
    fecha_inicio = db.Column('FechaInicio', db.Date, nullable=True)
    fecha_fin = db.Column('FechaFin', db.Date, nullable=True)
    fecha_creacion = db.Column('FechaCreacion', db.DateTime, default=datetime.utcnow)
    fecha_desactivacion = db.Column('FechaDesactivacion', db.DateTime, nullable=True)
    desactivado_por = db.Column('DesactivadoPorUsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)

    asignaciones = db.relationship('Assignments', backref='proyecto', lazy=True)

    def to_dict(self):
        return {
            "Id": self.id,
            "ClienteId": self.cliente_id,
            "Nombre": self.nombre,
            "Codigo": self.codigo,
            "Tipo": self.tipo,
            "JefeProyectoId": self.jefe_proyecto_id,
            "Estado": self.estado
        }