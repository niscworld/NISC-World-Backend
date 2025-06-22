import os

# RENDER_DB_URL = 'postgresql://srinivascharank_mytasklyprove:YaQZez9J2hZrdqG6Ja7wb9TfLwoCi6EM@dpg-d0or5i6uk2gs73903s60-a/mytasklyprove'
SUPABASE_SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.ndngdtfmycfggranhjxx:nisc-world-database@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'

# postgresql://postgres:nisc-world-database@db.ndngdtfmycfggranhjxx.supabase.co:5432/postgres
# postgresql://postgres.ndngdtfmycfggranhjxx:nisc-world-database@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
# postgresql://postgres.ndngdtfmycfggranhjxx:nisc-world-database@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
# postgresql://postgres.ndngdtfmycfggranhjxx:nisc-world-database@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'niscworld.db')

os.environ.setdefault('DATABASE_URL', SUPABASE_SQLALCHEMY_DATABASE_URI)

if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'

# Make sure instance folder exists
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

class Config:
    SITE_URL = "https://nisc-world-backend.onrender.com"
    SECRET_KEY = os.environ.get('SECRET_KEY', 'niscworld-secret')

    if os.environ.get('FLASK_ENV') == 'development':
        # Use SQLite for development
        print("Local Database Accessing...")
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH
    else:
        # Use the RENDER_DB_URL for production or deployment
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL',
            SUPABASE_SQLALCHEMY_DATABASE_URI
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class GeneralSettings:
    JWTExpireMinutes = 60
    MFA_OTP_EXPIRE_DURATION = 5 # Minutes
    FROM_EMAIL = 'nisc.co.in@gmail.com'
    MAIL_PASS_KEY = 'gtdl lscl nnhi jiwa'

    MAIL_END_NOTE = """
    Note: If you did not request this email or believe it was sent to you by mistake, please disregard it. 
    If you continue to receive such messages in error, please contact our support team.
    """

class ThreadSettings:
    NewSessionDeleteThread = 15



