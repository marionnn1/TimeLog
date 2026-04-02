from database.db import db
from datetime import datetime

class Assignments(db.Model):
    __tablename__ = 'Asignaciones'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    proyecto_id = db.Column('ProyectoId', db.Integer, db.ForeignKey('Proyectos.Id'), nullable=False)
    usuario_id = db.Column('UsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=False)
    
    fecha_asignacion = db.Column('FechaAsignacion', db.DateTime, default=datetime.utcnow)
    
    activo = db.Column('Activo', db.Boolean, default=True)
    fecha_desactivacion = db.Column('FechaDesactivacion', db.DateTime, nullable=True)
    desactivado_por = db.Column('DesactivadoPorUsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)

    usuario = db.relationship('Users', foreign_keys=[usuario_id], backref='asignaciones', lazy=True)

    def to_dict(self):
        return {
            "Id": self.id,
            "ProyectoId": self.proyecto_id,
            "UsuarioId": self.usuario_id,
            "Activo": self.activo
        }