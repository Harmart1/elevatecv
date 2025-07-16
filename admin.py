from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func
from src.models import db
from src.models.user import User
from src.models.resume import Resume, CoverLetter, InterviewSession, Template
from .auth import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard', methods=['GET'])
@admin_required
def get_dashboard_metrics(current_user):
    """Get main dashboard metrics from the database."""
    try:
        total_users = db.session.query(func.count(User.id)).scalar()
        total_resumes = db.session.query(func.count(Resume.id)).scalar()
        total_cover_letters = db.session.query(func.count(CoverLetter.id)).scalar()
        
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        users_last_month = db.session.query(func.count(User.id)).filter(User.created_at >= one_month_ago).scalar()
        resumes_last_month = db.session.query(func.count(Resume.id)).filter(Resume.created_at >= one_month_ago).scalar()

        # Mock some data that would require a more complex analytics setup
        api_calls_today = db.session.query(func.count(User.id)).filter(User.last_login >= (datetime.utcnow() - timedelta(days=1))).scalar() * 5 + 1000

        metrics = {
            "total_users": total_users,
            "user_growth_percentage": round((users_last_month / total_users * 100) if total_users else 0, 1),
            "total_resumes": total_resumes,
            "resume_growth_percentage": round((resumes_last_month / total_resumes * 100) if total_resumes else 0, 1),
            "api_calls_today": api_calls_today,
            "api_growth_percentage": 5.0, # Mocked
            "server_uptime": 99.9, # Mocked
            "total_cover_letters": total_cover_letters,
            "total_interviews": db.session.query(func.count(InterviewSession.id)).scalar()
        }
        
        return jsonify({"success": True, "metrics": metrics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users(current_user):
    """Get users with pagination, searching, and filtering."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        
        query = User.query
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(User.username.ilike(search_term) | User.email.ilike(search_term))
        
        if status_filter:
            query = query.filter(User.status == status_filter)
            
        users_paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "success": True,
            "users": [user.to_dict() for user in users_paginated.items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": users_paginated.total,
                "pages": users_paginated.pages,
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/users/<int:user_id>/suspend', methods=['POST'])
@admin_required
def suspend_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            return jsonify({"success": False, "message": "Cannot suspend an admin account"}), 403
            
        user.status = 'suspended'
        db.session.commit()
        return jsonify({"success": True, "message": f"User {user.username} has been suspended."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        user.status = 'active'
        db.session.commit()
        return jsonify({"success": True, "message": f"User {user.username} has been activated."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/admin/settings', methods=['PUT'])
@admin_required
def update_admin_settings(current_user):
    """Updates system-wide settings."""
    try:
        data = request.json
        # In a real app, you would persist these settings in a database or config file.
        # For this example, we just echo them back.
        print(f"Admin {current_user.username} updated settings: {data}")
        return jsonify({
            "success": True,
            "message": "Settings updated successfully",
            "updated_settings": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500