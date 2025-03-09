import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tienda.db'
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