class APIError(Exception):
    """
    Excepción personalizada para lanzar errores controlados desde los servicios.
    Ejemplo: raise APIError("El usuario ya existe", 400)
    """
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code