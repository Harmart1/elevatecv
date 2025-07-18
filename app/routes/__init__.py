from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.resume import Resume
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import PyPDF2
from io import BytesIO

bp = Blueprint('routes', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@bp.route('/upload_resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    user_id = get_jwt_identity()

    # Extract text from PDF
    pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    resume = Resume(filename=file.filename, data=file.read(), user_id=user_id, work_experience=text)
    db.session.add(resume)
    db.session.commit()

    return jsonify({'message': 'Resume uploaded and analyzed successfully'}), 200

@bp.route('/resumes', methods=['GET'])
@jwt_required()
def get_resumes():
    user_id = get_jwt_identity()
    resumes = Resume.query.filter_by(user_id=user_id).all()
    output = []
    for resume in resumes:
        resume_data = {}
        resume_data['id'] = resume.id
        resume_data['filename'] = resume.filename
        resume_data['work_experience'] = resume.work_experience
        output.append(resume_data)
    return jsonify({'resumes': output})
