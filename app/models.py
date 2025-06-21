# app/models.py

from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import get_current_time, generate_string
from datetime import timedelta


# ✅ User authentication model
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(64), primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)
    login_time = db.Column(db.DateTime, default=get_current_time)

    # 🔐 Set and check password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ✅ Profile details separated from auth
class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False, unique=True)
    fullname = db.Column(db.String(120))
    email = db.Column(db.String(120), nullable=True)
    position = db.Column(db.String(120))

    user = db.relationship('User', backref=db.backref('profile', uselist=False))


# ✅ Session model for tracking tokens and device data
class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False)

    jwt_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_current_time)
    expires_at = db.Column(db.DateTime)  # Can be null if tokens are self-contained

    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.String(256))

    user = db.relationship('User', backref='sessions')

    def __repr__(self):
        return f"<Session user_id={self.user_id} ip_address={self.ip_address}>"

class Internships(db.Model):
    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, default=generate_string)  # ✅ Must be unique & not nullable
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    duration = db.Column(db.String(50))
    location = db.Column(db.String(100))
    stipend = db.Column(db.String(50))
    posted_on = db.Column(db.DateTime, default=get_current_time)
    is_visible = db.Column(db.Boolean, default=True)

    applicants = db.relationship('InternshipApply', backref='internship', lazy=True)

class InternshipApply(db.Model):
    __tablename__ = 'internship_apply'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    resume_url = db.Column(db.String(300), nullable=True)
    applied_on = db.Column(db.DateTime, default=get_current_time)

    internship_code = db.Column(db.String(64), db.ForeignKey('internships.code'), nullable=False)
