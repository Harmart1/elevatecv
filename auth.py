import jwt
from flask import Blueprint, request, jsonify, current_app
from src.models.user import User
from src.models import db
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin privileges required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['full_name', 'email', 'password', 'headline', 'industry']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing user data'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'An account with this email already exists'}), 409

    # Generate a unique username from the email prefix
    email_prefix = data['email'].split('@')[0]
    username_candidate = email_prefix
    counter = 1
    while User.query.filter_by(username=username_candidate).first():
        username_candidate = f"{email_prefix}{counter}"
        counter += 1

    user = User(
        full_name=data['full_name'],
        email=data['email'],
        username=username_candidate, # Set the unique username
        headline=data['headline'],
        industry=data['industry']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# ... (login function remains the same) ...