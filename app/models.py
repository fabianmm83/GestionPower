from app import db
from datetime import datetime
from enum import Enum
from sqlalchemy import CheckConstraint

# Enumeración para el tipo de movimiento
class TipoMovimiento(Enum):
    ENTRADA = 'entrada'
    SALIDA = 'salida'

# Modelo de Producto
class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con MovimientoInventario
    movimientos = db.relationship('MovimientoInventario', back_populates='producto', cascade="all, delete-orphan")

    # Relación con VentaProducto
    ventas = db.relationship('VentaProducto', back_populates='producto', cascade="all, delete-orphan")  # <-- Agregar esta línea

    def __repr__(self):
        return f"<Producto {self.nombre}>"

# Modelo de Venta
class Venta(db.Model):
    __tablename__ = 'venta'
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
    producto = db.relationship('Producto', back_populates='ventas')  # Relación con Producto

    def __repr__(self):
        return f"<VentaProducto {self.venta_id}-{self.producto_id}>"

# Modelo de Categoría
class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

# Modelo de MovimientoInventario
class MovimientoInventario(db.Model):
    __tablename__ = 'movimientos_inventario'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)  # Clave foránea
    tipo = db.Column(db.Enum('ENTRADA', 'SALIDA', name='tipomovimiento'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Producto
    producto = db.relationship('Producto', back_populates='movimientos')  # Relación con Producto

    def __init__(self, producto_id, tipo, cantidad):
        self.producto_id = producto_id
        self.tipo = tipo.upper()  # Convertir siempre a mayúsculas
        self.cantidad = cantidad

    def __repr__(self):
        return f"<MovimientoInventario {self.id}>"