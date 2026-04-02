from database.db import db

class Absences(db.Model):
    __tablename__ = 'Ausencias'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column('UsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=True)
    fecha = db.Column('Fecha', db.Date, nullable=False)
    tipo = db.Column('Tipo', db.String(20)) 
    comentario = db.Column('Comentario', db.String(255))

    usuario = db.relationship('Users', backref='ausencias', lazy=True)