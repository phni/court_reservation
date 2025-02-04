from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """
    Initialize the database with the given Flask application.
    This function creates all necessary database tables if they don't exist.
    """
    from models import Reservation  # Import the model from models.py
    
    app.config.from_object('config.Config')  # Load configuration from config.py
    db.init_app(app)
    
    with app.app_context():
        db.create_all()  # Create all database tables