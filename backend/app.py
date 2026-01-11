from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    @app.get("/")
    def health_check():
        return "Sistema de facturacion Invagro activo"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
