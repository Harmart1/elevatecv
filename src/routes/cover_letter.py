from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx
# Corrected imports for the app factory pattern
from src.ai_service import ai_service
from src.routes.auth import token_required
from src.models import db
from src.models.resume import CoverLetter

cover_letter_bp = Blueprint('cover_letter', __name__)
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
@cover_letter_bp.route('/upload-job-description', methods=['POST'])
@token_required
def upload_job_description(current_user):
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid or no file selected'}), 400

        filename = secure_filename(file.filename)
        upload_dir = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_dir, f"job_desc_{current_user.id}_{filename}")
        file.save(file_path)

        file_ext = filename.rsplit('.', 1)[1].lower()
        text_content = extract_text_from_file(file_path, file_ext)

        if not text_content:
            os.remove(file_path) # Clean up empty file
            return jsonify({'success': False, 'error': 'Could not extract text from the file.'}), 400

        job_analysis = ai_service.analyze_job_description(text_content)

        return jsonify({
            'success': True, 'message': 'Job description uploaded successfully',
            'filename': filename, 'text_content': text_content,
            'analysis': job_analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500
@cover_letter_bp.route('/generate', methods=['POST'])
@token_required
def generate_cover_letter(current_user):
    try:
        data = request.get_json()
        if not data or not data.get('resume_text') or not data.get('job_description'):
            return jsonify({'success': False, 'error': 'Resume text and job description are required'}), 400
        cover_letter_result = ai_service.generate_cover_letter(
                data['resume_text'], data['job_description'],
                data.get('company_name', ''), data.get('position_title', '')
            )

        # Save the generated cover letter to the database
        new_cl = CoverLetter(
            user_id=current_user.id,
            job_title=data.get('position_title', 'N/A'),
            company_name=data.get('company_name', 'N/A'),
            generated_content=cover_letter_result.get('cover_letter')
        )
        db.session.add(new_cl)
        db.session.commit()

        return jsonify({'success': True, 'cover_letter': cover_letter_result})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Generation failed: {str(e)}'}), 500
@cover_letter_bp.route('/customize', methods=['POST'])
@token_required
def customize_cover_letter(current_user):
    try:
        data = request.get_json()
        if not data or not data.get('cover_letter_text') or not data.get('customization_request'):
            return jsonify({'success': False, 'error': 'Cover letter text and customization request are required'}), 400
        prompt = f"""
    Please customize the following cover letter based on the user's request.
    Original Cover Letter: {data['cover_letter_text']}
    Customization Request: {data['customization_request']}
    Provide only the full text of the customized cover letter as a a response.
    """

        customized_result = ai_service._call_google_ai(prompt, max_tokens=1500)

        if not customized_result:
            customized_result = data['cover_letter_text'] + "\n\n---\n(AI customization failed, returning original text.)"

        return jsonify({'success': True, 'customized_cover_letter': customized_result})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Customization failed: {str(e)}'}), 500
