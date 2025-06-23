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
    is_active = db.Column(db.Boolean, default=False)
    is_suspended = db.Column(db.Boolean, default=False)
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
    email = db.Column(db.String(120), nullable=True, default=None)
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
    code = db.Column(db.String(64), unique=True, nullable=False, default=generate_string)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    duration = db.Column(db.String(50))
    location = db.Column(db.String(100))
    stipend = db.Column(db.String(50))
    posted_on = db.Column(db.DateTime, default=get_current_time)
    is_visible = db.Column(db.Boolean, default=True)
    can_join = db.Column(db.Boolean, default=True)

    # ✅ HR taken from Profile
    hr_profile_id = db.Column(db.String(64), db.ForeignKey('profiles.user_id'), nullable=True)
    hr = db.relationship('Profile', backref='internships_posted', foreign_keys=[hr_profile_id])

    applicants = db.relationship('InternshipApply', backref='internship', lazy=True)


class InternshipApply(db.Model):
    __tablename__ = 'internship_apply'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    resume_url = db.Column(db.String(300), nullable=True)
    applied_on = db.Column(db.DateTime, default=get_current_time)

    internship_code = db.Column(db.String(64), db.ForeignKey('internships.code'), nullable=False)

class Interns(db.Model):
    __tablename__ = 'interns'  # ✅ Fixed table name syntax

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False, unique=False)
    internship_code = db.Column(db.String(64), db.ForeignKey('internships.code'), nullable=False, unique=False)
    
    completion_status = db.Column(db.String(50), default='ongoing')  # e.g., 'ongoing', 'completed', 'dropped'

    # Relationships
    user = db.relationship('User', backref='internships_joined')
    internship = db.relationship('Internships', backref='interns_enrolled')

    def __repr__(self):
        return f"<Intern user_id={self.user_id} internship_code={self.internship_code} status={self.completion_status}>"


class MFAVerification(db.Model):
    __tablename__ = 'mfa_verification'  # ✅ Standardized table name

    id = db.Column(db.Integer, primary_key=True)
    
    user = db.Column(db.String(150), nullable=False)  # Can store user_id, email, etc.
    key = db.Column(db.String(10), nullable=False)  # OTP or verification code

    verify_for = db.Column(db.String(250), nullable=False)  # LOGIN, InternApply, etc.
    created_at = db.Column(db.DateTime, default=get_current_time)
    expires_at = db.Column(db.DateTime, nullable=False)

    is_verified = db.Column(db.Boolean, default=False)

class UserNameGenerationSequence(db.Model):
    __tablename__ = 'user_name_generation_sequence'

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(1), nullable=False)  # A, E, I, O, U
    year = db.Column(db.Integer, nullable=False)

    current_users = db.Column(db.Integer, nullable=False, default=0)
    next_user_number = db.Column(db.Integer, nullable=False, default=1)

    total_users = db.Column(db.Integer, nullable=False, default=0)  # 👈 Lifetime count

    def generate_username(self):
        """Generates a new username and updates the state."""
        current_year_full = get_current_time().year
        current_year = int(str(current_year_full)[-2:])  # Last two digits

        # Reset if year has changed
        if self.year != current_year:
            self.year = current_year
            self.next_user_number = 1
            self.current_users = 0

        # Format username: NW(Year)(Type)(Padded Number)
        padded_number = str(self.next_user_number).zfill(4)
        username = f"NW{self.year:02d}{self.type}{padded_number}"

        # Update counters
        self.current_users += 1
        self.next_user_number += 1
        self.total_users += 1  # 👈 Increment total

        db.session.commit()

        return username

    def __repr__(self):
        return (
            f"<UserNameGenerationSequence type={self.type} "
            f"year={self.year} current_users={self.current_users} "
            f"next_user_number={self.next_user_number} total_users={self.total_users}>"
        )
