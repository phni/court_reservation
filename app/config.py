class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///reservations.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False