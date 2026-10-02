from datetime import datetime
from models import db

class Attendance(db.Model):
    """Subject-wise attendance record for a student."""
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    
    total_classes = db.Column(db.Integer, nullable=False, default=50)
    attended_classes = db.Column(db.Integer, nullable=False, default=40)
    attendance_percentage = db.Column(db.Float, nullable=False, default=80.0)
    status = db.Column(db.String(30), nullable=False, default='Good')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint per student and subject
    __table_args__ = (db.UniqueConstraint('student_id', 'subject_id', name='uq_student_subject_attendance'),)

    def calculate_percentage_and_status(self):
        """Calculate attendance percentage and status based on demo criteria."""
        if self.total_classes > 0:
            self.attendance_percentage = round((self.attended_classes / self.total_classes) * 100.0, 2)
        else:
            self.attendance_percentage = 0.0

        if self.attendance_percentage >= 75.0:
            self.status = 'Good'
        elif self.attendance_percentage >= 60.0:
            self.status = 'Needs Attention'
        else:
            self.status = 'Low Attendance'

    def __repr__(self):
        return f"<Attendance Student:{self.student_id} Subject:{self.subject_id} Pct:{self.attendance_percentage}%>"
