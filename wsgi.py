from app import create_app
from waitress import serve
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto dinámico o 5000 por defecto
    print(f"Servidor corriendo en: http://127.0.0.1:{port}")  # Mensaje de depuración
    serve(app, host="0.0.0.0", port=port)  # Usa Waitress para servir la aplicación