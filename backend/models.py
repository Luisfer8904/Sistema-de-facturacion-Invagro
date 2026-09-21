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


class AvesUser(db.Model):
    __tablename__ = "inva_aves_usuarios"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime)


class GanaderiaUser(db.Model):
    __tablename__ = "inva_ganaderia_usuarios"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(120), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="usuario")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime)
    ultimo_acceso = db.Column(db.DateTime)


class GanaderiaVeterinario(db.Model):
    __tablename__ = "inva_ganaderia_veterinarios"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_usuarios.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    numero_colegiado = db.Column(db.String(60))
    telefono = db.Column(db.String(30))
    especialidad = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime)


class GanaderiaFinca(db.Model):
    __tablename__ = "inva_ganaderia_fincas"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(140), nullable=False)
    propietario = db.Column(db.String(140))
    telefono = db.Column(db.String(30))
    ubicacion = db.Column(db.String(180))
    direccion = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    creada_por_user_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_usuarios.id"),
        nullable=False,
        index=True,
    )
    activa = db.Column(db.Boolean, nullable=False, default=True)
    fecha_registro = db.Column(db.DateTime)


class GanaderiaVeterinarioFinca(db.Model):
    __tablename__ = "inva_ganaderia_veterinario_fincas"
    __table_args__ = (
        db.UniqueConstraint("veterinario_id", "finca_id", name="uq_gan_vet_finca"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    veterinario_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_veterinarios.id"),
        nullable=False,
        index=True,
    )
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_fincas.id"),
        nullable=False,
        index=True,
    )
    es_responsable = db.Column(db.Boolean, nullable=False, default=False)
    fecha_asignacion = db.Column(db.DateTime)


class GanaderiaFincaUsuario(db.Model):
    __tablename__ = "inva_ganaderia_finca_usuarios"
    __table_args__ = (
        db.UniqueConstraint("user_id", "finca_id", name="uq_gan_finca_usuario"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_usuarios.id"),
        nullable=False,
        index=True,
    )
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_fincas.id"),
        nullable=False,
        index=True,
    )
    fecha_asignacion = db.Column(db.DateTime)


class GanaderiaPotrero(db.Model):
    __tablename__ = "inva_ganaderia_potreros"
    __table_args__ = (
        db.UniqueConstraint("finca_id", "nombre", name="uq_gan_finca_potrero"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_fincas.id"),
        nullable=False,
        index=True,
    )
    nombre = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default="potrero")
    capacidad = db.Column(db.Integer)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_registro = db.Column(db.DateTime)


class GanaderiaAnimal(db.Model):
    __tablename__ = "inva_ganaderia_animales"
    __table_args__ = (
        db.UniqueConstraint("finca_id", "codigo", name="uq_gan_finca_animal_codigo"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_fincas.id"),
        nullable=False,
        index=True,
    )
    potrero_id = db.Column(db.Integer, db.ForeignKey("inva_ganaderia_potreros.id"), index=True)
    codigo = db.Column(db.String(60), nullable=False)
    nombre = db.Column(db.String(120))
    raza = db.Column(db.String(100))
    sexo = db.Column(db.String(15), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    peso_actual = db.Column(db.Numeric(10, 2))
    procedencia = db.Column(db.String(160))
    madre_codigo = db.Column(db.String(60))
    padre_codigo = db.Column(db.String(60))
    foto = db.Column(db.String(255))
    estado = db.Column(db.String(30), nullable=False, default="activo")
    observaciones = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime)


class GanaderiaActividad(db.Model):
    __tablename__ = "inva_ganaderia_actividades"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_fincas.id"),
        nullable=False,
        index=True,
    )
    animal_id = db.Column(db.Integer, db.ForeignKey("inva_ganaderia_animales.id"), index=True)
    tipo = db.Column(db.String(40), nullable=False, index=True)
    titulo = db.Column(db.String(160), nullable=False)
    fecha = db.Column(db.Date, nullable=False, index=True)
    proxima_fecha = db.Column(db.Date, index=True)
    producto = db.Column(db.String(140))
    dosis = db.Column(db.String(80))
    peso = db.Column(db.Numeric(10, 2))
    resultado = db.Column(db.String(160))
    observaciones = db.Column(db.Text)
    realizada_por_user_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_usuarios.id"),
        nullable=False,
        index=True,
    )
    fecha_registro = db.Column(db.DateTime)


class GanaderiaPalpacionLote(db.Model):
    __tablename__ = "inva_ganaderia_palpaciones_lote"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_fincas.id"),
        nullable=False,
        index=True,
    )
    potrero_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_potreros.id"),
        nullable=False,
        index=True,
    )
    fecha = db.Column(db.Date, nullable=False, index=True)
    titulo = db.Column(db.String(160), nullable=False)
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default="abierta", index=True)
    creada_por_user_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_usuarios.id"),
        nullable=False,
        index=True,
    )
    fecha_registro = db.Column(db.DateTime, nullable=False)
    fecha_finalizacion = db.Column(db.DateTime)


class GanaderiaPalpacionDetalle(db.Model):
    __tablename__ = "inva_ganaderia_palpacion_detalles"
    __table_args__ = (
        db.UniqueConstraint(
            "palpacion_lote_id",
            "animal_id",
            name="uq_gan_palpacion_lote_animal",
        ),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    palpacion_lote_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_palpaciones_lote.id"),
        nullable=False,
        index=True,
    )
    animal_id = db.Column(
        db.Integer,
        db.ForeignKey("inva_ganaderia_animales.id"),
        nullable=False,
        index=True,
    )
    resultado = db.Column(db.String(20))
    dias_gestacion = db.Column(db.Integer)
    fecha_probable_parto = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False)


class AvesGranjaCliente(db.Model):
    __tablename__ = "inva_aves_granja_clientes"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    contacto = db.Column(db.String(120))
    telefono = db.Column(db.String(30))
    email = db.Column(db.String(120))
    direccion = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime)


class AvesLote(db.Model):
    __tablename__ = "inva_aves_lotes"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    encargado = db.Column(db.String(120))
    telefono = db.Column(db.String(30))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    plan_nombre = db.Column(db.String(120))
    cantidad_aves = db.Column(db.Integer, default=0)
    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime)


class AvesLoteActividad(db.Model):
    __tablename__ = "inva_aves_lote_actividades"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, nullable=False, index=True)
    plan_id = db.Column(db.Integer)
    actividad_nombre = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    edad_dias = db.Column(db.Integer, nullable=False)
    fecha_programada = db.Column(db.Date, nullable=False)
    fecha_realizacion = db.Column(db.Date, nullable=False)
    comentarios = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime)


class AvesLotePlanPersonalizado(db.Model):
    __tablename__ = "inva_aves_lote_plan_personalizado"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    edad_dias = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime)


class AvesLoteCierre(db.Model):
    __tablename__ = "inva_aves_lote_cierres"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    fecha_cierre = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(120), nullable=False)
    comentarios = db.Column(db.Text)
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
    rango_autorizado_inicio = db.Column(db.String(120))
    rango_autorizado_fin = db.Column(db.String(120))
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


class AbonoFactura(db.Model):
    __tablename__ = "inva-abonos_facturas"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(
        db.Integer, db.ForeignKey("inva-facturas_contado.id"), nullable=False
    )
    usuario_id = db.Column(db.Integer, db.ForeignKey("inva-usuarios.id"))
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime)


class CobroPersonal(db.Model):
    __tablename__ = "inva-cobros_personales"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    numero_cobro = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("inva-clientes.id"))
    nombre = db.Column(db.String(120), nullable=False)
    concepto = db.Column(db.String(160), nullable=False)
    telefono = db.Column(db.String(30))
    fecha = db.Column(db.DateTime)
    fecha_vencimiento = db.Column(db.Date)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    saldo = db.Column(db.Numeric(10, 2), nullable=False)
    observaciones = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey("inva-usuarios.id"))
    estado = db.Column(
        db.Enum("pendiente", "pagado", "anulado"), default="pendiente"
    )


class CobroPersonalDetalle(db.Model):
    __tablename__ = "inva-cobros_personales_detalle"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    cobro_id = db.Column(
        db.Integer, db.ForeignKey("inva-cobros_personales.id"), nullable=False
    )
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)


class AbonoCobroPersonal(db.Model):
    __tablename__ = "inva-abonos_cobros_personales"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    cobro_id = db.Column(
        db.Integer, db.ForeignKey("inva-cobros_personales.id"), nullable=False
    )
    usuario_id = db.Column(db.Integer, db.ForeignKey("inva-usuarios.id"))
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    comentario = db.Column(db.String(255))
    fecha = db.Column(db.DateTime)


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


class Pedido(db.Model):
    __tablename__ = "inva-pedidos"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    numero_pedido = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("inva-clientes.id"))
    usuario_id = db.Column(db.Integer, db.ForeignKey("inva-usuarios.id"))
    rtn = db.Column(db.String(20))
    fecha = db.Column(db.DateTime)
    subtotal = db.Column(db.Numeric(10, 2))
    isv = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    estado = db.Column(
        db.Enum("pendiente", "listo", "facturado", "anulado"), default="pendiente"
    )


class DetallePedido(db.Model):
    __tablename__ = "inva-detalle_pedidos"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(
        db.Integer, db.ForeignKey("inva-pedidos.id"), nullable=False
    )
    producto_id = db.Column(
        db.Integer, db.ForeignKey("inva-productos.id"), nullable=False
    )
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    isv_aplica = db.Column(db.Boolean, default=False)


class ChatSession(db.Model):
    __tablename__ = "inva-chat_sessions"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


class ChatMessage(db.Model):
    __tablename__ = "inva-chat_messages"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("inva-chat_sessions.id"))
    role = db.Column(db.String(20))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime)


class ChatSummary(db.Model):
    __tablename__ = "inva-chat_summaries"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("inva-chat_sessions.id"))
    summary = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)


class ChatAudit(db.Model):
    __tablename__ = "inva-chat_audit"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36))
    username = db.Column(db.String(50))
    question = db.Column(db.Text)
    tool_name = db.Column(db.String(64))
    params_json = db.Column(db.Text)
    elapsed_ms = db.Column(db.Integer)
    rows_returned = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)


class AvesPlan(db.Model):
    __tablename__ = "inva_aves_planes"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    plan_nombre = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    edad_dias = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime)
