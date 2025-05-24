import sqlite3
from pathlib import Path

def modificar_tabla_productos():
    # Configura la ruta a tu base de datos SQLite
    db_path = Path("instance") / "tienda.db"  # Ajusta según tu estructura
    
    # Verifica si la base de datos existe
    if not db_path.exists():
        print(f"Error: No se encontró la base de datos en {db_path}")
        return
    
    try:
        # Conecta a la base de datos
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("Comenzando modificación de la tabla producto...")
        
        # 1. Verificar si ya existen las columnas nuevas
        cursor.execute("PRAGMA table_info(producto)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'precio_venta' in columns and 'costo_adquisicion' in columns:
            print("Las columnas ya existen. No se realizaron cambios.")
            return
        
        # 2. Crear una tabla temporal con la nueva estructura
        print("Creando tabla temporal...")
        cursor.execute("""
        CREATE TABLE producto_temp (
            id INTEGER NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            precio_venta FLOAT NOT NULL DEFAULT 100,
            costo_adquisicion FLOAT NOT NULL DEFAULT 100,
            cantidad INTEGER DEFAULT 0,
            categoria_id INTEGER NOT NULL,
            activo BOOLEAN DEFAULT 1,
            fecha_registro DATETIME,
            cantidad_vendida INTEGER DEFAULT 0,
            PRIMARY KEY (id),
            FOREIGN KEY(categoria_id) REFERENCES categoria (id)
        )
        """)
        
        # 3. Copiar los datos de la tabla original a la temporal
        print("Copiando datos a tabla temporal...")
        cursor.execute("""
        INSERT INTO producto_temp (
            id, nombre, descripcion, precio_venta, costo_adquisicion,
            cantidad, categoria_id, activo, fecha_registro, cantidad_vendida
        )
        SELECT 
            id, nombre, descripcion, 
            CASE WHEN precio IS NULL THEN 100 ELSE precio END,  -- precio_venta
            100,  -- costo_adquisicion (valor default)
            cantidad, categoria_id, activo, fecha_registro, cantidad_vendida
        FROM producto
        """)
        
        # 4. Eliminar la tabla original
        print("Eliminando tabla original...")
        cursor.execute("DROP TABLE producto")
        
        # 5. Renombrar la tabla temporal a producto
        print("Renombrando tabla temporal...")
        cursor.execute("ALTER TABLE producto_temp RENAME TO producto")
        
        # 6. Actualizar la tabla venta_producto si es necesario
        try:
            cursor.execute("ALTER TABLE venta_producto RENAME COLUMN precio TO precio_venta")
            print("Columna 'precio' en venta_producto renombrada a 'precio_venta'")
        except sqlite3.OperationalError as e:
            print(f"No se pudo renombrar columna en venta_producto: {str(e)}")
        
        # Confirmar los cambios
        conn.commit()
        print("¡Modificación completada con éxito!")
        
    except sqlite3.Error as e:
        print(f"Error al modificar la base de datos: {str(e)}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    modificar_tabla_productos()
    input("Presiona Enter para salir...")