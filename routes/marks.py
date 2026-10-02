from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from routes.auth import admin_required

marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks', methods=['GET'])
@admin_required
def list_marks():
    """Display all student marks records with filters."""
    student_id = request.args.get('student_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    query = Marks.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    marks_list = query.order_by(Marks.id.desc()).all()
    students = Student.query.order_by(Student.name.asc()).all()
    subjects = Subject.query.order_by(Subject.semester.asc(), Subject.subject_name.asc()).all()

    return render_template(
        'marks.html',
        marks_list=marks_list,
        students=students,
        subjects=subjects,
        selected_student=student_id,
        selected_subject=subject_id
    )

@marks_bp.route('/marks/add', methods=['POST'])
@admin_required
def add_marks():
    """Enter marks with validation against subject maximum marks."""
    student_id = request.form.get('student_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    
    try:
        internal = float(request.form.get('internal_marks', 0.0) or 0.0)
        external = float(request.form.get('external_marks', 0.0) or 0.0)
        practical = float(request.form.get('practical_marks', 0.0) or 0.0)
    except ValueError:
        flash('Invalid numeric marks entered.', 'danger')
        return redirect(url_for('marks.list_marks'))

    student = Student.query.get(student_id)
    subject = Subject.query.get(subject_id)

    if not student or not subject:
        flash('Valid Student and Subject must be selected.', 'danger')
        return redirect(url_for('marks.list_marks'))

    # Validation: Entered marks must not exceed subject limits
    if internal > subject.internal_max:
        flash(f'Internal marks ({internal}) exceed maximum allowed ({subject.internal_max}).', 'danger')
        return redirect(url_for('marks.list_marks'))
    if external > subject.external_max:
        flash(f'External marks ({external}) exceed maximum allowed ({subject.external_max}).', 'danger')
        return redirect(url_for('marks.list_marks'))
    if practical > subject.practical_max:
        flash(f'Practical marks ({practical}) exceed maximum allowed ({subject.practical_max}).', 'danger')
        return redirect(url_for('marks.list_marks'))

    # Check if record already exists, update if so, otherwise create
    record = Marks.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if not record:
        record = Marks(student_id=student_id, subject_id=subject_id)
        db.session.add(record)

    record.internal_marks = internal
    record.external_marks = external
    record.practical_marks = practical
    record.calculate_total_and_result(subject)

    db.session.commit()
    flash(f'Marks saved for {student.name} - {subject.subject_name}: Total {record.total_marks}/{subject.total_max} ({record.percentage}%, {record.result})', 'success')
    return redirect(url_for('marks.list_marks'))

@marks_bp.route('/marks/<int:id>/delete', methods=['POST'])
@admin_required
def delete_marks(id):
    """Delete a marks record."""
    record = Marks.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('Marks entry deleted successfully.', 'info')
    return redirect(url_for('marks.list_marks'))
