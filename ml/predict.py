import os
import json
import joblib
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ML_DIR = os.path.join(BASE_DIR, 'ml')
MODEL_PATH = os.path.join(ML_DIR, 'model.pkl')
META_PATH = os.path.join(ML_DIR, 'model_metadata.json')

def load_or_train_model():
    """Load existing model or train a new one if not present."""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
        from ml.train_model import train_and_save_model
        train_and_save_model()
        
    model = joblib.load(MODEL_PATH)
    with open(META_PATH, 'r') as f:
        metadata = json.load(f)
    return model, metadata

def predict_student_performance(attendance, internal, previous, assignment, failed_subjects):
    """
    Predict performance category using the trained Decision Tree Classifier.
    
    Returns a dictionary with:
    - predicted_category
    - probabilities / confidence
    - risk_level ('Low', 'Moderate', 'High', 'Critical')
    - recommendations
    - disclaimer
    """
    model, metadata = load_or_train_model()
    
    # Prepare input DataFrame matching training feature columns
    input_df = pd.DataFrame([{
        'attendance_percentage': float(attendance),
        'internal_percentage': float(internal),
        'previous_percentage': float(previous),
        'assignment_percentage': float(assignment),
        'failed_subjects': int(failed_subjects)
    }])
    
    # Prediction
    prediction = model.predict(input_df)[0]
    probabilities = model.predict_proba(input_df)[0]
    
    prob_dict = {
        cls_name: round(float(prob) * 100, 1)
        for cls_name, prob in zip(model.classes_, probabilities)
    }
    
    # Determine risk level & actionable recommendations
    risk_mapping = {
        'Good': {
            'risk_level': 'Low Risk',
            'badge_class': 'success',
            'summary': 'Student is consistently performing well across coursework and attendance.',
            'recommendations': [
                'Encourage participation in technical seminars and project competitions.',
                'Maintain consistent attendance in practical lab sessions.',
                'Provide advanced practice questions for semester end exams.'
            ]
        },
        'Average': {
            'risk_level': 'Moderate',
            'badge_class': 'info',
            'summary': 'Student meets basic passing standards but has room for significant score improvement.',
            'recommendations': [
                'Focus on unit test revision and weak subject topics.',
                'Ensure attendance stays consistently above 75%.',
                'Schedule periodic mentoring check-ins before final submission.'
            ]
        },
        'Needs Improvement': {
            'risk_level': 'High Attention Needed',
            'badge_class': 'warning',
            'summary': 'Student exhibits lagging internal test marks or borderline attendance.',
            'recommendations': [
                'Conduct remedial / extra coaching classes for core theory subjects.',
                'Issue academic progress alert to class teacher / mentor.',
                'Monitor weekly assignment submission and lab journal completion.'
            ]
        },
        'At Risk': {
            'risk_level': 'Critical / Early Warning',
            'badge_class': 'danger',
            'summary': 'Student has multiple backlogs, low attendance (<60%), or poor internal marks.',
            'recommendations': [
                'Immediate one-on-one counseling with HOD / Academic Coordinator.',
                'Mandatory attendance recovery plan and makeup practical tests.',
                'Notify parents/guardians regarding detention risk and backlog clearance plan.'
            ]
        }
    }
    
    info = risk_mapping.get(prediction, risk_mapping['Average'])
    
    return {
        'predicted_category': prediction,
        'confidence_distribution': prob_dict,
        'risk_level': info['risk_level'],
        'badge_class': info['badge_class'],
        'summary': info['summary'],
        'recommendations': info['recommendations'],
        'inputs': {
            'attendance': float(attendance),
            'internal': float(internal),
            'previous': float(previous),
            'assignment': float(assignment),
            'failed_subjects': int(failed_subjects)
        },
        'disclaimer': 'Prediction is for academic demonstration only. It should not be treated as an official examination prediction or official MSBTE result.'
    }
