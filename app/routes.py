from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import DateTime, func, case
from app import db
from app.models import Producto, Categoria, Venta, VentaProducto, MovimientoInventario
from collections import defaultdict
from config.config import Config  # type: ignore
import io
import base64
import logging
from sqlalchemy.orm import joinedload


# Configuración de logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

# Cambiar el backend de Matplotlib a 'Agg' para evitar problemas con Tkinter
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Usa Config.CATEGORIAS_PREDETERMINADAS donde sea necesario
CATEGORIAS_PREDETERMINADAS = Config.CATEGORIAS_PREDETERMINADAS

routes = Blueprint('routes', __name__)

def generar_grafico_ventas(ventas_por_mes):
    # Extraer los meses y los totales de ventas
    meses = list(ventas_por_mes.keys())
    total_ventas = [ventas_por_mes[mes]["total_recaudado"] for mes in meses]

    # Crear el gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(meses, total_ventas, color='blue')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Total Recaudado')
    ax.set_title('Ventas por Mes')

    # Convertir el gráfico a imagen en base64
    img = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(img)
    img.seek(0)
    grafico_base64 = base64.b64encode(img.getvalue()).decode('utf8')

    return grafico_base64

def recalcular_stock():
    """Recalcula el stock de todos los productos basado en los movimientos de inventario."""
    productos = Producto.query.all()
    for producto in productos:
        movimientos_entrada = MovimientoInventario.query.filter_by(producto_id=producto.id, tipo='entrada').all()
        movimientos_salida = MovimientoInventario.query.filter_by(producto_id=producto.id, tipo='salida').all()

        stock_calculado = sum([m.cantidad for m in movimientos_entrada]) - sum([m.cantidad for m in movimientos_salida])
        producto.cantidad = stock_calculado
        db.session.commit()

@routes.route('/')
def index():
    page = request.args.get('page', 1, type=int)  # Página actual (por defecto es 1)
    productos = Producto.query.filter_by(activo=True).paginate(page=page, per_page=10)

    return render_template('index.html', productos=productos)


@routes.route('/productos')
def productos():
    page = request.args.get('page', 1, type=int)  # Página actual (por defecto es 1)
    productos_paginados = Producto.query.filter_by(activo=True).paginate(page=page, per_page=10)

    return render_template('productos_lista.html', productos=productos_paginados)

@routes.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        categoria_id = request.form['categoria']  # Aquí obtenemos el ID de la categoría seleccionada

        # Obtener la instancia de la categoría usando el ID
        categoria = Categoria.query.get(categoria_id)

        if not categoria:
            flash("Categoría no válida.", "danger")
            return redirect(url_for('routes.nuevo_producto'))

        # Crear el nuevo producto con la instancia de la categoría
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            cantidad=cantidad,
            categoria=categoria  # Asignar la instancia de Categoria
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        # Registrar movimiento de entrada
        movimiento = MovimientoInventario(
            producto_id=nuevo_producto.id,
            tipo='entrada',
            cantidad=cantidad
        )
        db.session.add(movimiento)
        db.session.commit()

        flash('Producto agregado correctamente.', 'success')
        return redirect(url_for('routes.index'))

    categorias = Categoria.query.all()  # Obtener todas las categorías desde la base de datos
    return render_template('nuevo_producto.html', categorias=categorias)


@routes.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = float(request.form['precio'])
        producto.cantidad = int(request.form['cantidad'])
        categoria_id = request.form['categoria']  # Aquí obtenemos el ID de la categoría seleccionada

        # Obtener la instancia de la categoría usando el ID
        categoria = Categoria.query.get(categoria_id)

        if not categoria:
            flash("Categoría no válida.", "danger")
            return redirect(url_for('routes.editar_producto', id=id))

        producto.categoria = categoria  # Asignar la instancia de Categoria al producto
        db.session.commit()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for('routes.index'))

    categorias = Categoria.query.all()  # Obtener todas las categorías desde la base de datos
    return render_template('editar_producto.html', producto=producto, categorias=categorias)










@routes.route('/venta/nueva', methods=['GET', 'POST'])
def nueva_venta():
    try:
        if request.method == 'POST':
            productos_seleccionados = request.form.getlist('productos')
        
            total_venta = 0
            productos_validos = []

            for producto_id in productos_seleccionados:
                producto = Producto.query.get(producto_id)

                if not producto:
                    flash(f"El producto con ID {producto_id} no existe.", "danger")
                    return redirect(url_for('routes.nueva_venta'))

                cantidad = int(request.form.get(f'cantidad_{producto_id}', 1))

                if cantidad > producto.cantidad:
                    flash(f"No hay suficiente stock para {producto.nombre}. Stock disponible: {producto.cantidad}", "danger")
                    return redirect(url_for('routes.nueva_venta'))

                productos_validos.append((producto, cantidad))

            if productos_validos:
                venta = Venta(total=0)
                db.session.add(venta)
                db.session.flush()

                for producto, cantidad in productos_validos:
                    venta_producto = VentaProducto(
                        venta_id=venta.id,
                        producto_id=producto.id,
                        cantidad=cantidad,
                        precio=producto.precio
                    )
                    db.session.add(venta_producto)
                    producto.cantidad -= cantidad
                    movimiento = MovimientoInventario(
                        producto_id=producto.id,
                        tipo='salida',
                        cantidad=cantidad
                    )
                    db.session.add(movimiento)
                    total_venta += producto.precio * cantidad

                venta.total = total_venta
                db.session.commit()

                flash("Venta registrada correctamente.", "success")
                return redirect(url_for('routes.index'))

            flash("No se seleccionaron productos válidos.", "warning")
            return redirect(url_for('routes.nueva_venta'))

        productos = Producto.query.filter_by(activo=True).all()
        return render_template('nueva_venta.html', productos=productos)

    except Exception as e:
        logging.error(f"Error en nueva_venta: {str(e)}")
        flash("Ocurrió un error al procesar la venta. Por favor, inténtalo de nuevo.", "danger")
        return redirect(url_for('routes.nueva_venta'))






@routes.route('/ventas', methods=['GET'])
def listar_ventas():
    ventas = Venta.query.all()

    mayor_venta = max([venta.total for venta in ventas], default=0)

    pago_promedio = sum([venta.total for venta in ventas]) / len(ventas) if ventas else 0

    ventas_por_mes = defaultdict(lambda: {"total_ventas": 0, "total_recaudado": 0})
    for venta in ventas:
        mes = venta.fecha.strftime("%B %Y")  # Formato: "Mes Año"
        ventas_por_mes[mes]["total_ventas"] += 1
        ventas_por_mes[mes]["total_recaudado"] += venta.total

    grafico_ventas = generar_grafico_ventas(ventas_por_mes)

    return render_template(
        "ventas_lista.html", 
        ventas=ventas,
        mayor_venta=mayor_venta,
        pago_promedio=pago_promedio,
        ventas_por_mes=ventas_por_mes,
        grafico_ventas=grafico_ventas  # Pasamos el gráfico al template
    )







@routes.route('/movimientos')
def listar_movimientos():
    movimientos = MovimientoInventario.query.order_by(MovimientoInventario.fecha.desc()).all()
    return render_template('movimientos_lista.html', movimientos=movimientos)







@routes.route('/venta/eliminar/<int:id>', methods=['POST'])
def eliminar_venta(id):
    try:
        venta = Venta.query.get_or_404(id)

        for venta_producto in venta.productos:
            producto = Producto.query.get(venta_producto.producto_id)
            if producto:
                producto.cantidad += venta_producto.cantidad  # Devolver la cantidad al stock

        for venta_producto in venta.productos:
            db.session.delete(venta_producto)

        db.session.delete(venta)
        db.session.commit()

        flash("Venta eliminada correctamente.", "success")
        return redirect(url_for('routes.listar_ventas'))

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al eliminar venta: {str(e)}")
        flash(f"Error al eliminar venta: {str(e)}", "danger")
        return redirect(url_for('routes.listar_ventas'))





@routes.route('/analisis_productos')
def analisis_productos():
    # Obtener el parámetro de filtro de la URL (por defecto 'vendidos')
    filtro = request.args.get('filtro', 'vendidos')  # Cambiado a 'vendidos' por defecto

    # Consulta base para obtener los productos vendidos y las cantidades
    query = db.session.query(
        Producto,
        db.func.coalesce(db.func.sum(VentaProducto.cantidad), 0).label('total_vendido'),
        db.func.coalesce(db.func.sum(VentaProducto.cantidad * Producto.precio), 0).label('ventas_totales'),
        db.case(
            (Producto.cantidad - db.func.coalesce(db.func.sum(VentaProducto.cantidad), 0) >= 0,
             Producto.cantidad - db.func.coalesce(db.func.sum(VentaProducto.cantidad), 0)),
            else_=0
        ).label('stock_restante')
    ).join(VentaProducto, VentaProducto.producto_id == Producto.id, isouter=True) \
     .join(Categoria, Categoria.id == Producto.categoria_id) \
     .group_by(Producto.id, Categoria.id)  # Agrupamos por Producto y Categoria

    # Aplicar el filtro según el parámetro
    if filtro == 'vendidos':
        query = query.having(db.func.coalesce(db.func.sum(VentaProducto.cantidad), 0) > 0)

    # Ejecutar la consulta
    productos_venta = query.all()

    # Si no hay productos vendidos y el filtro es 'vendidos', mostrar un mensaje
    if not productos_venta and filtro == 'vendidos':
        flash("No hay productos vendidos.", "warning")
        return render_template('analisis.html', datos=[], grafico_productos=None, filtro=filtro)

    # Generar gráfico de productos más vendidos
    productos = [producto[0].nombre for producto in productos_venta]  # Accede al producto (0) en la tupla
    cantidad_vendida = [producto.total_vendido for producto in productos_venta]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(productos, cantidad_vendida, color='green')
    ax.set_xlabel('Cantidad Vendida')
    ax.set_ylabel('Producto')
    ax.set_title('Productos Más Vendidos')

    # Convertir a imagen en base64
    img = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(img)
    img.seek(0)
    grafico_productos_base64 = base64.b64encode(img.getvalue()).decode('utf8')

    # Renderizar la plantilla con los datos y el filtro
    return render_template('analisis.html', 
                           datos=productos_venta, 
                           grafico_productos=grafico_productos_base64,
                           filtro=filtro)





    
    
    
    
    
@routes.route('/ver_base_de_datos')
def ver_base_de_datos():
    # Obtener todos los productos
    productos = Producto.query.all()
    
    # Obtener todas las ventas
    ventas = Venta.query.all()
    
    # Obtener todos los movimientos de inventario
    movimientos = MovimientoInventario.query.all()

    # Renderizar una plantilla con los datos
    return render_template('base_de_datos.html', 
                           productos=productos, 
                           ventas=ventas, 
                           movimientos=movimientos)
