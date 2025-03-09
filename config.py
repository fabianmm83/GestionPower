import os

class Config:
    # Usa la URL de PostgreSQL en lugar de SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 
        'postgresql://powerdb_821m_user:bpboqcKOK4PbcCmVi77rbEjdnuZbVcvX@dpg-cv6eklnnoe9s73bukq3g-a/powerdb_821m'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Lista de categorías predeterminadas (variable global)
CATEGORIAS_PREDETERMINADAS = [
    "SHORT V",
    "Leggins",
    "Enterizo",
    "Short sencillo",
    "Top",
    "Playeras oversize"  
]