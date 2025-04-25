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

bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')
admin_ui_bp = Blueprint('admin', __name__, url_prefix='/admin')

@click.command('create-admin')
@with_appcontext
def create_admin():
    """Create an admin user"""
    from getpass import getpass
    username = input("Enter admin username: ")
    password = getpass("Enter admin password: ")
    confirm = getpass("Confirm admin password: ")
    
    if password != confirm:
        print("Passwords don't match!")
        return
    
    # Check if user already exists
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"User {username} already exists!")
        return
        
    admin = User(
        username=username,
        password=password
    )
    
    try:
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user {username} created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")

def basic_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    # TODO: Replace with proper authentication logic
    user = User.query.filter_by(username=username).first()
    return user is not None and user.password == password

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_ui.login'))
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

@admin_bp.route('/contacts', methods=['GET'])
@basic_auth_required
def get_contacts():
    contacts = GetContactsUseCase.execute()
    return jsonify([{
        'id': contact.id,
        'name': contact.name,
        'email': contact.email,
        'message': contact.message,
        'created_at': contact.created_at.isoformat() if contact.created_at else None
    } for contact in contacts])

@admin_bp.route('/contacts/<int:id>', methods=['DELETE'])
@basic_auth_required
def delete_contact(id):
    result = DeleteContactUseCase.execute(id)
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result)

@admin_bp.route('/contacts/<int:id>', methods=['PUT'])
@basic_auth_required
def update_contact(id):
    data = request.get_json()
    result = UpdateContactUseCase.execute(id, data)
    if 'error' in result:
        status_code = 400 if 'Validation failed' in result['error'] else 500
        return jsonify(result), status_code
    return jsonify(result)

@bp.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    result = CreateContactUseCase.execute(data)
    if 'error' in result:
        status_code = 400 if 'Validation failed' in result['error'] else 500
        return jsonify(result), status_code
    return jsonify(result), 201