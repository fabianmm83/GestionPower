from app import db
from datetime import datetime

# Modelo de Producto
# models.py
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con VentaProducto
    ventas = db.relationship('VentaProducto', back_populates='producto', cascade="all, delete-orphan")

    # Relación con MovimientoInventario
    movimientos = db.relationship('MovimientoInventario', back_populates='producto', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Producto {self.nombre}>"
# Modelo de Venta
class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)

    # Relación con VentaProducto
    productos = db.relationship('VentaProducto', back_populates='venta', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venta {self.id}>"

# Modelo de VentaProducto (tabla intermedia)
class VentaProducto(db.Model):
    __tablename__ = 'venta_producto'
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id', ondelete="CASCADE"), primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id', ondelete="CASCADE"), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    # Relaciones inversas
    venta = db.relationship('Venta', back_populates='productos')
    producto = db.relationship('Producto', back_populates='ventas')

    def __repr__(self):
        return f"<VentaProducto {self.venta_id}-{self.producto_id}>"

# Modelo de Categoría
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'
    
    
class MovimientoInventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' o 'salida'
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Producto
    producto = db.relationship('Producto', back_populates='movimientos')

    def __repr__(self):
        return f"<MovimientoInventario {self.id}>"