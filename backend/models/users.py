from database.db import db
from datetime import datetime


class Users(db.Model):
    __tablename__ = "Usuarios"

    id = db.Column("Id", db.Integer, primary_key=True, autoincrement=True)
    oid_azure = db.Column("OidAzure", db.String(100), unique=True)
    nombre = db.Column("Nombre", db.String(100), nullable=False)
    rol = db.Column("Rol", db.String(20))
    sede = db.Column("Sede", db.String(50))
    activo = db.Column("Activo", db.Boolean, default=True)

    tipo_contrato = db.Column("TipoContrato", db.String(20), default="40H")
    horas_verano = db.Column("HorasDiariasVerano", db.Numeric(4, 2), default=7.00)
    horas_invierno_lj = db.Column("HorasInvierno_L_J", db.Numeric(4, 2), default=8.50)
    horas_invierno_v = db.Column(
        "HorasInvierno_Viernes", db.Numeric(4, 2), default=6.50
    )

    fecha_creacion = db.Column("FechaCreacion", db.DateTime, default=datetime.utcnow)
    fecha_desactivacion = db.Column("FechaDesactivacion", db.DateTime, nullable=True)
    desactivado_por = db.Column(
        "DesactivadoPorUsuarioId",
        db.Integer,
        db.ForeignKey("Usuarios.Id"),
        nullable=True,
    )

    def to_dict(self):
        return {
            "Id": self.id,
            "OidAzure": self.oid_azure,
            "Nombre": self.nombre,
            "Rol": self.rol,
            "Sede": self.sede,
            "Activo": self.activo,
        }
