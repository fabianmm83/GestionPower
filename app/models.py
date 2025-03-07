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
class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)

    # Relación con productos a través de la tabla intermedia
    productos = db.relationship('VentaProducto', back_populates='venta')

    def calcular_total(self):
        total = sum([vp.cantidad * vp.precio for vp in self.productos])
        return total

    # Método para agregar un producto a la venta
    def agregar_producto(self, producto, cantidad):
        venta_producto = VentaProducto(cantidad=cantidad, precio=producto.precio, producto=producto)
        self.productos.append(venta_producto)
        self.total = self.calcular_total()

# Tabla intermedia para la relación entre Venta y Producto
class VentaProducto(db.Model):
    __tablename__ = 'venta_producto'
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id', name='fk_venta_producto_venta'), primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id', name='fk_venta_producto_producto'), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    # Relaciones inversas
    venta = db.relationship('Venta', back_populates='productos')
    producto = db.relationship('Producto', back_populates='ventas')