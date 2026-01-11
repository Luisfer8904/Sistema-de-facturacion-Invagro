import logging

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    if not app.debug and not app.testing:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )

    @app.get("/")
    def health_check():
        return "Sistema de facturacion Invagro activo"

    return app


if __name__ == "__main__":
    app = create_app()
    if app.config.get("FLASK_ENV") == "development":
        app.run()
