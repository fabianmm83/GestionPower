from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
    app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura'
    app.config['DEBUG'] = True  # Activa el modo debug
    
    db.init_app(app)
    migrate = Migrate(app, db)

    from app.routes import routes
    app.register_blueprint(routes)  # Se registra el Blueprint correctamente

    
    with app.app_context():
        db.create_all()

    return app
