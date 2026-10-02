from datetime import datetime
from models import db

class Subject(db.Model):
    """
    Configurable Subject model representing academic course structure.
    Labeled: 'Demo MSBTE Academic Structure'
    """
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    subject_name = db.Column(db.String(120), nullable=False)
    branch = db.Column(db.String(80), nullable=False, default='Computer Engineering')
    semester = db.Column(db.Integer, nullable=False, default=5)
    subject_type = db.Column(db.String(30), nullable=False, default='Theory')  # Theory, Practical, Project, Lab
    
    # Marks distribution limits
    internal_max = db.Column(db.Float, nullable=False, default=30.0)
    external_max = db.Column(db.Float, nullable=False, default=70.0)
    practical_max = db.Column(db.Float, nullable=False, default=0.0)
    total_max = db.Column(db.Float, nullable=False, default=100.0)
    passing_marks = db.Column(db.Float, nullable=False, default=40.0)
    credits = db.Column(db.Integer, nullable=False, default=4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    marks = db.relationship('Marks', backref='subject', cascade='all, delete-orphan', lazy='dynamic')
    attendances = db.relationship('Attendance', backref='subject', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<Subject {self.subject_code} - {self.subject_name} (Sem {self.semester})>"
