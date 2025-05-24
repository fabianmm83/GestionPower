from dotenv import load_dotenv
import os


load_dotenv()

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
        'postgresql://gestionpowerdb_user:X86wwtFNPvp1cwfIEXf16LtemOWSM55A@dpg-cv75utjtq21c73amin10-a.oregon-postgres.render.com/gestionpowerdb'
    )
                    

# Selecciona la configuración según el entorno
config = ProductionConfig() if os.getenv('FLASK_ENV') == 'production' else DevelopmentConfig()

# Aquí puedes agregar algunas verificaciones de depuración si lo deseas
print(f"Usando la base de datos de {config.SQLALCHEMY_DATABASE_URI}")

print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
