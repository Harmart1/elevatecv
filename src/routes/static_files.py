import os
from flask import Blueprint, send_from_directory, current_app

static_files_bp = Blueprint('static_files', __name__)

@static_files_bp.route('/')
def index():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), 'index.html')

@static_files_bp.route('/<path:filename>')
def serve_html(filename):
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), filename)

@static_files_bp.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static', 'css'), filename)

@static_files_bp.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static', 'js'), filename)
