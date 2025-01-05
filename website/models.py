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
    
    # because we named the id as 'user_id' instead of default 'id'
    def get_id(self):
           return (self.user_id)
    
class JobSeeker(db.Model):
    __tablename__ = 'JOBSEEKERS'

    user_id = db.Column(db.Integer,db.ForeignKey('USERS.user_id', ondelete='CASCADE'),primary_key=True, nullable=False) 
    about = db.Column(db.Text)
    profile_pic = db.Column(db.String(200))  # Path to the uploaded profile picture

    #rel
    job_seeker_scoring_weights = db.relationship('JobSeekerScoringWeights', backref='JobSeeker', cascade="all, delete-orphan", uselist=False)


    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
    
class Recruiter(db.Model):
    __tablename__ = 'RECRUITERS'

    user_id = db.Column(db.Integer, db.ForeignKey('USERS.user_id', ondelete='CASCADE'),primary_key=True, nullable=False)
    
    about_company = db.Column(db.Text)

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
    

class JobSeekerScoringWeights(db.Model):
    __tablename__ = 'JOBSEEKER_SCORINGWEIGHTS'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('JOBSEEKERS.user_id', ondelete='CASCADE'), nullable=False)

    # Job description and file (if needed for context)
    job_description = db.Column(db.Text, nullable=True)
    resume_file_path = db.Column(db.String(255), nullable=True)

    # Skills (JSON format to store dynamically added skills and weights)
    skills = db.Column(db.JSON, nullable=True)

    # Education (specific degrees and fallback degrees with weights)
    specific_degrees = db.Column(db.JSON, nullable=True)
    fallback_degrees = db.Column(db.JSON, nullable=True)

    # Places worked (preferred companies and fallback industry with weights)
    preferred_companies = db.Column(db.JSON, nullable=True)
    fallback_industry = db.Column(db.String(255), nullable=True)
    fallback_industry_weight = db.Column(db.Integer, nullable=True)

    # Years worked (minimum and preferred with weights)
    min_years = db.Column(db.Integer, nullable=True)
    min_years_weight = db.Column(db.Integer, nullable=True)
    preferred_years = db.Column(db.Integer, nullable=True)
    preferred_years_weight = db.Column(db.Integer, nullable=True)

    # Gaps in work history (maximum gap tolerance and negative weight)
    max_gap_tolerance = db.Column(db.Integer, nullable=True)
    gap_negative_weight = db.Column(db.Integer, nullable=True)

    # Number of pages (ranges and weights in JSON format)
    page_ranges = db.Column(db.JSON, nullable=True)

    # Bullet points vs paragraph weights
    bullet_weight = db.Column(db.Integer, nullable=True)
    paragraph_weight = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<JobSeekerScoringWeights id={self.id} jobseeker_id={self.jobseeker_id}>"
