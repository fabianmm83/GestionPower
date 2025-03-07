from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import DateTime
from app import db
from app.models import Producto, Venta, VentaProducto

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    productos = Producto.query.filter_by(activo=True).all()  # Solo productos activos
    return render_template('index.html', productos=productos)

##agregar producto nuevo

@routes.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    # Obtener las categorías únicas existentes en la base de datos
    categorias = db.session.query(Producto.categoria).distinct().all()
    categorias = [categoria[0] for categoria in categorias]  # Convertir a lista de strings
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        categoria = request.form['categoria']

        # Crear el nuevo producto
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            cantidad=cantidad,
            categoria=categoria
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        return redirect(url_for('routes.index'))  # Redirigir al listado de productos

    return render_template('nuevo_producto.html', categorias=categorias)  # Pasar las categorías a la plantilla


@routes.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = float(request.form['precio'])
        producto.cantidad = int(request.form['cantidad'])
        producto.categoria = request.form['categoria']

        db.session.commit()
        return redirect(url_for('routes.index'))

    return render_template('editar_producto.html', producto=producto)


## producto eliminado ruta 
@routes.route('/producto/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)

    # Verifica si existen ventas asociadas al producto
    ventas = Venta.query.filter_by(producto_id=id).all()
    if ventas:
        flash("No se puede eliminar el producto porque tiene ventas asociadas.", "danger")
        return redirect(url_for('routes.index'))

    # Marca el producto como inactivo
    producto.activo = False
    db.session.commit()
    flash("Producto marcado como inactivo.", "success")
    return redirect(url_for('routes.index'))




@routes.route('/venta/nueva', methods=['GET', 'POST'])
def nueva_venta():
    if request.method == 'POST':
        productos_seleccionados = request.form.getlist('productos')  # Listado de IDs de productos seleccionados
        cantidades = request.form.getlist('cantidad')  # Cantidades correspondientes a cada producto
        total_venta = 0

        # Crear una nueva venta
        venta = Venta(total=total_venta)
        db.session.add(venta)

        for producto_id, cantidad in zip(productos_seleccionados, cantidades):
            producto = Producto.query.get(producto_id)
            if producto and producto.cantidad >= int(cantidad):  # Asegúrate de que haya stock
                venta_producto = VentaProducto(
                    venta_id=venta.id,
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio=producto.precio
                )
                db.session.add(venta_producto)

                # Descontar la cantidad del inventario
                producto.cantidad -= int(cantidad)
                total_venta += producto.precio * int(cantidad)

        # Actualizar el total de la venta
        venta.total = total_venta
        db.session.commit()

        return redirect(url_for('routes.index'))

    productos = Producto.query.filter_by(activo=True).all()  # Obtener los productos disponibles
    return render_template('nueva_venta.html', productos=productos)



@routes.route('/registro_venta', methods=['POST'])
def registrar_venta():
    data = request.json

    # Crear una nueva venta
    nueva_venta = Venta(total=0.0)

    # Agregar productos a la venta
    for item in data['productos']:
        producto_id = item['producto_id']
        cantidad = item['cantidad']

        # Obtener el producto de la base de datos
        producto = db.session.get(Producto, producto_id)
        if not producto:
            return jsonify({"error": f"Producto con ID {producto_id} no encontrado"}), 404

        # Agregar el producto a la venta
        nueva_venta.agregar_producto(producto, cantidad)

    # Guardar la venta en la base de datos
    db.session.add(nueva_venta)
    db.session.commit()

    return jsonify({"mensaje": "Venta registrada correctamente", "venta_id": nueva_venta.id}), 201





@routes.route('/ventas', methods=['GET'])
def listar_ventas():
    ventas = Venta.query.all()  # Obtener todas las ventas
    return render_template('ventas.html', ventas=ventas)



##RUTA PARA ELIMINAR VENTAS REGISTRADAS
@routes.route('/venta/eliminar/<int:id>', methods=['POST'])
def eliminar_venta(id):
    venta = Venta.query.get_or_404(id)  # Buscar la venta

    # Recuperar el producto relacionado y devolver el stock
    producto = Producto.query.get(venta.producto_id)
    if producto:
        producto.cantidad += venta.cantidad  # Devolver la cantidad al stock

    db.session.delete(venta)  # Eliminar la venta
    db.session.commit()  # Guardar cambios
    flash("Venta eliminada correctamente.", "success")

    return redirect(url_for('routes.listar_ventas'))  # Redirigir a la lista de ventas
