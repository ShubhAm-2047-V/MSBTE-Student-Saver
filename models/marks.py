from datetime import datetime
from models import db

class Marks(db.Model):
    """Subject-wise marks record for a student."""
    __tablename__ = 'marks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    
    internal_marks = db.Column(db.Float, nullable=False, default=0.0)
    external_marks = db.Column(db.Float, nullable=False, default=0.0)
    practical_marks = db.Column(db.Float, nullable=False, default=0.0)
    total_marks = db.Column(db.Float, nullable=False, default=0.0)
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    result = db.Column(db.String(10), nullable=False, default='Pass')  # 'Pass' or 'Fail'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint per student and subject
    __table_args__ = (db.UniqueConstraint('student_id', 'subject_id', name='uq_student_subject_marks'),)

    def calculate_total_and_result(self, subject=None):
        """Calculate total marks, percentage, and pass/fail result based on subject passing criteria."""
        subj = subject or self.subject
        self.total_marks = round(self.internal_marks + self.external_marks + self.practical_marks, 2)
        if subj and subj.total_max > 0:
            self.percentage = round((self.total_marks / subj.total_max) * 100.0, 2)
            self.result = 'Pass' if self.total_marks >= subj.passing_marks else 'Fail'
        else:
            self.percentage = 0.0
            self.result = 'Pass'

    def __repr__(self):
        return f"<Marks Student:{self.student_id} Subject:{self.subject_id} Total:{self.total_marks}>"
