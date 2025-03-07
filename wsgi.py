from app import create_app
from waitress import serve
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Heroku asigna el puerto a través de la variable de entorno $PORT
    serve(app, host="0.0.0.0", port=port)  # Usa el puerto dinámico de Heroku
