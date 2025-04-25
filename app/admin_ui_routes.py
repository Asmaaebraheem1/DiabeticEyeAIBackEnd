from flask.cli import with_appcontext
import click
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from functools import wraps
from app.models import User
from app.services import (
    GetContactsUseCase,
    CreateContactUseCase,
    UpdateContactUseCase,
    DeleteContactUseCase
)
from functools import wraps
from app.models import User
from app.services import GetContactsUseCase

admin_ui_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

@admin_ui_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if check_auth(username, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        return render_template('admin/login.html', error='Invalid credentials')
    return render_template('admin/login.html')

@admin_ui_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_ui_bp.route('/dashboard')
@admin_required
def dashboard():
    contacts = GetContactsUseCase.execute()
    return render_template('admin/dashboard.html', contacts=contacts)

def check_auth(username, password):
    user = User.query.filter_by(username=username).first()
    return user is not None and user.password == password