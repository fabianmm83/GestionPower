from app import create_app
from flask_migrate import Migrate, upgrade

# Crear la aplicación
app = create_app()

# Ejecutar las migraciones dentro del contexto de la aplicación
with app.app_context():
    upgrade()  # Esto aplica las migraciones pendientes
