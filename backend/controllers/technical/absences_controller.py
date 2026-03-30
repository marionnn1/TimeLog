from flask import Blueprint, request, jsonify
from auth import token_required # <-- VIGILANTE DE SEGURIDAD
from services.technical.absences_service import (
    obtener_ausencias_mes,
    guardar_ausencias,
    eliminar_ausencias,
)
from datetime import datetime
from errors import APIError

absences_bp = Blueprint("absences", __name__)


@absences_bp.route("/api/absences", methods=["GET"])
@token_required # <-- CANDADO
def get_ausencias():
    try:
        mes = int(request.args.get("mes", datetime.now().month))
        anio = int(request.args.get("anio", datetime.now().year))
    except (ValueError, TypeError):
        mes = datetime.now().month
        anio = datetime.now().year

    data = obtener_ausencias_mes(mes, anio)

    return jsonify({"status": "success", "data": data}), 200


@absences_bp.route("/api/absences", methods=["POST"])
@token_required # <-- CANDADO
def create_ausencias():
    d = request.json
    if not d:
        raise APIError("No se enviaron datos en la petición", status_code=400)

    guardar_ausencias(
        d.get("usuario_id"), d.get("fechas"), d.get("tipo"), d.get("comentario", "")
    )

    return (
        jsonify(
            {"status": "success", "message": "Ausencias registradas correctamente"}
        ),
        200,
    )


@absences_bp.route("/api/absences", methods=["DELETE"])
@token_required # <-- CANDADO
def delete_ausencia():
    d = request.json
    if not d:
        raise APIError("No se enviaron datos en la petición", status_code=400)

    eliminar_ausencias(d.get("usuario_id"), d.get("fechas"))

    return (
        jsonify({"status": "success", "message": "Ausencias eliminadas correctamente"}),
        200,
    )