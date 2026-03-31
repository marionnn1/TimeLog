from database.db import db

class AnnualDays(db.Model):
    __tablename__ = 'DiasAnuales'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column('UsuarioId', db.Integer, db.ForeignKey('Usuarios.Id'), nullable=False)
    anio = db.Column('Anio', db.Integer, nullable=False)
    
    dias_vacaciones_totales = db.Column('DiasVacacionesTotales', db.Integer, default=22)
    dias_asuntos_propios_totales = db.Column('DiasAsuntosPropiosTotales', db.Integer, default=2)
    dias_festivos_totales = db.Column('DiasFestivosTotales', db.Integer, default=14)

    __table_args__ = (db.UniqueConstraint('UsuarioId', 'Anio', name='UQ_Usuario_Anio_DiasAnuales'),)

    usuario = db.relationship('Users', backref='dias_anuales', lazy=True)

    def to_dict(self):
        return {
            "Anio": self.anio,
            "VacacionesTotales": self.dias_vacaciones_totales,
            "AsuntosPropiosTotales": self.dias_asuntos_propios_totales,
            "FestivosTotales": self.dias_festivos_totales
        }