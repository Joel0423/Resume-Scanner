from flask import Blueprint
from flask import render_template

views =  Blueprint('views', __name__)

@views.route("/")
def landing():
    return render_template("landing.html")

@views.route("/job-seekers")
def job_seeker_home():
    return render_template("job_seek_home.html")

@views.route("/recruiters")
def recruiter_home():
    return render_template("recruiter_home.html")