from flask.cli import with_appcontext
import click
from app.models import User
from app import db

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