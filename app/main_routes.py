from app.services import CreateContactUseCase
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

@bp.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    result = CreateContactUseCase.execute(data)
    if 'error' in result:
        status_code = 400 if 'Validation failed' in result['error'] else 500
        return jsonify(result), status_code
    return jsonify(result), 201