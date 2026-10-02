import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ML_DIR = os.path.join(BASE_DIR, 'ml')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def generate_synthetic_dataset(n_samples=350, random_state=42):
    """
    Generate synthetic dataset for MSBTE Diploma student performance classification.
    Uses realistic academic distributions for Diploma Computer Engineering students.
    """
    np.random.seed(random_state)
    
    # 1. Attendance percentage (Normal distribution centered at 78, clipped between 35 and 98)
    attendance = np.clip(np.random.normal(loc=76.0, scale=12.0, size=n_samples), 35.0, 98.0)
    
    # 2. Internal marks percentage (Correlated with attendance)
    internal = np.clip(0.6 * attendance + np.random.normal(loc=25.0, scale=8.0, size=n_samples), 30.0, 95.0)
    
    # 3. Previous semester percentage
    previous = np.clip(np.random.normal(loc=68.0, scale=11.0, size=n_samples), 38.0, 96.0)
    
    # 4. Assignment / Test performance percentage
    assignment = np.clip(0.5 * internal + 0.3 * attendance + np.random.normal(loc=15.0, scale=7.0, size=n_samples), 35.0, 98.0)
    
    # 5. Failed subjects (0 to 4 based on internal & previous performance)
    failed_subjects = []
    for i in range(n_samples):
        avg_score = (internal[i] + previous[i]) / 2.0
        if avg_score < 45 or attendance[i] < 50:
            fails = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
        elif avg_score < 60 or attendance[i] < 65:
            fails = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
        else:
            fails = np.random.choice([0, 1], p=[0.9, 0.1])
        failed_subjects.append(int(fails))
        
    failed_subjects = np.array(failed_subjects)

    # Determine Performance Category target
    # Categories: 'Good', 'Average', 'Needs Improvement', 'At Risk'
    categories = []
    for i in range(n_samples):
        composite_score = (
            0.30 * attendance[i] +
            0.30 * internal[i] +
            0.20 * previous[i] +
            0.20 * assignment[i] -
            (failed_subjects[i] * 6.0)
        )
        
        if composite_score >= 74.0 and failed_subjects[i] == 0:
            categories.append('Good')
        elif composite_score >= 60.0 and failed_subjects[i] <= 1:
            categories.append('Average')
        elif composite_score >= 46.0 and failed_subjects[i] <= 2:
            categories.append('Needs Improvement')
        else:
            categories.append('At Risk')

    df = pd.DataFrame({
        'attendance_percentage': np.round(attendance, 1),
        'internal_percentage': np.round(internal, 1),
        'previous_percentage': np.round(previous, 1),
        'assignment_percentage': np.round(assignment, 1),
        'failed_subjects': failed_subjects,
        'performance_category': categories
    })
    
    return df

def train_and_save_model():
    """
    Train Decision Tree Classifier and save model artifact & evaluation metrics.
    """
    os.makedirs(ML_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate data
    df = generate_synthetic_dataset(n_samples=350, random_state=42)
    
    # Save dataset to CSV
    csv_path = os.path.join(DATA_DIR, 'ml_training_dataset.csv')
    df.to_csv(csv_path, index=False)
    print(f"[ML] Dataset saved to {csv_path} ({len(df)} records)")
    
    # Feature selection
    feature_cols = [
        'attendance_percentage',
        'internal_percentage',
        'previous_percentage',
        'assignment_percentage',
        'failed_subjects'
    ]
    X = df[feature_cols]
    y = df['performance_category']
    
    # Train / Test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # Train Decision Tree Classifier (simple, transparent, highly explainable for viva)
    clf = DecisionTreeClassifier(
        criterion='gini',
        max_depth=4,
        min_samples_split=6,
        min_samples_leaf=3,
        random_state=42
    )
    clf.fit(X_train, X_train_y := y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    conf_matrix = confusion_matrix(y_test, y_pred, labels=clf.classes_).tolist()
    
    print(f"[ML] Model Trained Successfully. Real Test Accuracy: {accuracy * 100:.2f}%")
    
    # Save model artifact
    model_path = os.path.join(ML_DIR, 'model.pkl')
    joblib.dump(clf, model_path)
    print(f"[ML] Model saved to {model_path}")
    
    # Save training metadata and metrics for UI/Viva display
    metadata = {
        'model_type': 'Decision Tree Classifier',
        'criterion': 'gini',
        'max_depth': 4,
        'features': feature_cols,
        'classes': list(clf.classes_),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'accuracy': round(accuracy * 100, 2),
        'feature_importances': {
            col: round(float(imp) * 100, 2)
            for col, imp in zip(feature_cols, clf.feature_importances_)
        },
        'confusion_matrix': conf_matrix,
        'classification_report': report
    }
    
    meta_path = os.path.join(ML_DIR, 'model_metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"[ML] Metadata saved to {meta_path}")
    
    return metadata

if __name__ == '__main__':
    train_and_save_model()
