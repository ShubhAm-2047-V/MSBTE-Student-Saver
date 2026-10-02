from datetime import datetime
from models import db

class CapstoneProject(db.Model):
    """MSBTE 3rd Year Capstone Project Planning (22058) & Execution (22059) Tracker."""
    __tablename__ = 'capstone_projects'

    id = db.Column(db.Integer, primary_key=True)
    group_no = db.Column(db.String(20), unique=True, nullable=False)
    project_title = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(100), default='AI / Web Application')
    semester = db.Column(db.Integer, default=5)
    academic_year = db.Column(db.String(20), default='2025-2026')
    guide_name = db.Column(db.String(100), default='Prof. S. R. Patil')
    status = db.Column(db.String(50), default='In Progress')  # Synopsis Approved, In Progress, Ready for Viva, Completed
    weekly_diary_status = db.Column(db.String(50), default='Up to Date')  # Up to Date, Pending Review, Defaulter
    members = db.Column(db.Text, nullable=True)  # Comma separated student names and enrollments
    synopsis_submitted = db.Column(db.Boolean, default=True)
    report_submitted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CapstoneProject {self.group_no}: {self.project_title}>"
