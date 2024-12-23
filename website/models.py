from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'USERS'

    user_id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    role = db.Column(db.String(50), nullable=False)

    # Relationships
    job_seeker_profile = db.relationship('JobSeeker', backref='user', cascade="all, delete-orphan", uselist=False)
    recruiter_profile = db.relationship('Recruiter', backref='user', cascade="all, delete-orphan", uselist=False)

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
    
class JobSeeker(db.Model):
    __tablename__ = 'JOBSEEKERS'

    user_id = db.Column(db.Integer,db.ForeignKey('USERS.user_id', ondelete='CASCADE'),primary_key=True, nullable=False) 
    about = db.Column(db.Text)
    profile_pic = db.Column(db.String(200))  # Path to the uploaded profile picture


    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
    
class Recruiter(db.Model):
    __tablename__ = 'RECRUITERS'

    user_id = db.Column(db.Integer, db.ForeignKey('USERS.user_id', ondelete='CASCADE'),primary_key=True, nullable=False)
    
    about_company = db.Column(db.Text)

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"