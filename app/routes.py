from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import DateTime, func, case, text
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
def root():
    """Redirige a dashboard desde la raíz"""
    return redirect(url_for('routes.dashboard'))


@routes.route('/index')
def index():
    try:
        # Get filter parameters
        categoria_seleccionada = request.args.get('categoria', 'todas')
        page = request.args.get('page', 1, type=int)
        
        # Base query
        query = Producto.query.filter_by(activo=True)
        
        # Apply category filter
        if categoria_seleccionada != 'todas':
            query = query.filter_by(categoria=categoria_seleccionada)
        
        # Pagination
        productos = query.order_by(Producto.nombre).paginate(page=page, per_page=10)
        
        # Get all categories for dropdown
        categorias = db.session.query(Producto.categoria).distinct().all()
        categorias = [c[0] for c in categorias if c[0]]  # Extract category names
        
        return render_template(
            'index.html',
            productos=productos,
            categorias=categorias,
            categoria_seleccionada=categoria_seleccionada
        )
        
    except Exception as e:
        logging.error(f"Error en index: {str(e)}", exc_info=True)
        flash("Error al cargar el inventario", "danger")
        return redirect(url_for('routes.dashboard'))

@routes.route('/dashboard')
def dashboard():
    try:
        hoy = datetime.now().date()
        
        # Estadísticas básicas
        total_ventas_hoy = db.session.query(func.count(Venta.id)).filter(
            func.date(Venta.fecha) == hoy
        ).scalar() or 0
        
        monto_ventas_hoy = db.session.query(
            func.coalesce(func.sum(Venta.total), 0)
        ).filter(
            func.date(Venta.fecha) == hoy
        ).scalar() or 0
        
        # Productos más vendidos (últimos 30 días)
        fecha_limite = datetime.now() - timedelta(days=30)
        productos_mas_vendidos = db.session.query(
            Producto,
            func.coalesce(func.sum(VentaProducto.cantidad), 0).label('total_vendido')
        ).join(
            VentaProducto, Producto.id == VentaProducto.producto_id
        ).join(
            Venta, VentaProducto.venta_id == Venta.id
        ).filter(
            Venta.fecha >= fecha_limite
        ).group_by(
            Producto.id
        ).order_by(
            func.sum(VentaProducto.cantidad).desc()
        ).limit(5).all()
        
        # Últimas 5 ventas
        ultimas_ventas = Venta.query.order_by(
            Venta.fecha.desc()
        ).limit(5).all()
        
        # Estadísticas de inventario
        total_productos = Producto.query.count()
        productos_bajo_stock = Producto.query.filter(
            Producto.cantidad < 10
        ).count()
        
        return render_template('tienda/dashboard_tienda.html',
                            total_ventas_hoy=total_ventas_hoy,
                            monto_ventas_hoy=monto_ventas_hoy,
                            productos_mas_vendidos=productos_mas_vendidos,
                            ultimas_ventas=ultimas_ventas,
                            total_productos=total_productos,
                            productos_bajo_stock=productos_bajo_stock)
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error en dashboard: {str(e)}", exc_info=True)
        flash("Ocurrió un error al cargar el dashboard. Por favor intente nuevamente.", "danger")
        return redirect(url_for('routes.index'))


@routes.route('/tienda')
def index_tienda():
    return render_template('tienda/index_tienda.html')




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
        precio_venta = float(request.form['precio_venta'])
        costo_adquisicion = float(request.form['costo_adquisicion'])
        cantidad = int(request.form['cantidad'])
        categoria_id = request.form['categoria']

        categoria = Categoria.query.get(categoria_id)

        if not categoria:
            flash("Categoría no válida.", "danger")
            return redirect(url_for('routes.nuevo_producto'))

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio_venta=precio_venta,
            costo_adquisicion=costo_adquisicion,
            cantidad=cantidad,
            categoria=categoria
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        movimiento = MovimientoInventario(
            producto_id=nuevo_producto.id,
            tipo='entrada',
            cantidad=cantidad
        )
        db.session.add(movimiento)
        db.session.commit()

        flash('Producto agregado correctamente.', 'success')
        return redirect(url_for('routes.index'))

    categorias = Categoria.query.all()
    return render_template('nuevo_producto.html', categorias=categorias)


@routes.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio_venta = float(request.form['precio_venta'])
        producto.costo_adquisicion = float(request.form['costo_adquisicion'])
        producto.cantidad = int(request.form['cantidad'])
        categoria_id = request.form['categoria']

        categoria = Categoria.query.get(categoria_id)

        if not categoria:
            flash("Categoría no válida.", "danger")
            return redirect(url_for('routes.editar_producto', id=id))

        producto.categoria = categoria
        db.session.commit()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for('routes.index'))

    categorias = Categoria.query.all()
    return render_template('editar_producto.html', producto=producto, categorias=categorias)


@routes.route('/analisis_productos')
def analisis_productos():
    try:
        filtro = request.args.get('filtro', 'vendidos')

        # Subquery for sales aggregation
        ventas_subq = db.session.query(
            VentaProducto.producto_id,
            db.func.sum(VentaProducto.cantidad).label('total_vendido'),
            db.func.sum(VentaProducto.cantidad * VentaProducto.precio_venta).label('ventas_totales')
        ).group_by(VentaProducto.producto_id).subquery()

        # Main query
        query = db.session.query(
            Producto,
            db.func.coalesce(ventas_subq.c.total_vendido, 0).label('total_vendido'),
            db.func.coalesce(ventas_subq.c.ventas_totales, 0).label('ventas_totales'),
            db.func.coalesce(Producto.cantidad, 0) - db.func.coalesce(ventas_subq.c.total_vendido, 0)
                .label('stock_restante')
        ).outerjoin(
            ventas_subq, ventas_subq.c.producto_id == Producto.id
        ).join(
            Categoria, Categoria.id == Producto.categoria_id
        )

        # Apply filter - changed from HAVING to WHERE for subquery
        if filtro == 'vendidos':
            query = query.filter(ventas_subq.c.total_vendido > 0)

        productos_venta = query.all()

        # Handle no results
        if not productos_venta and filtro == 'vendidos':
            flash("No hay productos vendidos.", "info")
            return render_template('analisis.html', datos=[], grafico_productos=None, filtro=filtro)

        # Generate chart
        if productos_venta:
            productos = [p.Producto.nombre for p in productos_venta]
            cantidades = [p.total_vendido for p in productos_venta]
            
            plt.switch_backend('Agg')
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(productos, cantidades, color='green')
            ax.set_xlabel('Cantidad Vendida')
            ax.set_ylabel('Producto')
            ax.set_title('Productos Más Vendidos')
            plt.tight_layout()
            
            img = io.BytesIO()
            fig.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            grafico_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
            plt.close(fig)
        else:
            grafico_base64 = None

        return render_template(
            'analisis.html',
            datos=productos_venta,
            grafico_productos=grafico_base64,
            filtro=filtro
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error en analisis_productos: {str(e)}", exc_info=True)
        flash("Error al generar el análisis", "danger")
        return redirect(url_for('routes.index'))







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
    ventas = Venta.query.options(joinedload(Venta.productos).joinedload(VentaProducto.producto)).all()

    mayor_venta = max([venta.total for venta in ventas], default=0)
    pago_promedio = sum([venta.total for venta in ventas]) / len(ventas) if ventas else 0

    ventas_por_mes = defaultdict(lambda: {"total_ventas": 0, "total_recaudado": 0})
    for venta in ventas:
        mes = venta.fecha.strftime("%B %Y")
        ventas_por_mes[mes]["total_ventas"] += 1
        ventas_por_mes[mes]["total_recaudado"] += venta.total

    grafico_ventas = generar_grafico_ventas(ventas_por_mes)

    return render_template(
        "ventas_lista.html", 
        ventas=ventas,
        mayor_venta=mayor_venta,
        pago_promedio=pago_promedio,
        ventas_por_mes=ventas_por_mes,
        grafico_ventas=grafico_ventas
    )



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







@routes.route('/movimientos')
def listar_movimientos():
    movimientos = MovimientoInventario.query.order_by(MovimientoInventario.fecha.desc()).all()
    return render_template('movimientos_lista.html', movimientos=movimientos)

    
    
    
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
