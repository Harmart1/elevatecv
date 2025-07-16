import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Import the database instance
from .models import db

def create_app():
    """
    Application Factory Function
    """
    # Find the .env file in the root directory and load it
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    # --- App Initialization and Configuration ---
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
        static_url_path='/'  # Serve static files from the root URL
    )

    # Load configuration from environment variables or use defaults
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-secure-default-secret-key-for-development')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')

    # Ensure necessary directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'database'), exist_ok=True)

    # --- Initialize Extensions ---
    CORS(app)
    db.init_app(app)

    # --- Register Blueprints ---
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.resume import resume_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')


    # --- Database and Initial Data Setup ---
    with app.app_context():
        # Import models here to avoid circular imports
        from .models.user import User

        db.create_all()

        # Create a default admin user if one doesn't exist
        if not User.query.filter_by(username='admin').first():
            print("Creating default admin user...")
            admin_user = User(
                username='admin',
                full_name='Admin',
                email='admin@elevatecv.ai',
                role='admin'
            )
            admin_user.set_password('adminpassword')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created with username 'admin' and password 'adminpassword'")

    # --- Static File Routing ---
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:filename>')
    def serve_html(filename):
        # Serves root HTML files (e.g., login.html, register.html)
        return send_from_directory(app.static_folder, filename)

    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

    return app
