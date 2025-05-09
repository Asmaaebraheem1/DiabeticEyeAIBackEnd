import os
from app import create_app, db

app = create_app()

with app.app_context():
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Create all database tables
    db.create_all()
    print("Database tables created successfully")