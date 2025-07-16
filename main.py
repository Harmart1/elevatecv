import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.append(os.getcwd())

from src.models import db
from src.routes.user import user_bp
from src.routes.resume import resume_bp
from src.routes.cover_letter import cover_letter_bp
from src.routes.interview import interview_bp
from src.routes.templates import templates_bp
from src.routes.admin import admin_bp
from src.routes.career import career_bp
from src.routes.auth import auth_bp
from src.models.user import User  # Import User model for admin creation

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Ensure upload and database directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

# Enable CORS for all routes
CORS(app)

# Initialize database
db.init_app(app)

# Create an admin user on first run
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        print("Creating admin user...")
        admin_user = User(
            username='admin',
            email='admin@elevatecv.ai',
            full_name='Admin User',
            role='admin'
        )
        admin_user.set_password('adminpassword')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created with username 'admin' and password 'adminpassword'")

# Register all blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(resume_bp, url_prefix='/api')
app.register_blueprint(cover_letter_bp, url_prefix='/api')
app.register_blueprint(interview_bp, url_prefix='/api')
app.register_blueprint(templates_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(career_bp, url_prefix='/api')

# Serve static HTML/CSS/JS files
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    # Check if it's a root file like login.html or an asset in a subdirectory
    if os.path.exists(os.path.join(app.static_folder, filename)):
        return send_from_directory(app.static_folder, filename)
    # Fallback for simple paths (e.g., /login)
    html_filename = f"{filename}.html"
    if os.path.exists(os.path.join(app.static_folder, html_filename)):
        return send_from_directory(app.static_folder, html_filename)
    return "File not found", 404


@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)