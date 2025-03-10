from app import db
from datetime import datetime
from enum import Enum
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, Text

# Enumeración para el tipo de movimiento
class TipoMovimiento(Enum):
    ENTRADA = 'entrada'
    SALIDA = 'salida'
    
    
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    
    # Aquí cambias 'categoria' por una clave foránea
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)  # Clave foránea a 'Categoria'
    
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    cantidad_vendida = db.Column(db.Integer, default=0)

    # Relación con ProductoVariante
    variantes = db.relationship('ProductoVariante', back_populates='producto')

    # Relación con VentaProducto
    ventas = db.relationship('VentaProducto', back_populates='producto')

    # Relación con MovimientoInventario
    movimientos = db.relationship('MovimientoInventario', back_populates='producto')

    # Relación con Categoria (esto es lo que cambia)
    categoria = db.relationship('Categoria', backref='productos')

    def __repr__(self):
        return f"<Producto {self.nombre}>"

    def ventas_totales(self):
        return sum(venta.cantidad for venta in self.ventas)

    def movimientos_totales(self):
        entradas = sum(movimiento.cantidad for movimiento in self.movimientos if movimiento.tipo == TipoMovimiento.ENTRADA)
        salidas = sum(movimiento.cantidad for movimiento in self.movimientos if movimiento.tipo == TipoMovimiento.SALIDA)
        return entradas - salidas
   
    
    
    
    

class ProductoVariante(db.Model):
    __tablename__ = 'producto_variante'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50), nullable=False)  # El color de la variante
    precio_variante = db.Column(db.Float, nullable=False)  # El precio de la variante
    cantidad = db.Column(db.Integer, nullable=False)  # Cantidad disponible de esa variante
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)  # Relación con el producto principal

    # Relación con Producto
    producto = db.relationship('Producto', back_populates='variantes')

    def __repr__(self):
        return f"<ProductoVariante {self.color} - {self.producto.nombre}>"
class Venta(db.Model):
    __tablename__ = 'venta'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)

    # Relación con VentaProducto
    productos = db.relationship('VentaProducto', back_populates='venta', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venta {self.id}>"

    @staticmethod
    def ventas_por_fecha(start_date, end_date):
        return db.session.query(Venta).filter(Venta.fecha >= start_date, Venta.fecha <= end_date).all()

    @staticmethod
    def ventas_totales(start_date, end_date):
        return db.session.query(db.func.sum(Venta.total)).filter(Venta.fecha >= start_date, Venta.fecha <= end_date).scalar() or 0

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

    def after_insert(self):
        producto = self.producto
        producto.cantidad_vendida += self.cantidad
        db.session.commit()



class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

    
    
    
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
    
    @staticmethod
    def movimientos_totales_producto(producto_id, start_date, end_date):
        entradas = db.session.query(db.func.sum(MovimientoInventario.cantidad)).filter(MovimientoInventario.producto_id == producto_id, MovimientoInventario.tipo == TipoMovimiento.ENTRADA, MovimientoInventario.fecha >= start_date, MovimientoInventario.fecha <= end_date).scalar() or 0
        salidas = db.session.query(db.func.sum(MovimientoInventario.cantidad)).filter(MovimientoInventario.producto_id == producto_id, MovimientoInventario.tipo == TipoMovimiento.SALIDA, MovimientoInventario.fecha >= start_date, MovimientoInventario.fecha <= end_date).scalar() or 0
        return entradas - salidas
