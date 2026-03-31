from flask import Blueprint, request, jsonify, g
from auth import require_auth
from services.technical.time_entries_user_service import guardar_imputaciones_lote
from errors import APIError

time_entries_user_bp = Blueprint("time_entries_user", __name__)


@time_entries_user_bp.route("/api/time-entries/user", methods=["POST"])
@require_auth
def save_imputaciones():
    data = request.json
    if not data:
        raise APIError("No se enviaron datos en la petición", status_code=400)

    usuario_id = g.usuario_actual.id
    filas = data.get("filas")
    fechas = data.get("fechas")

    if not filas or not fechas:
        raise APIError("Faltan datos obligatorios (filas, fechas)", status_code=400)

    guardar_imputaciones_lote(usuario_id, filas, fechas)

    return (
        jsonify(
            {"status": "success", "message": "Imputaciones guardadas correctamente"}
        ),
        200,
    )
