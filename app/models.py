from app import db
from datetime import datetime

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relación con ventas a través de la tabla intermedia
    ventas = db.relationship('VentaProducto', back_populates='producto')

    def __repr__(self):
        return f'<Producto {self.nombre}>'

# Modelo de Venta
# En models.py

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)

    # Relación con productos a través de la tabla intermedia
    productos = db.relationship('VentaProducto', back_populates='venta', cascade="all, delete-orphan")

class VentaProducto(db.Model):
    __tablename__ = 'venta_producto'
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id', ondelete="CASCADE"), primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id', ondelete="CASCADE"), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    # Relaciones inversas
    venta = db.relationship('Venta', back_populates='productos')
    producto = db.relationship('Producto', back_populates='ventas')
    
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'