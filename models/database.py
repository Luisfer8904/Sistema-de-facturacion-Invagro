from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario por ID para Flask-Login"""
    return Usuario.query.get(int(user_id))


class Usuario(UserMixin, db.Model):
    """Modelo de usuarios del sistema"""
    __tablename__ = 'inva-usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100))
    email = db.Column(db.String(100))
    rol = db.Column(db.Enum('admin', 'vendedor', 'contador', name='rol_enum'), default='vendedor')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    # Relaciones
    facturas = db.relationship('Factura', backref='usuario', lazy=True)
    
    def set_password(self, password):
        """Hashear y guardar contraseña"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password, password)
    
    def actualizar_ultimo_acceso(self):
        """Actualizar timestamp de último acceso"""
        self.ultimo_acceso = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<Usuario {self.username}>'


class Cliente(db.Model):
    """Modelo de clientes"""
    __tablename__ = 'inva-clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ruc_dni = db.Column(db.String(20), unique=True, index=True)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    facturas = db.relationship('Factura', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'


class Producto(db.Model):
    """Modelo de productos"""
    __tablename__ = 'inva-productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.Enum('veterinario', 'shampoo', name='categoria_enum'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    detalles_factura = db.relationship('DetalleFactura', backref='producto', lazy=True)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'


class Factura(db.Model):
    """Modelo de facturas"""
    __tablename__ = 'inva-facturas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(50), unique=True, nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('inva-clientes.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('inva-usuarios.id'))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Numeric(10, 2))
    igv = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.Enum('pendiente', 'pagada', 'anulada', name='estado_enum'), default='pendiente')
    
    # Relaciones
    detalles = db.relationship('DetalleFactura', backref='factura', lazy=True, cascade='all, delete-orphan')
    
    def calcular_totales(self):
        """Calcular subtotal, IGV y total de la factura"""
        self.subtotal = sum(detalle.subtotal for detalle in self.detalles)
        self.igv = self.subtotal * 0.18  # IGV 18%
        self.total = self.subtotal + self.igv
    
    def __repr__(self):
        return f'<Factura {self.numero_factura}>'


class DetalleFactura(db.Model):
    """Modelo de detalles de factura"""
    __tablename__ = 'inva-detalle_facturas'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('inva-facturas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('inva-productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    def calcular_subtotal(self):
        """Calcular subtotal del detalle"""
        self.subtotal = self.cantidad * self.precio_unitario
    
    def __repr__(self):
        return f'<DetalleFactura {self.id}>'
