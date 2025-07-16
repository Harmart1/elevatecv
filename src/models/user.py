from src.models import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Profile information
    headline = db.Column(db.String(150), nullable=True)
    industry = db.Column(db.String(80), nullable=True)

    # System fields
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    status = db.Column(db.String(20), nullable=False, default='active')
    plan = db.Column(db.String(20), nullable=False, default='free')
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade="all, delete-orphan")
    cover_letters = db.relationship('CoverLetter', backref='user', lazy=True, cascade="all, delete-orphan")
    interview_sessions = db.relationship('InterviewSession', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        from src.models.resume import Resume # Local import to avoid circular dependency
        resume_count = db.session.query(db.func.count(Resume.id)).filter_by(user_id=self.id).scalar()

        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'headline': self.headline,
            'industry': self.industry,
            'role': self.role,
            'status': self.status,
            'plan': self.plan,
            'resume_count': resume_count,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.full_name}>'
