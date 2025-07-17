import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate  # Import Flask-Migrate

# Import the database instance
from .models import db

def create_app():
    """
    Application Factory Function
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    app = Flask(__name__) # Removed static folder config, will be handled by blueprints

    # --- Configuration ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-secure-default-secret-key-for-development')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'database'), exist_ok=True)

    # --- Initialize Extensions ---
    CORS(app)
    db.init_app(app)
    Migrate(app, db)  # Initialize Flask-Migrate

    # --- Register Blueprints ---
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.resume import resume_bp
    from .routes.cover_letter import cover_letter_bp
    from .routes.interview import interview_bp
    from .routes.admin import admin_bp
    from .routes.career import career_bp
    from .routes.templates import templates_bp
    from .routes.static_files import static_files_bp # New blueprint for static files

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    app.register_blueprint(cover_letter_bp, url_prefix='/api/cover-letter')
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(career_bp, url_prefix='/api/career')
    app.register_blueprint(templates_bp, url_prefix='/api/templates')
    app.register_blueprint(static_files_bp) # Register the new blueprint

    # --- Create Admin User (only if tables exist) ---
    with app.app_context():
        from .models.user import User
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        if inspector.has_table("user"):
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
                print("Admin user created.")

    return app
