from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.database import Usuario, Cliente, Producto, Factura

# Crear blueprint del dashboard
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Página principal del dashboard"""
    # Obtener estadísticas básicas
    total_clientes = Cliente.query.count()
    total_productos = Producto.query.filter_by(activo=True).count()
    total_facturas = Factura.query.count()
    facturas_pendientes = Factura.query.filter_by(estado='pendiente').count()
    
    # Obtener últimas facturas
    ultimas_facturas = Factura.query.order_by(Factura.fecha.desc()).limit(5).all()
    
    stats = {
        'total_clientes': total_clientes,
        'total_productos': total_productos,
        'total_facturas': total_facturas,
        'facturas_pendientes': facturas_pendientes
    }
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         ultimas_facturas=ultimas_facturas,
                         usuario=current_user)


@dashboard_bp.route('/clientes')
@login_required
def clientes():
    """Página de gestión de clientes"""
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)


@dashboard_bp.route('/productos')
@login_required
def productos():
    """Página de gestión de productos"""
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('productos.html', productos=productos)


@dashboard_bp.route('/facturas')
@login_required
def facturas():
    """Página de gestión de facturas"""
    facturas = Factura.query.order_by(Factura.fecha.desc()).all()
    return render_template('facturas.html', facturas=facturas)


@dashboard_bp.route('/reportes')
@login_required
def reportes():
    """Página de reportes"""
    return render_template('reportes.html')
