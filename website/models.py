from . import db
from flask_login import UserMixin
from datetime import datetime
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
    job_seeker_results = db.relationship('JobSeekerResult', backref='JobSeeker', cascade="all, delete-orphan", uselist=False)
    jobseeker_app = db.relationship("JobApplication", backref="JobSeeker", cascade="all, delete-orphan", uselist=False)


    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
    
class Recruiter(db.Model):
    __tablename__ = 'RECRUITERS'

    user_id = db.Column(db.Integer, db.ForeignKey('USERS.user_id', ondelete='CASCADE'),primary_key=True, nullable=False)
    
    about_company = db.Column(db.Text)

    # Relationships
    job = db.relationship('Job', backref='Recruiter', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
    

class JobSeekerScoringWeights(db.Model):
    __tablename__ = 'JOBSEEKER_SCORINGWEIGHTS'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('JOBSEEKERS.user_id', ondelete='CASCADE'), nullable=False)

    # Job description and file
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


# Post the job
class Job(db.Model):
    __tablename__ = 'JOBS'

    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    deadline = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('RECRUITERS.user_id',  ondelete='CASCADE'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    job_weights = db.relationship('RecruiterJobScoringWeights', backref='Job', cascade="all, delete-orphan")
    job_application = db.relationship("JobApplication", backref="Job", cascade="all, delete-orphan")
    job_post_results = db.relationship("JobPostResult", backref="Job", cascade="all, delete-orphan")

class RecruiterJobScoringWeights(db.Model):
    __tablename__ = 'RECRUITER_JOB_SCORINGWEIGHTS'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('JOBS.job_id', ondelete='CASCADE'), nullable=False)

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
        return f"<RecruiterJobScoringWeights id={self.id} job_id={self.job_id}>"
    

class JobSeekerResult(db.Model):
    result_id = db.Column(db.Integer, primary_key=True)
    jobseeker_id = db.Column(db.Integer, db.ForeignKey('JOBSEEKERS.user_id', ondelete='CASCADE'), nullable=False)
    scores = db.Column(db.JSON, nullable=True)
    recommendations = db.Column(db.JSON, nullable=True)
    resume_file_path = db.Column(db.String(255), nullable=True)


class JobApplication(db.Model):
    __tablename__ = 'JOB_APPLICATIONS'

    application_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('JOBS.job_id', ondelete='CASCADE'), nullable=False)
    jobseeker_id = db.Column(db.Integer, db.ForeignKey('JOBSEEKERS.user_id', ondelete='CASCADE'), nullable=False)
    resume_file_path = db.Column(db.String(500), nullable=False)

    
class JobPostResult(db.Model):
    result_id = db.Column(db.Integer, primary_key=True)
    jobseeker_id = db.Column(db.Integer, db.ForeignKey('JOBSEEKERS.user_id', ondelete='CASCADE'), nullable=False)
    job_id =  db.Column(db.Integer, db.ForeignKey('JOBS.job_id', ondelete='CASCADE'), nullable=False)
    scores = db.Column(db.JSON, nullable=True)
    total_score = db.Column(db.Integer, nullable=False)
    recommendations = db.Column(db.JSON, nullable=True)
    resume_file_path = db.Column(db.String(255), nullable=True)

