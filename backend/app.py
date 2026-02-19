from flask import Flask
from flask_cors import CORS
from controllers.proyectos_controller import proyectos_bp

# Importamos nuestros controladores
from controllers.usuarios_controller import usuarios_bp

app = Flask(__name__)
CORS(app)

# Registramos los módulos (Blueprints)
app.register_blueprint(usuarios_bp)
app.register_blueprint(proyectos_bp)
# Cuando creemos proyectos, simplemente añadiremos: app.register_blueprint(proyectos_bp)

if __name__ == '__main__':
    # Usamos 0.0.0.0 para que Docker pueda exponer el puerto correctamente
    app.run(debug=True, host='0.0.0.0', port=5000)