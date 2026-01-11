import os

from dotenv import load_dotenv


def load_environment():
    env = os.getenv("FLASK_ENV")
    if env is None or env == "development":
        load_dotenv()


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


load_environment()


class Config:
    SECRET_KEY = require_env("SECRET_KEY")
    FLASK_ENV = require_env("FLASK_ENV")
    DB_HOST = require_env("DB_HOST")
    DB_USER = require_env("DB_USER")
    DB_PASS = require_env("DB_PASS")
    DB_NAME = require_env("DB_NAME")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
