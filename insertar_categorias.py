# insertar_categorias.py
from config.config import config  # Importa la configuración
from app import create_app, db  # Importa create_app y db desde app
from app.models import Categoria  # Importa el modelo Categoria

# Crear la aplicación Flask
app = create_app()

# Crear un contexto de aplicación
with app.app_context():
    # Verificar si ya existen categorías en la base de datos
    if Categoria.query.count() == 0:
        # Insertar las categorías predeterminadas
        for categoria_nombre in config.CATEGORIAS_PREDETERMINADAS:
            categoria = Categoria(nombre=categoria_nombre)
            db.session.add(categoria)
        
        # Guardar los cambios en la base de datos
        db.session.commit()
        print("Categorías predeterminadas insertadas correctamente.")
    else:
        print("Ya existen categorías en la base de datos. No se insertaron nuevas categorías.")