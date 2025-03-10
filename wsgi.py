import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render generalmente asigna un puerto dinámico
    app.run(host="0.0.0.0", port=port, debug=False)  # No se usa en producción pero se deja por si acaso
