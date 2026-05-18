"""
auth_helpers.py · Sistema Invagro

Decoradores y utilidades de autenticación / autorización por rol.

Cómo se usa:

    from auth_helpers import login_required, admin_required, role_required, current_user

    @app.get("/productos")
    @login_required
    def productos():
        ...

    @app.get("/usuarios")
    @admin_required
    def lista_usuarios():
        ...

    @app.get("/reportes")
    @role_required("admin", "contador")
    def reportes():
        ...

    # Dentro de la vista:
    user = current_user()              # objeto User o None
    es_admin = current_user_is_admin()
    uid = current_user_id()            # int o None
"""

from functools import wraps
from flask import session, redirect, url_for, abort

from models import User


# --------------- Helpers públicos para usar en vistas ---------------

def current_user():
    """Devuelve el objeto User actualmente logueado, o None."""
    username = session.get("user")
    if not username:
        return None
    return User.query.filter_by(username=username).first()


def current_user_id():
    """ID del usuario logueado, o None si no hay sesión."""
    # Optimización: si lo guardamos en sesión al login, evita un query.
    uid = session.get("user_id")
    if uid is not None:
        return uid
    user = current_user()
    return user.id if user else None


def current_user_role():
    """Rol del usuario logueado ('admin', 'vendedor', 'contador') o None."""
    role = session.get("rol")
    if role:
        return role
    user = current_user()
    return user.rol if user else None


def current_user_is_admin():
    return current_user_role() == "admin"


def current_user_is_vendedor():
    return current_user_role() == "vendedor"


# --------------- Decoradores ---------------

def login_required(view_func):
    """Redirige a /login si no hay sesión activa."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """
    Permite el acceso solo si el rol del usuario está dentro de allowed_roles.
    Si no hay sesión, redirige al login.
    Si está logueado pero sin permiso, devuelve 403.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not session.get("user"):
                return redirect(url_for("login"))
            role = current_user_role()
            if role not in allowed_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Atajo: solo admins pueden acceder."""
    return role_required("admin")(view_func)
