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
    categoria = db.Column(db.Enum("veterinario", "shampoo"), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
