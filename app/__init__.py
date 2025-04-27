# Flask application factory
from flask import Flask
from app.extensions import db, cors, migrate
from app.services import ImageAnalysisService

def create_app():
    app = Flask(__name__)
    
    # Explicitly import and use Config
    from config import Config
    app.config.from_object(Config)
    
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

    # Ensure instance folder exists
    import os
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    # Create tables if not exists
    with app.app_context():
        db.create_all()
        
        # Initialize ML model
        ImageAnalysisService.initialize_model()
        
        # Import models after db initialization to avoid circular imports
        from app import models

    # Register blueprints
    from app.main_routes import bp as main_bp
    from app.admin_routes import admin_bp
    from app.admin_ui_routes import admin_ui_bp
    from app.cli import create_admin
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_ui_bp)
    app.cli.add_command(create_admin)

    # Set secret key for sessions
    app.secret_key = 'your-secret-key-here'  # TODO: Replace with proper secret key

    return app