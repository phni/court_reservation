from flask import Flask
from routes import app_blueprint
from database import init_db

app = Flask(__name__)
app.register_blueprint(app_blueprint)

# Initialize database
init_db(app)  # Pass the app instance to init_db

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)