from app import create_app
from flask_migrate import Migrate, upgrade

app = create_app()

with app.app_context():
    upgrade()  # Esto aplica las migraciones pendientes
