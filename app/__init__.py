from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config.config import config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Carga la configuración según el entorno
    app.config.from_object(config)

    # Inicializa la base de datos y Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)

    # Registra el Blueprint de rutas
    from app.routes import routes
    app.register_blueprint(routes)

    # Crea las tablas en la base de datos (si no existen)
    with app.app_context():
        db.create_all()

    return app