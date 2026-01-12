import logging

from flask import Flask, jsonify, redirect, render_template, request, session, url_for


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

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
            email = request.form.get("email", "").strip()
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            user_value = email or username

            if user_value and password:
                session["user"] = user_value
                return redirect(url_for("dashboard"))

            return render_template(
                "login.html",
                error="Ingresa usuario y contrasena para continuar.",
            )

        return render_template("login.html")

    @app.get("/dashboard")
    def dashboard():
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template("dashboard.html", user=session["user"])

    @app.get("/clientes")
    def clientes():
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template("clientes.html", user=session["user"])

    @app.get("/facturacion")
    def facturacion():
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template("facturacion.html", user=session["user"])

    @app.get("/productos")
    def productos():
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template("productos.html", user=session["user"])

    @app.get("/reportes")
    def reportes():
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template("reportes.html", user=session["user"])

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    app = create_app()
    if app.config.get("FLASK_ENV") == "development":
        app.run()
