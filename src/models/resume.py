from src.models import db
from datetime import datetime
import json

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_content = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(db.Text, nullable=True)
    ats_score = db.Column(db.Integer, nullable=True)
    template_id = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='uploaded')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'filename': self.filename,
            'parsed_data': json.loads(self.parsed_data) if self.parsed_data else None,
            'ats_score': self.ats_score, 'template_id': self.template_id, 'status': self.status,
            'created_at': self.created_at.isoformat(), 'updated_at': self.updated_at.isoformat()
        }

class CoverLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    generated_content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InterviewSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)
    performance_score = db.Column(db.Float, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    industry = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    color_options = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'template_id': self.template_id, 'name': self.name, 'category': self.category,
            'industry': self.industry, 'description': self.description, 'preview_url': self.preview_url,
            'rating': self.rating, 'color_options': json.loads(self.color_options) if self.color_options else []
        }
