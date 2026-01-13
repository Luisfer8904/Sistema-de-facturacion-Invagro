import logging
import os
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import click
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from models import (
    Categoria,
    Cliente,
    DetalleFacturaContado,
    DetalleFacturaCredito,
    FacturaContado,
    FacturaCredito,
    Producto,
    User,
    db,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)

    upload_folder = os.path.join(app.static_folder, "uploads", "productos")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["PRODUCT_UPLOAD_FOLDER"] = upload_folder

    allowed_extensions = {"jpg", "jpeg", "png", "webp"}

    def save_product_image(file_storage):
        if not file_storage or not file_storage.filename:
            return None

        filename = secure_filename(file_storage.filename)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in allowed_extensions:
            raise ValueError("Formato de imagen no permitido.")

        unique_name = f"{uuid4().hex}.{ext}"
        file_path = os.path.join(app.config["PRODUCT_UPLOAD_FOLDER"], unique_name)
        file_storage.save(file_path)
        return unique_name

    def generate_invoice_number():
        return f"F001-{datetime.utcnow():%Y%m%d%H%M%S}"

    if not app.debug and not app.testing:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )

    @app.get("/")
    def landing():
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if not username or not password:
                return render_template(
                    "login.html",
                    error="Ingresa usuario y contrasena para continuar.",
                )

            try:
                user = User.query.filter_by(username=username, activo=True).first()
            except SQLAlchemyError:
                return render_template(
                    "login.html",
                    error="No se pudo validar el usuario. Intenta nuevamente.",
                )

            if not user or not check_password_hash(user.password, password):
                return render_template(
                    "login.html",
                    error="Usuario o contrasena incorrectos.",
                )

            session["user"] = user.username
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.get("/dashboard")
    def dashboard():
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template("dashboard.html", user=session["user"])

    @app.get("/logout")
    def logout():
        session.pop("user", None)
        return redirect(url_for("login"))

    @app.route("/clientes", methods=["GET", "POST"])
    def clientes():
        if not session.get("user"):
            return redirect(url_for("login"))

        error = None
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            ruc_dni = request.form.get("ruc_dni", "").strip() or None
            direccion = request.form.get("direccion", "").strip() or None
            telefono = request.form.get("telefono", "").strip() or None
            email = request.form.get("email", "").strip() or None

            if not nombre:
                error = "El nombre del cliente es obligatorio."
            else:
                try:
                    cliente = Cliente(
                        nombre=nombre,
                        ruc_dni=ruc_dni,
                        direccion=direccion,
                        telefono=telefono,
                        email=email,
                    )
                    db.session.add(cliente)
                    db.session.commit()
                    return redirect(url_for("clientes"))
                except SQLAlchemyError:
                    db.session.rollback()
                    error = "No se pudo guardar el cliente."

        clientes_list = Cliente.query.order_by(Cliente.id.desc()).all()
        return render_template(
            "clientes.html",
            user=session["user"],
            clientes=clientes_list,
            error=error,
        )

    @app.get("/facturacion")
    def facturacion():
        if not session.get("user"):
            return redirect(url_for("login"))

        clientes_list = Cliente.query.order_by(Cliente.nombre.asc()).all()
        categorias_list = Categoria.query.filter_by(activo=True).order_by(
            Categoria.nombre.asc()
        ).all()
        productos_list = Producto.query.filter_by(activo=True).order_by(Producto.nombre.asc()).all()
        return render_template(
            "facturacion.html",
            user=session["user"],
            clientes=clientes_list,
            categorias=categorias_list,
            productos=productos_list,
        )

    @app.route("/productos", methods=["GET", "POST"])
    def productos():
        if not session.get("user"):
            return redirect(url_for("login"))

        error = None
        if request.method == "POST":
            codigo = request.form.get("codigo", "").strip()
            nombre = request.form.get("nombre", "").strip()
            categoria = request.form.get("categoria", "").strip()
            precio = request.form.get("precio", "").strip()
            stock = request.form.get("stock", "").strip()
            descripcion = request.form.get("descripcion", "").strip() or None
            activo = request.form.get("activo") == "on"
            isv_aplica = request.form.get("isv_aplica") == "on"
            foto_file = request.files.get("foto")

            if not codigo or not nombre or not categoria or not precio:
                error = "Completa codigo, nombre, categoria y precio."
            else:
                try:
                    foto_filename = save_product_image(foto_file)
                    producto = Producto(
                        codigo=codigo,
                        nombre=nombre,
                        categoria=categoria,
                        precio=precio,
                        stock=stock or 0,
                        descripcion=descripcion,
                        activo=activo,
                        isv_aplica=isv_aplica,
                        foto=foto_filename,
                    )
                    db.session.add(producto)
                    db.session.commit()
                    return redirect(url_for("productos"))
                except ValueError as exc:
                    error = str(exc)
                except SQLAlchemyError:
                    db.session.rollback()
                    error = "No se pudo guardar el producto."

        productos_list = Producto.query.order_by(Producto.id.desc()).all()
        categorias_list = Categoria.query.filter_by(activo=True).order_by(
            Categoria.nombre.asc()
        ).all()
        return render_template(
            "productos.html",
            user=session["user"],
            productos=productos_list,
            categorias=categorias_list,
            error=error,
        )

    @app.get("/reportes")
    def reportes():
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template("reportes.html", user=session["user"])

    @app.route("/clientes/<int:cliente_id>/edit", methods=["GET", "POST"])
    def editar_cliente(cliente_id):
        if not session.get("user"):
            return redirect(url_for("login"))

        cliente = Cliente.query.get_or_404(cliente_id)
        error = None

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            ruc_dni = request.form.get("ruc_dni", "").strip() or None
            direccion = request.form.get("direccion", "").strip() or None
            telefono = request.form.get("telefono", "").strip() or None
            email = request.form.get("email", "").strip() or None

            if not nombre:
                error = "El nombre del cliente es obligatorio."
            else:
                try:
                    cliente.nombre = nombre
                    cliente.ruc_dni = ruc_dni
                    cliente.direccion = direccion
                    cliente.telefono = telefono
                    cliente.email = email
                    db.session.commit()
                    return redirect(url_for("clientes"))
                except SQLAlchemyError:
                    db.session.rollback()
                    error = "No se pudo actualizar el cliente."

        return render_template(
            "cliente_form.html",
            user=session["user"],
            cliente=cliente,
            error=error,
        )

    @app.post("/clientes/<int:cliente_id>/delete")
    def eliminar_cliente(cliente_id):
        if not session.get("user"):
            return redirect(url_for("login"))

        cliente = Cliente.query.get_or_404(cliente_id)
        try:
            db.session.delete(cliente)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        return redirect(url_for("clientes"))

    @app.route("/productos/<int:producto_id>/edit", methods=["GET", "POST"])
    def editar_producto(producto_id):
        if not session.get("user"):
            return redirect(url_for("login"))

        producto = Producto.query.get_or_404(producto_id)
        categorias_list = Categoria.query.filter_by(activo=True).order_by(
            Categoria.nombre.asc()
        ).all()
        error = None

        if request.method == "POST":
            codigo = request.form.get("codigo", "").strip()
            nombre = request.form.get("nombre", "").strip()
            categoria = request.form.get("categoria", "").strip()
            precio = request.form.get("precio", "").strip()
            stock = request.form.get("stock", "").strip()
            descripcion = request.form.get("descripcion", "").strip() or None
            activo = request.form.get("activo") == "on"
            isv_aplica = request.form.get("isv_aplica") == "on"
            foto_file = request.files.get("foto")

            if not codigo or not nombre or not categoria or not precio:
                error = "Completa codigo, nombre, categoria y precio."
            else:
                try:
                    producto.codigo = codigo
                    producto.nombre = nombre
                    producto.categoria = categoria
                    producto.precio = precio
                    producto.stock = stock or 0
                    producto.descripcion = descripcion
                    producto.activo = activo
                    producto.isv_aplica = isv_aplica
                    if foto_file and foto_file.filename:
                        foto_filename = save_product_image(foto_file)
                        if producto.foto:
                            old_path = os.path.join(
                                app.config["PRODUCT_UPLOAD_FOLDER"], producto.foto
                            )
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        producto.foto = foto_filename
                    db.session.commit()
                    return redirect(url_for("productos"))
                except ValueError as exc:
                    error = str(exc)
                except SQLAlchemyError:
                    db.session.rollback()
                    error = "No se pudo actualizar el producto."

        return render_template(
            "producto_form.html",
            user=session["user"],
            producto=producto,
            categorias=categorias_list,
            error=error,
        )

    @app.post("/productos/<int:producto_id>/delete")
    def eliminar_producto(producto_id):
        if not session.get("user"):
            return redirect(url_for("login"))

        producto = Producto.query.get_or_404(producto_id)
        try:
            db.session.delete(producto)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        return redirect(url_for("productos"))

    @app.post("/categorias")
    def crear_categoria():
        if not session.get("user"):
            return redirect(url_for("login"))

        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            return redirect(url_for("productos"))

        try:
            categoria = Categoria(nombre=nombre, activo=True)
            db.session.add(categoria)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        return redirect(url_for("productos"))

    @app.post("/categorias/<int:categoria_id>/delete")
    def eliminar_categoria(categoria_id):
        if not session.get("user"):
            return redirect(url_for("login"))

        categoria = Categoria.query.get_or_404(categoria_id)
        try:
            categoria.activo = False
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        return redirect(url_for("productos"))

    @app.post("/facturas")
    def crear_factura():
        if not session.get("user"):
            return jsonify({"error": "No autorizado."}), 401

        data = request.get_json(silent=True) or {}
        tipo = (data.get("tipo") or "").strip().lower()
        cliente_id = data.get("cliente_id") or None
        rtn = (data.get("rtn") or "").strip() or None
        pago_raw = data.get("pago", 0)
        items = data.get("items") or []

        if tipo not in {"contado", "credito"}:
            return jsonify({"error": "Tipo de factura invalido."}), 400
        if not items:
            return jsonify({"error": "No hay productos en la factura."}), 400

        try:
            pago = Decimal(str(pago_raw))
        except Exception:
            return jsonify({"error": "Pago invalido."}), 400

        producto_ids = []
        parsed_items = []
        for item in items:
            try:
                producto_id = int(item.get("producto_id"))
                cantidad = int(item.get("cantidad"))
            except (TypeError, ValueError):
                return jsonify({"error": "Producto o cantidad invalida."}), 400
            if cantidad <= 0:
                return jsonify({"error": "Cantidad invalida."}), 400
            producto_ids.append(producto_id)
            parsed_items.append((producto_id, cantidad))

        productos = Producto.query.filter(Producto.id.in_(producto_ids)).all()
        productos_map = {producto.id: producto for producto in productos}
        if len(productos_map) != len(set(producto_ids)):
            return jsonify({"error": "Producto no encontrado."}), 400

        subtotal = Decimal("0")
        isv = Decimal("0")
        detalles = []
        for producto_id, cantidad in parsed_items:
            producto = productos_map[producto_id]
            precio = Decimal(str(producto.precio))
            linea = precio * Decimal(cantidad)
            subtotal += linea
            if producto.isv_aplica:
                isv += linea * Decimal("0.15")
            detalles.append((producto, cantidad, precio, linea))

        total = subtotal + isv
        if pago < 0:
            return jsonify({"error": "Pago invalido."}), 400
        if tipo == "contado" and pago < total:
            return jsonify({"error": "Pago insuficiente para contado."}), 400

        usuario = User.query.filter_by(username=session["user"]).first()
        usuario_id = usuario.id if usuario else None
        numero_factura = generate_invoice_number()

        try:
            if tipo == "contado":
                cambio = pago - total
                factura = FacturaContado(
                    numero_factura=numero_factura,
                    cliente_id=cliente_id,
                    usuario_id=usuario_id,
                    rtn=rtn,
                    fecha=datetime.utcnow(),
                    subtotal=subtotal,
                    isv=isv,
                    total=total,
                    pago=pago,
                    cambio=cambio,
                    estado="pagada",
                )
                db.session.add(factura)
                db.session.flush()
                for producto, cantidad, precio, linea in detalles:
                    db.session.add(
                        DetalleFacturaContado(
                            factura_id=factura.id,
                            producto_id=producto.id,
                            cantidad=cantidad,
                            precio_unitario=precio,
                            subtotal=linea,
                            isv_aplica=producto.isv_aplica,
                        )
                    )
            else:
                saldo = total - pago
                if saldo < 0:
                    saldo = Decimal("0")
                estado = "pagada" if saldo == 0 else "pendiente"
                factura = FacturaCredito(
                    numero_factura=numero_factura,
                    cliente_id=cliente_id,
                    usuario_id=usuario_id,
                    rtn=rtn,
                    fecha=datetime.utcnow(),
                    subtotal=subtotal,
                    isv=isv,
                    total=total,
                    pago_inicial=pago,
                    saldo=saldo,
                    estado=estado,
                )
                db.session.add(factura)
                db.session.flush()
                for producto, cantidad, precio, linea in detalles:
                    db.session.add(
                        DetalleFacturaCredito(
                            factura_id=factura.id,
                            producto_id=producto.id,
                            cantidad=cantidad,
                            precio_unitario=precio,
                            subtotal=linea,
                            isv_aplica=producto.isv_aplica,
                        )
                    )

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"error": "No se pudo guardar la factura."}), 500

        return jsonify(
            {
                "numero_factura": numero_factura,
                "total": float(total),
                "tipo": tipo,
            }
        )

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Tablas creadas o verificadas.")

    @app.cli.command("create-admin")
    @click.option("--username", default="admin", show_default=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, password):
        user = User.query.filter_by(username=username).first()
        if user:
            click.echo("El usuario ya existe.")
            return

        user = User(
            username=username,
            password=generate_password_hash(password),
            nombre_completo="Administrador Invagro",
            email="admin@invagro.com",
            rol="admin",
            activo=True,
        )
        db.session.add(user)
        db.session.commit()
        click.echo("Usuario admin creado.")

    return app


if __name__ == "__main__":
    app = create_app()
    if app.config.get("FLASK_ENV") == "development":
        app.run()
