import logging
import os
import re
import time
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import click
from sqlalchemy import func
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models import (
    AbonoFactura,
    AjustesNegocio,
    Categoria,
    Cliente,
    DetalleFacturaContado,
    FacturaContado,
    Producto,
    User,
    db,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)

    upload_folder = os.path.join(app.static_folder, "uploads", "productos")
    try:
        os.makedirs(upload_folder, exist_ok=True)
    except PermissionError:
        app.logger.warning("No se pudo crear la carpeta de uploads.")
    app.config["PRODUCT_UPLOAD_FOLDER"] = upload_folder
    invoice_folder = os.path.join(app.static_folder, "invoices")
    try:
        os.makedirs(invoice_folder, exist_ok=True)
    except PermissionError:
        app.logger.warning("No se pudo crear la carpeta de facturas.")
    app.config["INVOICE_PDF_FOLDER"] = invoice_folder

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

    def parse_rango_autorizado_inicio(rango_texto):
        if not rango_texto:
            return None
        matches = list(re.finditer(r"\d+", rango_texto))
        if not matches:
            return None
        start_match = matches[-1]
        prefix = rango_texto[: start_match.start()]
        start_raw = start_match.group(0)
        try:
            start_num = int(start_raw)
        except ValueError:
            return None
        return {"prefix": prefix, "start_num": start_num, "width": len(start_raw)}

    def generate_invoice_number():
        settings = get_business_settings()
        rango_inicio = settings.rango_autorizado_inicio or settings.rango_autorizado or ""
        rango_info = parse_rango_autorizado_inicio(rango_inicio)
        if not rango_info:
            return f"F001-{datetime.utcnow():%Y%m%d%H%M%S}"

        last_invoice = FacturaContado.query.order_by(FacturaContado.id.desc()).first()
        next_num = rango_info["start_num"]
        if last_invoice and last_invoice.numero_factura:
            if last_invoice.numero_factura.startswith(rango_info["prefix"]):
                suffix = last_invoice.numero_factura[len(rango_info["prefix"]):]
                if suffix.isdigit():
                    next_num = int(suffix) + 1

        return f"{rango_info['prefix']}{next_num:0{rango_info['width']}d}"

    def build_invoice_pdf_filename(numero_factura, token=None):
        safe_base = re.sub(r"[\\/\\s]+", "-", numero_factura).strip("-")
        safe_name = secure_filename(safe_base) or "factura"
        if token:
            safe_token = re.sub(r"[^a-zA-Z0-9_-]+", "", token)
            if safe_token:
                safe_name = f"{safe_name}-{safe_token}"
        return f"{safe_name}.pdf"

    def cleanup_old_pdfs(folder_path, max_age_seconds=86400, prefix=None):
        cutoff = time.time() - max_age_seconds
        try:
            for name in os.listdir(folder_path):
                if not name.lower().endswith(".pdf"):
                    continue
                if prefix and not name.startswith(prefix):
                    continue
                file_path = os.path.join(folder_path, name)
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff:
                    os.remove(file_path)
        except OSError:
            app.logger.warning("No se pudo limpiar PDFs antiguos.")

    def get_business_settings():
        settings = AjustesNegocio.query.first()
        if settings:
            return settings
        settings = AjustesNegocio(
            nombre="Invagro",
            rtn="",
            telefono="",
            email="",
            direccion="",
            cai="",
            rango_autorizado="",
            rango_autorizado_inicio="",
            rango_autorizado_fin="",
            fecha_limite_emision="",
            mensaje="",
        )
        db.session.add(settings)
        db.session.commit()
        return settings

    def create_invoice_pdf(file_path, settings, invoice, detalles, tipo, cliente, usuario):
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            leftMargin=22,
            rightMargin=22,
            topMargin=22,
            bottomMargin=22,
        )
        story = []
        usable_height = doc.height
        logo_path = os.path.join(app.static_folder, "assets", "logo.jpg")
        logo_image = None
        if os.path.exists(logo_path):
            logo_image = Image(logo_path, width=60, height=60)

        header_center = (
            f"<b>{settings.nombre}</b><br/>"
            f"{settings.direccion or ''}<br/>"
            f"RTN: {settings.rtn or '-'} &nbsp;&nbsp; TEL: {settings.telefono or '-'}<br/>"
            f"{settings.email or ''}"
        )
        header_right = (
            f"<b>FACTURA</b><br/>{invoice.numero_factura}<br/>"
            f"FECHA: {invoice.fecha.strftime('%d/%m/%Y %I:%M %p')}"
        )
        header_table = Table(
            [[logo_image or "", Paragraph(header_center, styles["Normal"]), Paragraph(header_right, styles["Normal"])]],
            colWidths=[90, 300, 130],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 6))

        cliente_nombre = cliente.nombre if cliente else "N/A"
        cliente_telefono = cliente.telefono if cliente else "-"
        cliente_line = (
            f"<b>CLIENTE:</b> {cliente_nombre} &nbsp;&nbsp; "
            f"<b>RTN:</b> {invoice.rtn or '-'} &nbsp;&nbsp; "
            f"<b>TEL:</b> {cliente_telefono}"
        )
        cliente_paragraph = Paragraph(cliente_line, styles["Normal"])
        story.append(cliente_paragraph)
        story.append(Spacer(1, 4))

        tipo_texto = "CONTADO" if tipo == "contado" else "CREDITO"
        vendedor = usuario.nombre_completo if usuario and usuario.nombre_completo else "General"
        estado = invoice.estado.upper() if invoice.estado else "-"
        meta_line = (
            f"<b>CAJERO:</b> {vendedor} &nbsp;&nbsp; "
            f"<b>VENDEDOR:</b> GENERAL &nbsp;&nbsp; "
            f"<b>TERMINOS:</b> {tipo_texto} &nbsp;&nbsp; "
            f"<b>ESTADO:</b> {estado}"
        )
        meta_paragraph = Paragraph(meta_line, styles["Normal"])
        story.append(meta_paragraph)
        story.append(Spacer(1, 6))

        data = [
            [
                "CODIGO",
                "DESCRIPCION",
                "UNIDAD",
                "CANTIDAD",
                "PRECIO UNIT.",
                "DESCTO",
                "ISV %",
                "TOTAL",
            ]
        ]
        exento_total = Decimal("0")
        gravado_total = Decimal("0")
        for detalle in detalles:
            producto = detalle["producto"]
            isv_text = "15%" if detalle["isv_aplica"] else "0%"
            if detalle["isv_aplica"]:
                gravado_total += Decimal(str(detalle["subtotal"]))
            else:
                exento_total += Decimal(str(detalle["subtotal"]))
            descuento_linea = Decimal(str(detalle.get("descuento", 0) or 0))
            data.append(
                [
                    producto.codigo,
                    producto.nombre,
                    "UNIDAD",
                    str(detalle["cantidad"]),
                    f"L {detalle['precio']:.2f}",
                    f"L {descuento_linea:.2f}",
                    isv_text,
                    f"L {detalle['subtotal']:.2f}",
                ]
            )
        def build_product_table(rows, header_font_size, body_font_size):
            table_instance = Table(rows, colWidths=[50, 195, 50, 50, 68, 45, 35, 45])
            table_instance.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), header_font_size),
                        ("FONTSIZE", (0, 1), (-1, -1), body_font_size),
                        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 2),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ]
                )
            )
            return table_instance

        isv_total = gravado_total * Decimal("0.15")
        total_final = Decimal(str(invoice.total or 0))
        descuento_valor = Decimal(str(getattr(invoice, "descuento", 0) or 0))
        totals_data = [
            ["DESCUENTOS Y REBAJAS", f"L {descuento_valor:.2f}"],
            ["SUBTOTAL", f"L {invoice.subtotal:.2f}"],
            ["IMPORTE EXENTO", f"L {exento_total:.2f}"],
            ["IMPORTE EXONERADO", "L 0.00"],
            ["IMPORTE GRAVADO 15%", f"L {gravado_total:.2f}"],
            ["ISV 15.00%", f"L {isv_total:.2f}"],
            ["TOTAL A PAGAR", f"L {total_final:.2f}"],
        ]
        totals_table = Table(totals_data, colWidths=[130, 85], hAlign="RIGHT")
        totals_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        notes_text = (
            "<b>DATOS DEL ADQUIRENTE EXONERADO</b><br/>"
            "N° ORDEN DE COMPRA EXENTA:<br/>"
            "N° CONST. REGISTRO EXONERADO:<br/>"
            "N° REGISTRO SAG:"
        )
        notes_paragraph = Paragraph(notes_text, styles["Normal"])
        bottom_block = Table(
            [[notes_paragraph, totals_table]],
            colWidths=[doc.width - 215, 215],
        )
        bottom_block.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ]
            )
        )

        # Calculate heights to stretch the product table and pin footer to the page bottom.
        header_height = header_table.wrap(doc.width, usable_height)[1]
        cliente_height = cliente_paragraph.wrap(doc.width, usable_height)[1]
        meta_height = meta_paragraph.wrap(doc.width, usable_height)[1]
        bottom_height = bottom_block.wrap(doc.width, usable_height)[1]

        item_count = max(0, len(data) - 1)
        if item_count > 18:
            header_font_size = 7
            body_font_size = 8
        elif item_count > 12:
            header_font_size = 8
            body_font_size = 9
        else:
            header_font_size = 8
            body_font_size = 9

        product_table = build_product_table(data, header_font_size, body_font_size)
        product_table.wrap(doc.width, usable_height)
        base_table_height = product_table._height
        row_height = product_table._rowHeights[1] if len(product_table._rowHeights) > 1 else 18
        reserved_spacing = 6 + 4 + 6  # spacers after header, cliente y meta
        extra_bottom_space = 142  # ~5 cm to leave room for legal/footer lines
        target_table_height = max(
            0,
            usable_height
            - (header_height + cliente_height + meta_height + bottom_height + reserved_spacing)
            - extra_bottom_space,
        )
        if base_table_height < target_table_height and row_height:
            extra_rows = int((target_table_height - base_table_height) / row_height)
            if extra_rows > 0:
                data.extend([["", "", "", "", "", "", "", ""]] * extra_rows)
                product_table = build_product_table(data, header_font_size, body_font_size)

        story.append(product_table)
        story.append(Spacer(1, 4))
        story.append(KeepTogether([bottom_block]))
        story.append(Spacer(1, 4))

        footer_blocks = []
        if settings.mensaje:
            footer_blocks.append(Paragraph(settings.mensaje, styles["Normal"]))
        rango_texto = ""
        if settings.rango_autorizado_inicio or settings.rango_autorizado_fin:
            inicio = settings.rango_autorizado_inicio or "-"
            fin = settings.rango_autorizado_fin or "-"
            rango_texto = f"{inicio} - {fin}"
        elif settings.rango_autorizado:
            rango_texto = settings.rango_autorizado
        if settings.cai or rango_texto or settings.fecha_limite_emision:
            footer_text = (
                f"CAI: {settings.cai or '-'}<br/>"
                f"RANGO AUTORIZADO: {rango_texto or '-'}<br/>"
                f"FECHA LIMITE DE EMISION: {settings.fecha_limite_emision or '-'}"
            )
            footer_blocks.append(Paragraph(footer_text, styles["Normal"]))
        if footer_blocks:
            story.append(KeepTogether(footer_blocks))
        doc.build(story)

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

        now = datetime.utcnow()
        cutoff = now - timedelta(days=30)

        try:
            clientes_count = Cliente.query.count()
            productos_count = Producto.query.filter_by(activo=True).count()
            facturas_credito_count = FacturaContado.query.filter_by(estado="credito").count()
            credito_total = (
                db.session.query(func.coalesce(func.sum(FacturaContado.total), 0))
                .filter(FacturaContado.estado == "credito")
                .scalar()
                or 0
            )
            credito_menor_30 = (
                db.session.query(func.coalesce(func.sum(FacturaContado.total), 0))
                .filter(
                    FacturaContado.estado == "credito",
                    FacturaContado.fecha >= cutoff,
                )
                .scalar()
                or 0
            )
            credito_mayor_30 = (
                db.session.query(func.coalesce(func.sum(FacturaContado.total), 0))
                .filter(
                    FacturaContado.estado == "credito",
                    FacturaContado.fecha < cutoff,
                )
                .scalar()
                or 0
            )
        except SQLAlchemyError:
            db.session.rollback()
            clientes_count = 0
            productos_count = 0
            facturas_credito_count = 0
            credito_total = 0
            credito_menor_30 = 0
            credito_mayor_30 = 0

        return render_template(
            "dashboard.html",
            user=session["user"],
            clientes_count=clientes_count,
            productos_count=productos_count,
            facturas_credito_count=facturas_credito_count,
            credito_total=credito_total,
            credito_menor_30=credito_menor_30,
            credito_mayor_30=credito_mayor_30,
        )

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

        productos_list = Producto.query.filter_by(activo=True).order_by(Producto.id.desc()).all()
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

        try:
            clientes_data = [
                {
                    "id": cliente.id,
                    "nombre": cliente.nombre,
                    "rtn": cliente.ruc_dni or "",
                    "telefono": cliente.telefono or "",
                }
                for cliente in Cliente.query.order_by(Cliente.nombre.asc()).all()
            ]
            facturas_raw = (
                FacturaContado.query.filter_by(estado="credito")
                .order_by(FacturaContado.fecha.desc())
                .all()
            )
            facturas_credito = []
            for factura in facturas_raw:
                total = Decimal(str(factura.total or 0))
                abonado = Decimal(str(factura.pago or 0))
                saldo = total - abonado
                if saldo <= 0:
                    continue
                facturas_credito.append(
                    {
                        "id": factura.id,
                        "numero_factura": factura.numero_factura,
                        "cliente_id": factura.cliente_id,
                        "fecha": factura.fecha.strftime("%d/%m/%Y")
                        if factura.fecha
                        else "-",
                        "total": float(total),
                        "abonado": float(abonado),
                        "saldo": float(saldo),
                    }
                )
        except SQLAlchemyError:
            db.session.rollback()
            clientes_data = []
            facturas_credito = []

        return render_template(
            "reportes.html",
            user=session["user"],
            clientes=clientes_data,
            facturas_credito=facturas_credito,
        )

    def parse_report_date_range(start_raw, end_raw):
        today = datetime.utcnow()
        if start_raw:
            start_date = datetime.strptime(start_raw, "%Y-%m-%d")
        else:
            start_date = datetime(today.year, today.month, 1)
        if end_raw:
            end_date = datetime.strptime(end_raw, "%Y-%m-%d")
        else:
            end_date = today
        if end_date < start_date:
            raise ValueError("Rango de fechas invalido.")
        end_exclusive = end_date + timedelta(days=1)
        return start_date, end_exclusive

    @app.post("/reportes/productos-top")
    def reportes_productos_top():
        if not session.get("user"):
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        start_raw = (data.get("start_date") or "").strip()
        end_raw = (data.get("end_date") or "").strip()
        try:
            start_date, end_exclusive = parse_report_date_range(start_raw, end_raw)
        except ValueError:
            return jsonify({"error": "Rango de fechas invalido."}), 400

        rows = (
            db.session.query(
                Producto.codigo,
                Producto.nombre,
                func.sum(DetalleFacturaContado.cantidad).label("cantidad"),
                func.sum(DetalleFacturaContado.subtotal).label("total"),
            )
            .join(
                DetalleFacturaContado,
                DetalleFacturaContado.producto_id == Producto.id,
            )
            .join(
                FacturaContado,
                FacturaContado.id == DetalleFacturaContado.factura_id,
            )
            .filter(FacturaContado.estado != "anulada")
            .filter(FacturaContado.fecha >= start_date)
            .filter(FacturaContado.fecha < end_exclusive)
            .group_by(Producto.codigo, Producto.nombre)
            .order_by(func.sum(DetalleFacturaContado.cantidad).desc())
            .limit(50)
            .all()
        )

        productos = [
            {
                "codigo": row.codigo,
                "nombre": row.nombre,
                "cantidad": int(row.cantidad or 0),
                "total": float(row.total or 0),
            }
            for row in rows
        ]
        total_vendido = sum(item["total"] for item in productos)
        return jsonify({"productos": productos, "total": total_vendido})

    @app.post("/reportes/productos-top/pdf")
    def reportes_productos_top_pdf():
        if not session.get("user"):
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        start_raw = (data.get("start_date") or "").strip()
        end_raw = (data.get("end_date") or "").strip()
        try:
            start_date, end_exclusive = parse_report_date_range(start_raw, end_raw)
        except ValueError:
            return jsonify({"error": "Rango de fechas invalido."}), 400

        productos = (
            db.session.query(
                Producto.codigo,
                Producto.nombre,
                func.sum(DetalleFacturaContado.cantidad).label("cantidad"),
                func.sum(DetalleFacturaContado.subtotal).label("total"),
            )
            .join(
                DetalleFacturaContado,
                DetalleFacturaContado.producto_id == Producto.id,
            )
            .join(
                FacturaContado,
                FacturaContado.id == DetalleFacturaContado.factura_id,
            )
            .filter(FacturaContado.estado != "anulada")
            .filter(FacturaContado.fecha >= start_date)
            .filter(FacturaContado.fecha < end_exclusive)
            .group_by(Producto.codigo, Producto.nombre)
            .order_by(func.sum(DetalleFacturaContado.cantidad).desc())
            .limit(50)
            .all()
        )
        productos_data = [
            {
                "codigo": row.codigo,
                "nombre": row.nombre,
                "cantidad": int(row.cantidad or 0),
                "total": float(row.total or 0),
            }
            for row in productos
        ]
        total_vendido = sum(item["total"] for item in productos_data)
        settings = get_business_settings()
        safe_base = f"top-productos-{datetime.utcnow():%Y%m%d%H%M%S}"
        filename = build_invoice_pdf_filename(safe_base)
        file_path = os.path.join(app.config["INVOICE_PDF_FOLDER"], filename)
        cleanup_old_pdfs(app.config["INVOICE_PDF_FOLDER"], prefix="top-productos-")
        create_top_products_pdf(
            file_path, settings, productos_data, total_vendido, start_date, end_exclusive
        )
        pdf_url = url_for("static", filename=f"invoices/{filename}", _external=True)
        return jsonify({"pdf_url": pdf_url})

    @app.post("/reportes/compras-cliente")
    def reportes_compras_cliente():
        if not session.get("user"):
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        cliente_id = data.get("cliente_id")
        if not cliente_id:
            return jsonify({"error": "Cliente requerido"}), 400
        try:
            cliente_id = int(cliente_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Cliente invalido"}), 400

        start_raw = (data.get("start_date") or "").strip()
        end_raw = (data.get("end_date") or "").strip()
        try:
            start_date, end_exclusive = parse_report_date_range(start_raw, end_raw)
        except ValueError:
            return jsonify({"error": "Rango de fechas invalido."}), 400

        facturas = (
            FacturaContado.query.filter_by(cliente_id=cliente_id)
            .filter(FacturaContado.estado != "anulada")
            .filter(FacturaContado.fecha >= start_date)
            .filter(FacturaContado.fecha < end_exclusive)
            .order_by(FacturaContado.fecha.desc())
            .all()
        )

        items = [
            {
                "numero_factura": factura.numero_factura,
                "fecha": factura.fecha.strftime("%d/%m/%Y") if factura.fecha else "-",
                "total": float(factura.total or 0),
                "estado": factura.estado or "-",
            }
            for factura in facturas
        ]
        total_compras = sum(item["total"] for item in items)
        return jsonify({"facturas": items, "total": total_compras})

    @app.post("/reportes/compras-cliente/pdf")
    def reportes_compras_cliente_pdf():
        if not session.get("user"):
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        cliente_id = data.get("cliente_id")
        if not cliente_id:
            return jsonify({"error": "Cliente requerido"}), 400
        try:
            cliente_id = int(cliente_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Cliente invalido"}), 400

        start_raw = (data.get("start_date") or "").strip()
        end_raw = (data.get("end_date") or "").strip()
        try:
            start_date, end_exclusive = parse_report_date_range(start_raw, end_raw)
        except ValueError:
            return jsonify({"error": "Rango de fechas invalido."}), 400

        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        facturas = (
            FacturaContado.query.filter_by(cliente_id=cliente_id)
            .filter(FacturaContado.estado != "anulada")
            .filter(FacturaContado.fecha >= start_date)
            .filter(FacturaContado.fecha < end_exclusive)
            .order_by(FacturaContado.fecha.desc())
            .all()
        )
        facturas_data = [
            {
                "numero_factura": factura.numero_factura,
                "fecha": factura.fecha.strftime("%d/%m/%Y") if factura.fecha else "-",
                "estado": factura.estado or "-",
                "total": float(factura.total or 0),
            }
            for factura in facturas
        ]
        total_compras = sum(item["total"] for item in facturas_data)
        settings = get_business_settings()
        safe_base = f"compras-cliente-{cliente_id}-{datetime.utcnow():%Y%m%d%H%M%S}"
        filename = build_invoice_pdf_filename(safe_base)
        file_path = os.path.join(app.config["INVOICE_PDF_FOLDER"], filename)
        cleanup_old_pdfs(app.config["INVOICE_PDF_FOLDER"], prefix="compras-cliente-")
        create_client_purchases_pdf(
            file_path,
            settings,
            cliente,
            facturas_data,
            total_compras,
            start_date,
            end_exclusive,
        )
        pdf_url = url_for("static", filename=f"invoices/{filename}", _external=True)
        return jsonify({"pdf_url": pdf_url})

    def query_productos_por_cliente(cliente_id, start_date, end_exclusive):
        rows = (
            db.session.query(
                Producto.codigo,
                Producto.nombre,
                func.sum(DetalleFacturaContado.cantidad).label("cantidad"),
                func.sum(DetalleFacturaContado.subtotal).label("total"),
            )
            .join(
                DetalleFacturaContado,
                DetalleFacturaContado.producto_id == Producto.id,
            )
            .join(
                FacturaContado,
                FacturaContado.id == DetalleFacturaContado.factura_id,
            )
            .filter(FacturaContado.estado != "anulada")
            .filter(FacturaContado.cliente_id == cliente_id)
            .filter(FacturaContado.fecha >= start_date)
            .filter(FacturaContado.fecha < end_exclusive)
            .group_by(Producto.codigo, Producto.nombre)
            .order_by(func.sum(DetalleFacturaContado.cantidad).desc())
            .all()
        )
        return [
            {
                "codigo": row.codigo,
                "nombre": row.nombre,
                "cantidad": int(row.cantidad or 0),
                "total": float(row.total or 0),
            }
            for row in rows
        ]

    @app.post("/reportes/productos-cliente")
    def reportes_productos_cliente():
        if not session.get("user"):
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        cliente_id = data.get("cliente_id")
        if not cliente_id:
            return jsonify({"error": "Cliente requerido"}), 400
        try:
            cliente_id = int(cliente_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Cliente invalido"}), 400

        start_raw = (data.get("start_date") or "").strip()
        end_raw = (data.get("end_date") or "").strip()
        try:
            start_date, end_exclusive = parse_report_date_range(start_raw, end_raw)
        except ValueError:
            return jsonify({"error": "Rango de fechas invalido."}), 400

        productos = query_productos_por_cliente(cliente_id, start_date, end_exclusive)
        total_compras = sum(item["total"] for item in productos)
        return jsonify({"productos": productos, "total": total_compras})

    @app.post("/reportes/productos-cliente/pdf")
    def reportes_productos_cliente_pdf():
        if not session.get("user"):
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        cliente_id = data.get("cliente_id")
        if not cliente_id:
            return jsonify({"error": "Cliente requerido"}), 400
        try:
            cliente_id = int(cliente_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Cliente invalido"}), 400

        start_raw = (data.get("start_date") or "").strip()
        end_raw = (data.get("end_date") or "").strip()
        try:
            start_date, end_exclusive = parse_report_date_range(start_raw, end_raw)
        except ValueError:
            return jsonify({"error": "Rango de fechas invalido."}), 400

        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        productos = query_productos_por_cliente(cliente_id, start_date, end_exclusive)
        total_compras = sum(item["total"] for item in productos)
        settings = get_business_settings()
        safe_base = f"productos-cliente-{cliente_id}-{datetime.utcnow():%Y%m%d%H%M%S}"
        filename = build_invoice_pdf_filename(safe_base)
        file_path = os.path.join(app.config["INVOICE_PDF_FOLDER"], filename)
        cleanup_old_pdfs(app.config["INVOICE_PDF_FOLDER"], prefix="productos-cliente-")
        create_products_by_client_pdf(
            file_path, settings, cliente, productos, total_compras, start_date, end_exclusive
        )
        pdf_url = url_for("static", filename=f"invoices/{filename}", _external=True)
        return jsonify({"pdf_url": pdf_url})

    def create_account_statement_pdf(file_path, settings, cliente, facturas, total_saldo):
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            leftMargin=22,
            rightMargin=22,
            topMargin=22,
            bottomMargin=22,
        )
        story = []
        logo_path = os.path.join(app.static_folder, "assets", "logo.jpg")
        logo_image = None
        if os.path.exists(logo_path):
            logo_image = Image(logo_path, width=60, height=60)

        header_center = (
            f"<b>{settings.nombre}</b><br/>"
            f"{settings.direccion or ''}<br/>"
            f"RTN: {settings.rtn or '-'} &nbsp;&nbsp; TEL: {settings.telefono or '-'}<br/>"
            f"{settings.email or ''}"
        )
        header_right = f"<b>ESTADO DE CUENTA</b><br/>FECHA: {datetime.utcnow():%d/%m/%Y}"
        header_table = Table(
            [
                [
                    logo_image or "",
                    Paragraph(header_center, styles["Normal"]),
                    Paragraph(header_right, styles["Normal"]),
                ]
            ],
            colWidths=[90, 300, 130],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 10))

        cliente_line = (
            f"<b>CLIENTE:</b> {cliente.nombre} &nbsp;&nbsp; "
            f"<b>RTN:</b> {cliente.ruc_dni or '-'} &nbsp;&nbsp; "
            f"<b>TEL:</b> {cliente.telefono or '-'}"
        )
        story.append(Paragraph(cliente_line, styles["Normal"]))
        story.append(Spacer(1, 8))

        table_data = [["FACTURA", "FECHA", "TOTAL", "ABONADO", "SALDO"]]
        for factura in facturas:
            table_data.append(
                [
                    factura["numero_factura"],
                    factura["fecha"],
                    f"L {factura['total']:.2f}",
                    f"L {factura['abonado']:.2f}",
                    f"L {factura['saldo']:.2f}",
                ]
            )
        table = Table(table_data, colWidths=[120, 90, 90, 90, 90])
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

        total_table = Table(
            [["TOTAL PENDIENTE", f"L {total_saldo:.2f}"]],
            colWidths=[150, 120],
        )
        total_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(total_table)
        doc.build(story)

    def create_products_by_client_pdf(
        file_path, settings, cliente, productos, total_compras, start_date, end_exclusive
    ):
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            leftMargin=22,
            rightMargin=22,
            topMargin=22,
            bottomMargin=22,
        )
        story = []
        logo_path = os.path.join(app.static_folder, "assets", "logo.jpg")
        logo_image = None
        if os.path.exists(logo_path):
            logo_image = Image(logo_path, width=60, height=60)

        header_center = (
            f"<b>{settings.nombre}</b><br/>"
            f"{settings.direccion or ''}<br/>"
            f"RTN: {settings.rtn or '-'} &nbsp;&nbsp; TEL: {settings.telefono or '-'}<br/>"
            f"{settings.email or ''}"
        )
        rango_texto = (
            f"{start_date:%d/%m/%Y} - {(end_exclusive - timedelta(days=1)):%d/%m/%Y}"
        )
        header_right = f"<b>PRODUCTOS POR CLIENTE</b><br/>RANGO: {rango_texto}"
        header_table = Table(
            [
                [
                    logo_image or "",
                    Paragraph(header_center, styles["Normal"]),
                    Paragraph(header_right, styles["Normal"]),
                ]
            ],
            colWidths=[90, 300, 130],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 10))

        cliente_line = (
            f"<b>CLIENTE:</b> {cliente.nombre} &nbsp;&nbsp; "
            f"<b>RTN:</b> {cliente.ruc_dni or '-'} &nbsp;&nbsp; "
            f"<b>TEL:</b> {cliente.telefono or '-'}"
        )
        story.append(Paragraph(cliente_line, styles["Normal"]))
        story.append(Spacer(1, 8))

        table_data = [["CODIGO", "PRODUCTO", "UNIDADES", "TOTAL"]]
        for producto in productos:
            table_data.append(
                [
                    producto["codigo"],
                    producto["nombre"],
                    str(producto["cantidad"]),
                    f"L {producto['total']:.2f}",
                ]
            )
        table = Table(table_data, colWidths=[90, 230, 90, 90])
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

        total_table = Table(
            [["TOTAL COMPRADO", f"L {total_compras:.2f}"]],
            colWidths=[150, 120],
        )
        total_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(total_table)
        doc.build(story)

    def create_top_products_pdf(
        file_path, settings, productos, total_vendido, start_date, end_exclusive
    ):
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            leftMargin=22,
            rightMargin=22,
            topMargin=22,
            bottomMargin=22,
        )
        story = []
        logo_path = os.path.join(app.static_folder, "assets", "logo.jpg")
        logo_image = None
        if os.path.exists(logo_path):
            logo_image = Image(logo_path, width=60, height=60)

        header_center = (
            f"<b>{settings.nombre}</b><br/>"
            f"{settings.direccion or ''}<br/>"
            f"RTN: {settings.rtn or '-'} &nbsp;&nbsp; TEL: {settings.telefono or '-'}<br/>"
            f"{settings.email or ''}"
        )
        rango_texto = (
            f"{start_date:%d/%m/%Y} - {(end_exclusive - timedelta(days=1)):%d/%m/%Y}"
        )
        header_right = f"<b>TOP PRODUCTOS</b><br/>RANGO: {rango_texto}"
        header_table = Table(
            [
                [
                    logo_image or "",
                    Paragraph(header_center, styles["Normal"]),
                    Paragraph(header_right, styles["Normal"]),
                ]
            ],
            colWidths=[90, 300, 130],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 10))

        table_data = [["CODIGO", "PRODUCTO", "UNIDADES", "TOTAL"]]
        for producto in productos:
            table_data.append(
                [
                    producto["codigo"],
                    producto["nombre"],
                    str(producto["cantidad"]),
                    f"L {producto['total']:.2f}",
                ]
            )
        table = Table(table_data, colWidths=[90, 230, 90, 90])
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

        total_table = Table(
            [["TOTAL VENDIDO", f"L {total_vendido:.2f}"]],
            colWidths=[150, 120],
        )
        total_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(total_table)
        doc.build(story)

    def create_client_purchases_pdf(
        file_path, settings, cliente, facturas, total_compras, start_date, end_exclusive
    ):
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            leftMargin=22,
            rightMargin=22,
            topMargin=22,
            bottomMargin=22,
        )
        story = []
        logo_path = os.path.join(app.static_folder, "assets", "logo.jpg")
        logo_image = None
        if os.path.exists(logo_path):
            logo_image = Image(logo_path, width=60, height=60)

        header_center = (
            f"<b>{settings.nombre}</b><br/>"
            f"{settings.direccion or ''}<br/>"
            f"RTN: {settings.rtn or '-'} &nbsp;&nbsp; TEL: {settings.telefono or '-'}<br/>"
            f"{settings.email or ''}"
        )
        rango_texto = (
            f"{start_date:%d/%m/%Y} - {(end_exclusive - timedelta(days=1)):%d/%m/%Y}"
        )
        header_right = f"<b>COMPRAS POR CLIENTE</b><br/>RANGO: {rango_texto}"
        header_table = Table(
            [
                [
                    logo_image or "",
                    Paragraph(header_center, styles["Normal"]),
                    Paragraph(header_right, styles["Normal"]),
                ]
            ],
            colWidths=[90, 300, 130],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 10))

        cliente_line = (
            f"<b>CLIENTE:</b> {cliente.nombre} &nbsp;&nbsp; "
            f"<b>RTN:</b> {cliente.ruc_dni or '-'} &nbsp;&nbsp; "
            f"<b>TEL:</b> {cliente.telefono or '-'}"
        )
        story.append(Paragraph(cliente_line, styles["Normal"]))
        story.append(Spacer(1, 8))

        table_data = [["FACTURA", "FECHA", "ESTADO", "TOTAL"]]
        for factura in facturas:
            table_data.append(
                [
                    factura["numero_factura"],
                    factura["fecha"],
                    factura["estado"],
                    f"L {factura['total']:.2f}",
                ]
            )
        table = Table(table_data, colWidths=[130, 90, 90, 90])
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (3, 1), (3, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

        total_table = Table(
            [["TOTAL COMPRADO", f"L {total_compras:.2f}"]],
            colWidths=[150, 120],
        )
        total_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(total_table)
        doc.build(story)

    @app.post("/reportes/estado-cuenta/pdf")
    def reportes_estado_cuenta_pdf():
        if not session.get("user"):
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        cliente_id = data.get("cliente_id")
        if not cliente_id:
            return jsonify({"error": "Cliente requerido"}), 400
        try:
            cliente_id = int(cliente_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Cliente invalido"}), 400

        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        facturas_raw = (
            FacturaContado.query.filter_by(estado="credito", cliente_id=cliente_id)
            .order_by(FacturaContado.fecha.asc())
            .all()
        )
        facturas_credito = []
        total_saldo = Decimal("0")
        for factura in facturas_raw:
            total = Decimal(str(factura.total or 0))
            abonado = Decimal(str(factura.pago or 0))
            saldo = total - abonado
            if saldo <= 0:
                continue
            total_saldo += saldo
            facturas_credito.append(
                {
                    "numero_factura": factura.numero_factura,
                    "fecha": factura.fecha.strftime("%d/%m/%Y")
                    if factura.fecha
                    else "-",
                    "total": float(total),
                    "abonado": float(abonado),
                    "saldo": float(saldo),
                }
            )
        settings = get_business_settings()
        safe_base = f"estado-cuenta-{cliente_id}-{datetime.utcnow():%Y%m%d%H%M%S}"
        filename = build_invoice_pdf_filename(safe_base)
        file_path = os.path.join(app.config["INVOICE_PDF_FOLDER"], filename)
        cleanup_old_pdfs(app.config["INVOICE_PDF_FOLDER"], prefix="estado-cuenta-")
        create_account_statement_pdf(
            file_path, settings, cliente, facturas_credito, total_saldo
        )
        pdf_url = url_for("static", filename=f"invoices/{filename}")
        return jsonify({"pdf_url": pdf_url})

    @app.route("/ajustes", methods=["GET", "POST"])
    def ajustes():
        if not session.get("user"):
            return redirect(url_for("login"))

        settings = AjustesNegocio.query.first()
        if not settings:
            settings = AjustesNegocio(nombre="Invagro")
            db.session.add(settings)
            db.session.commit()

        if request.method == "POST":
            settings.nombre = request.form.get("nombre", "").strip() or "Invagro"
            settings.rtn = request.form.get("rtn", "").strip()
            settings.telefono = request.form.get("telefono", "").strip()
            settings.email = request.form.get("email", "").strip()
            settings.direccion = request.form.get("direccion", "").strip()
            settings.cai = request.form.get("cai", "").strip()
            settings.rango_autorizado = request.form.get("rango_autorizado", "").strip()
            settings.rango_autorizado_inicio = request.form.get(
                "rango_autorizado_inicio", ""
            ).strip()
            settings.rango_autorizado_fin = request.form.get(
                "rango_autorizado_fin", ""
            ).strip()
            settings.fecha_limite_emision = request.form.get("fecha_limite_emision", "").strip()
            settings.mensaje = request.form.get("mensaje", "").strip()
            db.session.commit()
            return redirect(url_for("ajustes"))

        return render_template("ajustes.html", user=session["user"], settings=settings)

    @app.get("/facturas/credito")
    def facturas_credito():
        if not session.get("user"):
            return redirect(url_for("login"))

        try:
            facturas_raw = FacturaContado.query.filter_by(estado="credito").order_by(
                FacturaContado.fecha.desc()
            ).all()
        except SQLAlchemyError:
            db.session.rollback()
            facturas_raw = []
        facturas = []
        for factura in facturas_raw:
            fecha_label = factura.fecha.strftime("%d/%m/%Y") if factura.fecha else "-"
            abonado = factura.pago or Decimal("0")
            saldo = (factura.total or Decimal("0")) - abonado
            facturas.append(
                {
                    "id": factura.id,
                    "numero_factura": factura.numero_factura,
                    "cliente_id": factura.cliente_id,
                    "fecha": factura.fecha,
                    "fecha_label": fecha_label,
                    "total": factura.total,
                    "abonado": abonado,
                    "saldo": saldo,
                    "estado_label": "credito",
                    "pdf_filename": factura.pdf_filename,
                }
            )
        clientes = Cliente.query.all()
        clientes_map = {cliente.id: cliente.nombre for cliente in clientes}
        return render_template(
            "facturas_credito.html",
            user=session["user"],
            facturas=facturas,
            clientes_map=clientes_map,
        )

    @app.post("/facturas/credito/<int:factura_id>/cobrar")
    def cobrar_factura_credito(factura_id):
        if not session.get("user"):
            return redirect(url_for("login"))

        try:
            factura = FacturaContado.query.get_or_404(factura_id)
        except SQLAlchemyError:
            db.session.rollback()
            return redirect(url_for("facturas_credito"))
        if factura.estado != "credito":
            return redirect(url_for("facturas_credito"))

        try:
            usuario = User.query.filter_by(username=session["user"]).first()
            usuario_id = usuario.id if usuario else None
            saldo = (factura.total or Decimal("0")) - (factura.pago or Decimal("0"))
            if saldo > 0:
                db.session.add(
                    AbonoFactura(
                        factura_id=factura.id,
                        usuario_id=usuario_id,
                        monto=saldo,
                        fecha=datetime.utcnow(),
                    )
                )
            factura.estado = "pagada"
            factura.pago = factura.total
            factura.cambio = Decimal("0")
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        return redirect(url_for("facturas_credito"))

    @app.post("/facturas/credito/<int:factura_id>/abonos")
    def registrar_abono_factura(factura_id):
        if not session.get("user"):
            return redirect(url_for("login"))

        try:
            monto_raw = request.form.get("monto", "0").strip()
            monto = Decimal(monto_raw)
        except Exception:
            return redirect(url_for("facturas_credito"))
        if monto <= 0:
            return redirect(url_for("facturas_credito"))

        factura = FacturaContado.query.get_or_404(factura_id)
        if factura.estado != "credito":
            return redirect(url_for("facturas_credito"))

        pago_actual = factura.pago or Decimal("0")
        saldo = (factura.total or Decimal("0")) - pago_actual
        if monto > saldo:
            return redirect(url_for("facturas_credito"))

        try:
            usuario = User.query.filter_by(username=session["user"]).first()
            usuario_id = usuario.id if usuario else None
            db.session.add(
                AbonoFactura(
                    factura_id=factura.id,
                    usuario_id=usuario_id,
                    monto=monto,
                    fecha=datetime.utcnow(),
                )
            )
            factura.pago = pago_actual + monto
            nuevo_saldo = saldo - monto
            if nuevo_saldo <= 0:
                factura.estado = "pagada"
                factura.cambio = Decimal("0")
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        return redirect(url_for("facturas_credito"))

    @app.get("/facturas/historial")
    def facturas_historial():
        if not session.get("user"):
            return redirect(url_for("login"))

        try:
            facturas_contado = FacturaContado.query.order_by(
                FacturaContado.fecha.desc()
            ).all()
        except SQLAlchemyError:
            db.session.rollback()
            facturas_contado = []
        facturas = []
        for factura in facturas_contado:
            fecha_label = factura.fecha.strftime("%d/%m/%Y") if factura.fecha else "-"
            if factura.estado == "credito":
                estado_label = "credito"
            elif factura.estado == "pagada":
                estado_label = "pagada"
            elif factura.estado == "anulada":
                estado_label = "anulada"
            else:
                estado_label = "contado"
            facturas.append(
                {
                    "id": factura.id,
                    "tipo": "credito" if estado_label == "credito" else "contado",
                    "numero_factura": factura.numero_factura,
                    "cliente_id": factura.cliente_id,
                    "fecha": factura.fecha,
                    "fecha_label": fecha_label,
                    "total": factura.total,
                    "estado_label": estado_label,
                    "pdf_filename": factura.pdf_filename,
                }
            )
        facturas.sort(
            key=lambda item: item.get("fecha") or datetime.min,
            reverse=True,
        )
        clientes = Cliente.query.all()
        clientes_map = {cliente.id: cliente.nombre for cliente in clientes}
        return render_template(
            "facturas_historial.html",
            user=session["user"],
            facturas=facturas,
            clientes_map=clientes_map,
        )

    @app.route("/facturas/<path:factura_ref>/delete", methods=["POST", "GET"])
    def eliminar_factura(factura_ref):
        if not session.get("user"):
            return redirect(url_for("login"))

        tipo = (request.form.get("tipo", "") or "").strip().lower()
        ref = factura_ref.strip()
        factura_id = None
        numero_ref = None

        if "/" in ref and not tipo:
            factura = FacturaContado.query.filter_by(numero_factura=ref).first()
            if factura:
                try:
                    DetalleFacturaContado.query.filter_by(
                        factura_id=factura.id
                    ).delete(synchronize_session=False)
                    db.session.delete(factura)
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
                return redirect(url_for("facturas_historial"))

        parts = [part for part in ref.split("/") if part]
        if len(parts) == 2 and parts[0] in {"contado", "credito"} and parts[1].isdigit():
            tipo = parts[0]
            factura_id = int(parts[1])
        elif ref.isdigit():
            factura_id = int(ref)
        elif parts and parts[-1].isdigit():
            factura_id = int(parts[-1])
        else:
            numero_ref = ref

        try:
            if tipo in {"contado", "credito"} and factura_id is not None:
                factura = FacturaContado.query.get_or_404(factura_id)
                DetalleFacturaContado.query.filter_by(
                    factura_id=factura_id
                ).delete(synchronize_session=False)
                db.session.delete(factura)
            elif factura_id is not None:
                factura = FacturaContado.query.get(factura_id)
                if not factura:
                    return redirect(url_for("facturas_historial"))
                DetalleFacturaContado.query.filter_by(
                    factura_id=factura_id
                ).delete(synchronize_session=False)
                db.session.delete(factura)
            else:
                factura = None
                if numero_ref:
                    factura = FacturaContado.query.filter_by(
                        numero_factura=numero_ref
                    ).first()
                    if factura:
                        DetalleFacturaContado.query.filter_by(
                            factura_id=factura.id
                        ).delete(synchronize_session=False)
                        db.session.delete(factura)
                    else:
                        return redirect(url_for("facturas_historial"))
                else:
                    return redirect(url_for("facturas_historial"))

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        return redirect(url_for("facturas_historial"))

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
            producto.activo = False
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
        fecha_raw = (data.get("fecha") or "").strip()
        items = data.get("items") or []

        if tipo not in {"contado", "credito"}:
            return jsonify({"error": "Tipo de factura invalido."}), 400
        if not items:
            return jsonify({"error": "No hay productos en la factura."}), 400

        try:
            pago = Decimal(str(pago_raw))
        except Exception:
            return jsonify({"error": "Pago invalido."}), 400
        if fecha_raw:
            try:
                fecha_factura = datetime.strptime(fecha_raw, "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Fecha invalida."}), 400
        else:
            fecha_factura = datetime.utcnow()

        producto_ids = []
        parsed_items = []
        for item in items:
            try:
                producto_id = int(item.get("producto_id"))
                cantidad = int(item.get("cantidad"))
                descuento = Decimal(str(item.get("descuento", 0) or 0))
            except (TypeError, ValueError):
                return jsonify({"error": "Producto o cantidad invalida."}), 400
            if cantidad <= 0:
                return jsonify({"error": "Cantidad invalida."}), 400
            if descuento < 0:
                return jsonify({"error": "Descuento invalido."}), 400
            producto_ids.append(producto_id)
            parsed_items.append((producto_id, cantidad, descuento))

        productos = Producto.query.filter(Producto.id.in_(producto_ids)).all()
        productos_map = {producto.id: producto for producto in productos}
        if len(productos_map) != len(set(producto_ids)):
            return jsonify({"error": "Producto no encontrado."}), 400

        subtotal = Decimal("0")
        isv = Decimal("0")
        descuento_total = Decimal("0")
        detalles = []
        for producto_id, cantidad, descuento in parsed_items:
            producto = productos_map[producto_id]
            precio = Decimal(str(producto.precio))
            linea_bruta = precio * Decimal(cantidad)
            descuento_unit = min(descuento, precio)
            descuento_aplicado = descuento_unit * Decimal(cantidad)
            linea_neta = max(Decimal("0"), (precio - descuento_unit) * Decimal(cantidad))
            subtotal += linea_bruta
            descuento_total += descuento_aplicado
            if producto.isv_aplica:
                isv += linea_neta * Decimal("0.15")
            detalles.append((producto, cantidad, precio, linea_neta, descuento_unit))

        total = max(Decimal("0"), subtotal - descuento_total) + isv
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
                    fecha=fecha_factura,
                    subtotal=subtotal,
                    isv=isv,
                    descuento=descuento_total,
                    total=total,
                    pago=pago,
                    cambio=cambio,
                    estado="contado",
                )
                db.session.add(factura)
                db.session.flush()
                for producto, cantidad, precio, linea, descuento_unit in detalles:
                    db.session.add(
                        DetalleFacturaContado(
                            factura_id=factura.id,
                            producto_id=producto.id,
                            cantidad=cantidad,
                            precio_unitario=precio,
                            subtotal=linea,
                            descuento=descuento_unit,
                            isv_aplica=producto.isv_aplica,
                        )
                    )
            else:
                factura = FacturaContado(
                    numero_factura=numero_factura,
                    cliente_id=cliente_id,
                    usuario_id=usuario_id,
                    rtn=rtn,
                    fecha=fecha_factura,
                    subtotal=subtotal,
                    isv=isv,
                    descuento=descuento_total,
                    total=total,
                    pago=pago,
                    cambio=Decimal("0"),
                    estado="credito",
                )
                db.session.add(factura)
                db.session.flush()
                for producto, cantidad, precio, linea, descuento_unit in detalles:
                    db.session.add(
                        DetalleFacturaContado(
                            factura_id=factura.id,
                            producto_id=producto.id,
                            cantidad=cantidad,
                            precio_unitario=precio,
                            subtotal=linea,
                            descuento=descuento_unit,
                            isv_aplica=producto.isv_aplica,
                        )
                    )

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"error": "No se pudo guardar la factura."}), 500

        pdf_url = None
        try:
            settings = get_business_settings()
            cliente = Cliente.query.get(cliente_id) if cliente_id else None
            detalles_pdf = [
                {
                    "producto": producto,
                    "cantidad": cantidad,
                    "precio": float(precio),
                    "subtotal": float(linea),
                    "descuento": float(descuento_unit),
                    "isv_aplica": producto.isv_aplica,
                }
                for producto, cantidad, precio, linea, descuento_unit in detalles
            ]
            random_token = uuid4().hex[:6]
            pdf_filename = build_invoice_pdf_filename(numero_factura, token=random_token)
            pdf_path = os.path.join(app.config["INVOICE_PDF_FOLDER"], pdf_filename)
            create_invoice_pdf(pdf_path, settings, factura, detalles_pdf, tipo, cliente, usuario)
            factura.pdf_filename = pdf_filename
            db.session.commit()
            pdf_url = url_for("static", filename=f"invoices/{pdf_filename}")
        except Exception:
            app.logger.exception("No se pudo generar el PDF de la factura.")

        return jsonify(
            {
                "numero_factura": numero_factura,
                "total": float(total),
                "tipo": tipo,
                "pdf_url": pdf_url,
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
