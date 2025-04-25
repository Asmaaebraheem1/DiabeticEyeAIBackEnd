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

admin_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')

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
    user = User.query.filter_by(username=username).first()
    return user is not None and user.password == password

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