import os
from flask import Blueprint, send_from_directory, current_app

static_files_bp = Blueprint('static_files', __name__)

@static_files_bp.route('/')
def index():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'index.html')

@static_files_bp.route('/resume-analyzer')
def resume_analyzer():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'resume-analyzer.html')

@static_files_bp.route('/cover-letter')
def cover_letter():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'cover-letter.html')

@static_files_bp.route('/interview-prep')
def interview_prep():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'interview-prep.html')

@static_files_bp.route('/login')
def login():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'login.html')

@static_files_bp.route('/register')
def register():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'register.html')

@static_files_bp.route('/career-dashboard')
def career_dashboard():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'career-dashboard.html')

@static_files_bp.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static', 'css'), filename)

@static_files_bp.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static', 'js'), filename)
