import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_database_uri():
    db_env = os.environ.get('DATABASE_URL')
    if db_env:
        return db_env
    
    local_db = os.path.join(BASE_DIR, 'database.db')
    if os.environ.get('VERCEL'):
        tmp_db = '/tmp/database.db'
        if not os.path.exists(tmp_db) and os.path.exists(local_db):
            try:
                shutil.copy2(local_db, tmp_db)
            except Exception:
                pass
        return f"sqlite:///{tmp_db}"
    return f"sqlite:///{local_db}"

class Config:
    """Application configuration for MSBTE Student Saver."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'msbte_student_saver_secret_key_2026')
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paths
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    EXPORTS_DIR = '/tmp/exports' if os.environ.get('VERCEL') else os.path.join(BASE_DIR, 'exports')
    ML_DIR = os.path.join(BASE_DIR, 'ml')
    
    # Session security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
