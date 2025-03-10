from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto dinámico o 5000 por defecto
    print(f"Servidor corriendo muy bien en: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)  # Usa el servidor de desarrollo de Flask