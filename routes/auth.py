from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.database import Usuario

# Crear blueprint de autenticación
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_raw = (request.form.get('remember') or '').strip().lower()
        remember = remember_raw in {'on', 'true', '1', 'yes'}
        
        # Validar campos
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('login.html')
        
        # Buscar usuario
        usuario = Usuario.query.filter_by(username=username).first()
        
        # Verificar credenciales
        if usuario and usuario.check_password(password):
            if not usuario.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
                return render_template('login.html')
            
            # Login exitoso
            login_user(usuario, remember=remember)
            usuario.actualizar_ultimo_acceso()
            
            flash(f'¡Bienvenido {usuario.nombre_completo or usuario.username}!', 'success')
            
            # Redirigir a la página solicitada o al dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('auth.login'))
