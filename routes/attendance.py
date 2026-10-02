from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.student import Student
from models.subject import Subject
from models.attendance import Attendance
from routes.auth import admin_required

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET'])
@admin_required
def list_attendance():
    """Display student attendance records with filters."""
    student_id = request.args.get('student_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    query = Attendance.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    attendance_list = query.order_by(Attendance.id.desc()).all()
    students = Student.query.order_by(Student.name.asc()).all()
    subjects = Subject.query.order_by(Subject.semester.asc(), Subject.subject_name.asc()).all()

    return render_template(
        'attendance.html',
        attendance_list=attendance_list,
        students=students,
        subjects=subjects,
        selected_student=student_id,
        selected_subject=subject_id
    )

@attendance_bp.route('/attendance/add', methods=['POST'])
@admin_required
def add_attendance():
    """Add or update attendance record with validation."""
    student_id = request.form.get('student_id', type=int)
    subject_id = request.form.get('subject_id', type=int)

    try:
        total_classes = int(request.form.get('total_classes', 50) or 50)
        attended_classes = int(request.form.get('attended_classes', 40) or 40)
    except ValueError:
        flash('Total and Attended classes must be valid integers.', 'danger')
        return redirect(url_for('attendance.list_attendance'))

    student = Student.query.get(student_id)
    subject = Subject.query.get(subject_id)

    if not student or not subject:
        flash('Valid Student and Subject must be selected.', 'danger')
        return redirect(url_for('attendance.list_attendance'))

    # Validation
    if total_classes <= 0:
        flash('Total classes conducted must be greater than 0.', 'danger')
        return redirect(url_for('attendance.list_attendance'))

    if attended_classes > total_classes:
        flash(f'Attended classes ({attended_classes}) cannot exceed Total classes ({total_classes}).', 'danger')
        return redirect(url_for('attendance.list_attendance'))

    if attended_classes < 0:
        flash('Attended classes cannot be negative.', 'danger')
        return redirect(url_for('attendance.list_attendance'))

    record = Attendance.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if not record:
        record = Attendance(student_id=student_id, subject_id=subject_id)
        db.session.add(record)

    record.total_classes = total_classes
    record.attended_classes = attended_classes
    record.calculate_percentage_and_status()

    db.session.commit()
    flash(f'Attendance recorded for {student.name} - {subject.subject_name}: {record.attended_classes}/{record.total_classes} ({record.attendance_percentage}%, {record.status})', 'success')
    return redirect(url_for('attendance.list_attendance'))

@attendance_bp.route('/attendance/<int:id>/delete', methods=['POST'])
@admin_required
def delete_attendance(id):
    """Delete an attendance record."""
    record = Attendance.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('Attendance record deleted successfully.', 'info')
    return redirect(url_for('attendance.list_attendance'))
