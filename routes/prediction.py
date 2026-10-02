from flask import Blueprint, render_template, request, jsonify, flash
from models.student import Student
from routes.auth import login_required
from ml.predict import predict_student_performance, load_or_train_model

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/prediction', methods=['GET', 'POST'])
@login_required
def predict_page():
    """
    Interactive Machine Learning Early Warning & Performance Prediction tool.
    Enables predicting risk category for any student or custom inputs.
    """
    students = Student.query.order_by(Student.name.asc()).all()
    _, metadata = load_or_train_model()

    prediction_result = None
    selected_student_id = None
    
    # Default form values
    form_data = {
        'attendance': 75.0,
        'internal': 65.0,
        'previous': 68.0,
        'assignment': 72.0,
        'failed_subjects': 0
    }

    if request.method == 'POST':
        selected_student_id = request.form.get('student_id', type=int)
        
        try:
            attendance = float(request.form.get('attendance', 75.0))
            internal = float(request.form.get('internal', 65.0))
            previous = float(request.form.get('previous', 68.0))
            assignment = float(request.form.get('assignment', 72.0))
            failed_subjects = int(request.form.get('failed_subjects', 0))
            
            form_data = {
                'attendance': attendance,
                'internal': internal,
                'previous': previous,
                'assignment': assignment,
                'failed_subjects': failed_subjects
            }

            prediction_result = predict_student_performance(
                attendance=attendance,
                internal=internal,
                previous=previous,
                assignment=assignment,
                failed_subjects=failed_subjects
            )
            
            flash('ML Prediction generated successfully using Decision Tree Classifier.', 'success')

        except Exception as e:
            flash(f'Error generating prediction: {str(e)}', 'danger')

    return render_template(
        'prediction.html',
        students=students,
        metadata=metadata,
        prediction_result=prediction_result,
        form_data=form_data,
        selected_student_id=selected_student_id
    )

@prediction_bp.route('/simulator')
@login_required
def simulator_page():
    """
    Interactive MSBTE What-If Academic Performance & Grade Simulator.
    Simulates:
    - Progressive Assessment (PA): Test 1 (20) + Test 2 (20) avg + Micro-Project (10) = 30 Marks
    - End Semester Exam (ESE): Theory Paper (70 Marks)
    - Total Subject Marks (100 Marks)
    - ML Decision Tree Grade Tier & Early Warning Prediction
    """
    students = Student.query.order_by(Student.name.asc()).all()
    _, metadata = load_or_train_model()
    return render_template('simulator.html', students=students, metadata=metadata)

@prediction_bp.route('/prediction/api', methods=['POST'])
@login_required
def predict_api():
    """REST API endpoint for real-time AJAX ML predictions."""
    try:
        data = request.get_json() or {}
        attendance = float(data.get('attendance', 75.0))
        internal = float(data.get('internal', 65.0))
        previous = float(data.get('previous', 68.0))
        assignment = float(data.get('assignment', 72.0))
        failed_subjects = int(data.get('failed_subjects', 0))

        result = predict_student_performance(
            attendance=attendance,
            internal=internal,
            previous=previous,
            assignment=assignment,
            failed_subjects=failed_subjects
        )
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

