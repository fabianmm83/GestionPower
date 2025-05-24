from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config.config import config
import logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Carga la configuración según el entorno
    app.config.from_object(config)

    # Configuración de logging
    logging.basicConfig(
        level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Inicializa la base de datos y Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)

    # Registra el Blueprint de rutas
    from app.routes import routes
    app.register_blueprint(routes)

    # Crea las tablas en la base de datos (si no existen)
    with app.app_context():
        db.create_all()

    # Mensajes de inicio
    logger.debug(f"Modo DEBUG activado: {app.config['DEBUG']}")
    logger.debug(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    if app.debug:
        port = app.config.get("PORT", 5000)
        logger.info(f"\n{'*' * 50}")
        logger.info(f"* Servidor corriendo en: http://127.0.0.1:{port}")
        logger.info(f"* Modo DEBUG: {app.config['DEBUG']}")
        logger.info(f"{'*' * 50}\n")
        # Activa el debug mode de Flask explícitamente
        app.config.update(
            DEBUG=True,
            ENV='development',
            FLASK_DEBUG=1
        )

    return app