from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import DateTime
from app import db
from app.models import Producto, Venta, VentaProducto
from config import CATEGORIAS_PREDETERMINADAS
from collections import defaultdict

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    productos = Producto.query.filter_by(activo=True).all()  # Solo productos activos
    return render_template('index.html', productos=productos)

##agregar producto nuevo
@routes.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        # Obtener los datos del formulario
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

        flash('Producto agregado correctamente.', 'success')  # Mensaje de éxito
        return redirect(url_for('routes.index'))  # Redirigir al listado de productos

    # Pasar las categorías predeterminadas a la plantilla
    return render_template('nuevo_producto.html', categorias=CATEGORIAS_PREDETERMINADAS)


@routes.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = float(request.form['precio'])
        producto.cantidad = int(request.form['cantidad'])
        categoria = request.form['categoria']

        # Validar que la categoría seleccionada esté en la lista de categorías predeterminadas
        if categoria not in CATEGORIAS_PREDETERMINADAS:
            flash("Categoría no válida.", "danger")
            return redirect(url_for('routes.editar_producto', id=id))

        producto.categoria = categoria
        db.session.commit()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for('routes.index'))

    # Pasar las categorías predeterminadas a la plantilla
    return render_template('editar_producto.html', producto=producto, categorias=CATEGORIAS_PREDETERMINADAS)

## producto eliminado ruta 
@routes.route('/producto/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    try:
        producto = Producto.query.get_or_404(id)

        # Verifica si existen registros en la tabla intermedia de ventas asociadas al producto
        ventas_asociadas = VentaProducto.query.filter_by(producto_id=id).first()
        if ventas_asociadas:
            flash("No se puede eliminar el producto porque tiene ventas asociadas.", "danger")
            print("NO SE PUEDE ELIMINAR PORQUE TIENE VENTAS ASOCIADAS") 
            return redirect(url_for('routes.index'))

        # Si no hay ventas asociadas, marca el producto como inactivo
        producto.activo = False
        print("SE ELIMINÓ SIN PROBLEMA") 
        db.session.commit()

        flash("Producto marcado como inactivo.", "success")
        return redirect(url_for('routes.index'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar producto: {str(e)}", "danger")
        return redirect(url_for('routes.index'))

@routes.route('/venta/nueva', methods=['GET', 'POST'])
def nueva_venta():
    if request.method == 'POST':
        try:
            productos_seleccionados = request.form.getlist('productos')  # IDs de productos seleccionados
            total_venta = 0
            total_productos = 0

            print("Productos seleccionados:", productos_seleccionados)  # Depuración

            # Crear una nueva venta
            venta = Venta(total=total_venta, cantidad=total_productos)
            db.session.add(venta)

            for producto_id in productos_seleccionados:
                producto = Producto.query.get(producto_id)
                if producto:
                    # Obtener la cantidad para este producto
                    cantidad = int(request.form.get(f'cantidad_{producto_id}', 1))  # Valor predeterminado: 1

                    print(f"Producto ID: {producto_id}, Cantidad: {cantidad}")  # Depuración

                    # Validar que la cantidad no supere el stock disponible
                    if cantidad > producto.cantidad:
                        flash(f"No hay suficiente stock para {producto.nombre}. Stock disponible: {producto.cantidad}", "danger")
                        db.session.rollback()  # Deshacer la transacción
                        return redirect(url_for('routes.nueva_venta'))

                    # Crear la relación VentaProducto
                    venta_producto = VentaProducto(
                        venta_id=venta.id,
                        producto_id=producto.id,
                        cantidad=cantidad,
                        precio=producto.precio
                    )
                    db.session.add(venta_producto)

                    # Descontar la cantidad del inventario
                    producto.cantidad -= cantidad

                    # Actualizar el total de la venta y el número de productos vendidos
                    total_venta += producto.precio * cantidad
                    total_productos += cantidad

            # Actualizar el total de la venta y el número de productos vendidos
            venta.total = total_venta
            venta.cantidad = total_productos
            db.session.commit()

            flash("Venta registrada correctamente.", "success")
            return redirect(url_for('routes.index'))

        except Exception as e:
            db.session.rollback()  # Deshacer la transacción en caso de error
            flash(f"Error al registrar la venta: {str(e)}", "danger")
            return redirect(url_for('routes.nueva_venta'))

    # Obtener los productos disponibles (activos)
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('nueva_venta.html', productos=productos)

@routes.route('/ventas', methods=['GET'])
def listar_ventas():
    # Obtener todas las ventas desde la base de datos
    ventas = Venta.query.all()

    # Calcular la mayor venta
    mayor_venta = max([venta.total for venta in ventas], default=0)

    # Calcular el pago promedio
    pago_promedio = sum([venta.total for venta in ventas]) / len(ventas) if ventas else 0

    # Agrupar ventas por mes
    ventas_por_mes = defaultdict(lambda: {"total_ventas": 0, "total_recaudado": 0})
    for venta in ventas:
        mes = venta.fecha.strftime("%B %Y")  # Formato: "Mes Año"
        ventas_por_mes[mes]["total_ventas"] += 1
        ventas_por_mes[mes]["total_recaudado"] += venta.total

    # Pasar los datos a la plantilla
    return render_template(
        "ventas.html",  # Nombre de tu plantilla HTML
        ventas=ventas,
        mayor_venta=mayor_venta,
        pago_promedio=pago_promedio,
        ventas_por_mes=ventas_por_mes
    )




##RUTA PARA ELIMINAR VENTAS REGISTRADAS
@routes.route('/venta/eliminar/<int:id>', methods=['POST'])
def eliminar_venta(id):
    try:
        print("Iniciando eliminación de venta...")  # Depuración
        venta = Venta.query.get_or_404(id)  # Buscar la venta
        print(f"Venta encontrada: {venta.id}")  # Depuración

        # Recorrer todos los productos asociados a la venta
        for venta_producto in venta.productos:
            producto = Producto.query.get(venta_producto.producto_id)
            if producto:
                print(f"Devolviendo stock del producto: {producto.nombre}")  # Depuración
                producto.cantidad += venta_producto.cantidad  # Devolver la cantidad al stock

        # Eliminar las entradas en la tabla intermedia VentaProducto
        print("Eliminando registros en VentaProducto...")  # Depuración
        for venta_producto in venta.productos:
            db.session.delete(venta_producto)

        # Finalmente, eliminar la venta
        print("Eliminando la venta...")  # Depuración
        db.session.delete(venta)
        db.session.commit()  # Guardar cambios
        print("Venta eliminada correctamente.")  # Depuración

        flash("Venta eliminada correctamente.", "success")
        return redirect(url_for('routes.listar_ventas'))  # Redirigir a la lista de ventas

    except Exception as e:
        print(f"Error: {str(e)}")  # Depuración
        db.session.rollback()
        flash(f"Error al eliminar venta: {str(e)}", "danger")
        return redirect(url_for('routes.listar_ventas'))