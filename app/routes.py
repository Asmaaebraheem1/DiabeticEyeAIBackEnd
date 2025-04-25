from flask.cli import with_appcontext
import click

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
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.models import Contact, User
from app import db
from datetime import datetime
import re
from functools import wraps

bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')
admin_ui_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_contact_data(data):
    errors = {}
    
    # Name validation
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors['name'] = 'Name must be at least 2 characters'
    
    # Email validation
    if not data.get('email'):
        errors['email'] = 'Email is required'
    elif not validate_email(data['email']):
        errors['email'] = 'Invalid email format'
    
    # Message validation
    if not data.get('message') or len(data['message'].strip()) < 10:
        errors['message'] = 'Message must be at least 10 characters'
    
    return errors

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
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin/dashboard.html', contacts=contacts)

@admin_bp.route('/contacts', methods=['GET'])
@basic_auth_required
def get_contacts():
    contacts = Contact.query.all()
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
    contact = Contact.query.get_or_404(id)
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': 'Contact deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/contacts/<int:id>', methods=['PUT'])
@basic_auth_required
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    
    validation_errors = validate_contact_data(data)
    if validation_errors:
        return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
    
    try:
        contact.name = data['name'].strip()
        contact.email = data['email'].strip()
        contact.message = data['message'].strip()
        db.session.commit()
        return jsonify({'message': 'Contact updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    
    # Validate input
    validation_errors = validate_contact_data(data)
    if validation_errors:
        return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
    
    # Create and save contact
    contact = Contact(
        name=data['name'].strip(),
        email=data['email'].strip(),
        message=data['message'].strip()
    )
    
    try:
        db.session.add(contact)
        db.session.commit()
        return jsonify({'message': 'Submitted successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save contact'}), 500