from app import db

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_title = db.Column(db.String(120))
    work_experience = db.Column(db.Text)

    def __repr__(self):
        return f'<Resume {self.filename}>'
