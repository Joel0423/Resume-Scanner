from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

views =  Blueprint('views', __name__)

def redirect_home():
    if current_user.role == "recruiter":
        return redirect(url_for('views.recruiter_home'))
    elif current_user.role == "job-seeker":
        return redirect(url_for('views.job_seeker_home'))

@views.route("/")
def landing():
    return render_template("landing.html")

@views.route("/job-seekers")
@login_required
def job_seeker_home():
    if current_user.role == 'recruiter':
        return redirect(url_for('views.recruiter_home'))
    return render_template("job_seek_home.html")

@views.route("/recruiters")
@login_required
def recruiter_home():
    if current_user.role == 'job-seeker':
        return redirect(url_for('views.job_seeker_home'))
    return render_template("recruiter_home.html")