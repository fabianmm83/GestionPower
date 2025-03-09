import os

class Config:
    # Configuración común para todos los entornos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_super_segura')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'  # Activa el modo debug

    # Lista de categorías predeterminadas (variable global)
    CATEGORIAS_PREDETERMINADAS = [
        "SHORT V",
        "Leggins",
        "Enterizo",
        "Short sencillo",
        "Top",
        "Playeras oversize"  
    ]

class DevelopmentConfig(Config):
    # Configuración para desarrollo local (usando SQLite)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///tienda.db')

class ProductionConfig(Config):
    # Configuración para producción (usando PostgreSQL en Render)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 
        'postgresql://powerdb_821m_user:bpboqcKOK4PbcCmVi77rbEjdnuZbVcvX@dpg-cv6eklnnoe9s73bukq3g-a/powerdb_821m'
    )

# Selecciona la configuración según el entorno
if os.getenv('FLASK_ENV') == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()