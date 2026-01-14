from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "inva-usuarios"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100))
    email = db.Column(db.String(100))
    rol = db.Column(db.Enum("admin", "vendedor", "contador"), default="vendedor")
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime)
    ultimo_acceso = db.Column(db.DateTime)


class Cliente(db.Model):
    __tablename__ = "inva-clientes"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ruc_dni = db.Column(db.String(20), unique=True)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime)


class Producto(db.Model):
    __tablename__ = "inva-productos"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    isv_aplica = db.Column(db.Boolean, default=False)
    foto = db.Column(db.String(255))


class Categoria(db.Model):
    __tablename__ = "inva-categorias"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime)


class AjustesNegocio(db.Model):
    __tablename__ = "inva-ajustes_negocio"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    rtn = db.Column(db.String(30))
    telefono = db.Column(db.String(30))
    email = db.Column(db.String(120))
    direccion = db.Column(db.String(255))
    cai = db.Column(db.String(60))
    rango_autorizado = db.Column(db.String(120))
    fecha_limite_emision = db.Column(db.String(30))
    mensaje = db.Column(db.String(255))


class FacturaContado(db.Model):
    __tablename__ = "inva-facturas_contado"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("inva-clientes.id"))
    usuario_id = db.Column(db.Integer, db.ForeignKey("inva-usuarios.id"))
    rtn = db.Column(db.String(20))
    fecha = db.Column(db.DateTime)
    subtotal = db.Column(db.Numeric(10, 2))
    isv = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    pago = db.Column(db.Numeric(10, 2))
    cambio = db.Column(db.Numeric(10, 2))
    estado = db.Column(
        db.Enum("contado", "credito", "pagada", "anulada"), default="contado"
    )
    pdf_filename = db.Column(db.String(255))


class DetalleFacturaContado(db.Model):
    __tablename__ = "inva-detalle_facturas_contado"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(
        db.Integer, db.ForeignKey("inva-facturas_contado.id"), nullable=False
    )
    producto_id = db.Column(
        db.Integer, db.ForeignKey("inva-productos.id"), nullable=False
    )
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    isv_aplica = db.Column(db.Boolean, default=False)


class FacturaCredito(db.Model):
    __tablename__ = "inva-facturas_credito"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("inva-clientes.id"))
    usuario_id = db.Column(db.Integer, db.ForeignKey("inva-usuarios.id"))
    rtn = db.Column(db.String(20))
    fecha = db.Column(db.DateTime)
    subtotal = db.Column(db.Numeric(10, 2))
    isv = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    pago_inicial = db.Column(db.Numeric(10, 2))
    saldo = db.Column(db.Numeric(10, 2))
    estado = db.Column(
        db.Enum("pendiente", "pagada", "anulada"), default="pendiente"
    )
    pdf_filename = db.Column(db.String(255))


class DetalleFacturaCredito(db.Model):
    __tablename__ = "inva-detalle_facturas_credito"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(
        db.Integer, db.ForeignKey("inva-facturas_credito.id"), nullable=False
    )
    producto_id = db.Column(
        db.Integer, db.ForeignKey("inva-productos.id"), nullable=False
    )
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    isv_aplica = db.Column(db.Boolean, default=False)
