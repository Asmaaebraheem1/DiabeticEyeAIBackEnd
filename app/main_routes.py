from app.services import CreateContactUseCase
from flask.cli import with_appcontext
from flask import send_file
import os
import click
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from functools import wraps
from app.models import User
from app.services import (
    GetContactsUseCase,
    CreateContactUseCase,
    UpdateContactUseCase,
    DeleteContactUseCase,
    AnalyzeImageUseCase
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

@bp.route('/api/analyze', methods=['POST'])
def analyze():
    from PIL import Image
    from io import BytesIO
    from pdf2image import convert_from_bytes
    import requests
    
    # Check if file was uploaded
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        try:
            if file.content_type == 'application/pdf':
                images = convert_from_bytes(file.read())
                if not images:
                    return jsonify({'error': 'Could not extract images from PDF'}), 400
                image = images[0]
                # Save extracted image to temp file
                import tempfile
                temp_dir = os.path.join(bp.root_path, 'temp_images')
                os.makedirs(temp_dir, exist_ok=True)
                temp_img = tempfile.NamedTemporaryFile(
                    suffix='.jpg',
                    dir=temp_dir,
                    delete=False
                )
                image.save(temp_img.name, 'JPEG')
                temp_img.close()
                
                # Analyze the extracted image
                result = AnalyzeImageUseCase.execute(image)
                if 'error' in result:
                    return jsonify(result), 500
                
                return jsonify({
                    'prediction': result['prediction'],
                    'confidence': result['confidence'],
                    'extracted_image': os.path.basename(temp_img.name)
                })
            else:
                image = Image.open(file.stream)
        except Exception as e:
            return jsonify({'error': f'Invalid file: {str(e)}'}), 400
    
    # Check if URL was provided
    elif 'url' in request.json:
        try:
            response = requests.get(request.json['url'])
            image = Image.open(BytesIO(response.content))
        except Exception as e:
            return jsonify({'error': f'Invalid image URL: {str(e)}'}), 400
    
    else:
        return jsonify({'error': 'No file or URL provided'}), 400
    
    # Analyze the image
    result = AnalyzeImageUseCase.execute(image)
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 200

@bp.route('/temp_images/<path:filename>')
def serve_temp_image(filename):
    """Serve temporary extracted images"""
    temp_dir = os.path.join(bp.root_path, 'temp_images')
    image_path = os.path.join(temp_dir, filename)
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    return send_file(image_path, mimetype='image/jpeg')