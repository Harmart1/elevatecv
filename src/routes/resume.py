from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx

from src.ai_service import ai_service
from src.routes.auth import token_required
from src.models import db
from src.models.resume import Resume

resume_bp = Blueprint('resume', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path, extension):
    text = ""
    try:
        if extension == 'pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ''
        elif extension == 'docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + '\n'
        elif extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
    return text

@resume_bp.route('/upload', methods=['POST'])
@token_required
def upload_resume(current_user):
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()

        # Create a unique filename to avoid conflicts
        unique_filename = f"user_{current_user.id}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        text_content = extract_text_from_file(file_path, file_ext)

        if not text_content:
            os.remove(file_path) # Clean up
            return jsonify({'success': False, 'error': 'Could not extract text from file'}), 400

        # Save to database
        new_resume = Resume(
            user_id=current_user.id,
            filename=filename,
            original_content=text_content
        )
        db.session.add(new_resume)
        db.session.commit()

        return jsonify({'success': True, 'message': 'File uploaded and text extracted.', 'text_content': text_content})
    return jsonify({'success': False, 'error': 'File type not allowed'}), 400

@resume_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_resume_text(current_user):
    data = request.get_json()
    if not data or not data.get('resume_text'):
        return jsonify({'success': False, 'error': 'Resume text is required'}), 400

    resume_text = data.get('resume_text')
    job_description = data.get('job_description', '')

    analysis_result = ai_service.analyze_resume(resume_text, job_description)

    # Optional: Update the latest resume record for this user with the score
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    if latest_resume:
        latest_resume.ats_score = analysis_result.get('ats_score')
        latest_resume.status = 'analyzed'
        db.session.commit()

    return jsonify({'success': True, 'analysis': analysis_result})
