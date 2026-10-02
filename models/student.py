from datetime import datetime
from models import db

class Student(db.Model):
    """Student profile model storing diploma student details and academic context."""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_no = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(80), nullable=False, default='Computer Engineering')
    semester = db.Column(db.Integer, nullable=False, default=5)
    academic_year = db.Column(db.String(20), nullable=False, default='2025-2026')
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    admission_year = db.Column(db.Integer, nullable=False, default=2023)
    
    # Baseline indicators for ML & analytics
    previous_percentage = db.Column(db.Float, default=70.0)
    assignment_percentage = db.Column(db.Float, default=75.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    marks = db.relationship('Marks', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    attendances = db.relationship('Attendance', backref='student', cascade='all, delete-orphan', lazy='dynamic')

    def calculate_overall_percentage(self):
        """Calculate aggregate percentage across all entered subjects."""
        student_marks = self.marks.all()
        if not student_marks:
            return round(self.previous_percentage or 0.0, 2)
        total_obtained = sum(m.total_marks for m in student_marks)
        total_possible = sum(m.subject.total_max for m in student_marks if m.subject)
        if total_possible == 0:
            return 0.0
        return round((total_obtained / total_possible) * 100.0, 2)

    def calculate_internal_percentage(self):
        """Calculate aggregate internal marks percentage."""
        student_marks = self.marks.all()
        if not student_marks:
            return 70.0
        total_internal = sum(m.internal_marks for m in student_marks)
        max_internal = sum(m.subject.internal_max for m in student_marks if m.subject)
        if max_internal == 0:
            return 0.0
        return round((total_internal / max_internal) * 100.0, 2)

    def calculate_overall_attendance(self):
        """Calculate overall attendance percentage across all subjects."""
        records = self.attendances.all()
        if not records:
            return 80.0
        total_conducted = sum(a.total_classes for a in records)
        total_attended = sum(a.attended_classes for a in records)
        if total_conducted == 0:
            return 0.0
        return round((total_attended / total_conducted) * 100.0, 2)

    def get_passed_subjects_count(self):
        """Count subjects where student scored passing marks."""
        return sum(1 for m in self.marks.all() if m.result == 'Pass')

    def get_failed_subjects_count(self):
        """Count subjects where student failed to meet passing criteria."""
        return sum(1 for m in self.marks.all() if m.result == 'Fail')

    def get_performance_category(self):
        """
        Project-defined performance classification (Demo criteria):
        90-100: Excellent
        75-89: Good
        60-74: Average
        40-59: Needs Improvement
        Below 40: At Risk
        """
        pct = self.calculate_overall_percentage()
        if pct >= 90.0:
            return 'Excellent'
        elif pct >= 75.0:
            return 'Good'
        elif pct >= 60.0:
            return 'Average'
        elif pct >= 40.0:
            return 'Needs Improvement'
        else:
            return 'At Risk'

    def get_attendance_status(self):
        """
        Project-defined attendance status (Demo criteria):
        >= 75%: Good
        60% - 74%: Needs Attention
        < 60%: Low Attendance
        """
        att = self.calculate_overall_attendance()
        if att >= 75.0:
            return 'Good'
        elif att >= 60.0:
            return 'Needs Attention'
    def get_atkt_status(self):
        """
        MSBTE ATKT (Allowed To Keep Term) Eligibility Evaluation:
        - 0 Backlogs: Eligible (Clear Pass)
        - 1-3 Backlogs: Eligible with ATKT (Allowed to appear / keep term)
        - > 3 Backlogs: Not Promoted / Year Down
        """
        fails = self.get_failed_subjects_count()
        if fails == 0:
            return {'status': 'Clear Pass', 'badge_class': 'success', 'eligible': True, 'msg': 'Eligible for Final Diploma Award without pending backlogs.'}
        elif fails <= 3:
            return {'status': f'ATKT ({fails} Backlog{"s" if fails > 1 else ""})', 'badge_class': 'warning', 'eligible': True, 'msg': f'Eligible for Term Progression under MSBTE ATKT rule (<= 3 heads).'}
        else:
            return {'status': f'Year Down ({fails} Backlogs)', 'badge_class': 'danger', 'eligible': False, 'msg': 'Not eligible for term progression due to > 3 uncleared heads of passing.'}

    def get_msbte_class(self):
        """
        MSBTE Diploma Award Class Classification:
        >= 75%: First Class with Distinction
        >= 60%: First Class
        >= 50%: Second Class
        >= 40%: Pass Class
        < 40%: Fail / Uncleared
        """
        if self.get_failed_subjects_count() > 0:
            return 'Pending Backlogs'
        pct = self.calculate_overall_percentage()
        if pct >= 75.0:
            return 'First Class with Distinction'
        elif pct >= 60.0:
            return 'First Class'
        elif pct >= 50.0:
            return 'Second Class'
        elif pct >= 40.0:
            return 'Pass Class'
        else:
            return 'Fail'

    def __repr__(self):
        return f"<Student {self.enrollment_no} - {self.name}>"
