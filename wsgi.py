import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render generalmente asigna un puerto dinámico
    print(f"Corriendo en: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)  # No se usa en producción pero se deja por si acaso
