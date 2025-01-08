from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from .models import JobSeekerScoringWeights
from . import db
from .jobseeker_scoring import calculate_resume_score

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

@views.route("/jobseek-upload", methods=['GET', 'POST'])
@login_required
def jobseek_upload():
    if request.method == 'POST':
        # Ensure the user is a job-seeker
        if current_user.role != 'job-seeker':
            flash("Access denied.", "error")
            return redirect(url_for('views.recruiter_home'))

        # Get the form data
        job_description = request.form.get('job_description')
        skills = request.form.getlist('skills-section[]')  # Assuming dynamic skills are sent as a list
        skill_weights = request.form.getlist('skills-section_weight[]')
        skills_data = {skills[i]: int(skill_weights[i]) for i in range(len(skills))}

        specific_degrees = request.form.getlist('education_specific[]')
        specific_degree_weights = request.form.getlist('education_specific_weight[]')
        specific_degrees_data = {specific_degrees[i]: int(specific_degree_weights[i]) for i in range(len(specific_degrees))}

        fallback_degrees = request.form.getlist('fallback_degree[]')
        fallback_degree_weights = request.form.getlist('fallback_weight[]')
        fallback_degrees_data = {fallback_degrees[i]: int(fallback_degree_weights[i]) for i in range(len(fallback_degrees))}

        preferred_companies = request.form.getlist('places-section[]')
        company_weights = request.form.getlist('places-section_weight[]')
        preferred_companies_data = {preferred_companies[i]: int(company_weights[i]) for i in range(len(preferred_companies))}

        fallback_industry = request.form.get('industry')
        fallback_industry_weight = request.form.get('industry_weight', type=int)

        min_years = request.form.get('min_years', type=int)
        min_years_weight = request.form.get('min_years_weight', type=int)
        preferred_years = request.form.get('preferred_years', type=int)
        preferred_years_weight = request.form.get('preferred_years_weight', type=int)

        max_gap_tolerance = request.form.get('max_gap', type=int)
        gap_negative_weight = request.form.get('gap_weight', type=int)

        page_ranges = request.form.getlist('pages-section[]')
        page_range_weights = request.form.getlist('pages-section_weight[]')
        page_ranges_data = {page_ranges[i]: int(page_range_weights[i]) for i in range(len(page_ranges))}

        bullet_weight = request.form.get('bullet_weight', type=int)
        paragraph_weight = request.form.get('paragraph_weight', type=int)

        # Handle the uploaded resume file
        resume_file = request.files.get('resume_file')
        resume_file_path = None
        if resume_file:
            # Define the folder outside the current directory
            upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploaded_resumes')
            os.makedirs(upload_folder, exist_ok=True)

            # Secure the filename and save the file
            filename = secure_filename(resume_file.filename)
            resume_file_path = os.path.join(upload_folder, filename)
            resume_file.save(resume_file_path)

        # Create the JobSeekerScoringWeights object
        scoring_weights = JobSeekerScoringWeights(
            user_id=current_user.user_id,
            job_description=job_description,
            resume_file_path=resume_file_path,
            skills=skills_data,
            specific_degrees=specific_degrees_data,
            fallback_degrees=fallback_degrees_data,
            preferred_companies=preferred_companies_data,
            fallback_industry=fallback_industry,
            fallback_industry_weight=fallback_industry_weight,
            min_years=min_years,
            min_years_weight=min_years_weight,
            preferred_years=preferred_years,
            preferred_years_weight=preferred_years_weight,
            max_gap_tolerance=max_gap_tolerance,
            gap_negative_weight=gap_negative_weight,
            page_ranges=page_ranges_data,
            bullet_weight=bullet_weight,
            paragraph_weight=paragraph_weight
        )

        # Save to the database
        try:
            test = scoring_weights
            db.session.add(scoring_weights)
            db.session.commit()
            flash("Scoring weights and resume uploaded successfully.", "success")
            
            calculate_resume_score(resume_file_path, job_description, scoring_weights)

            return redirect(url_for('views.jobseek_result'))
        
            
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('views.jobseek_upload'))

    # GET request - render the upload form
    if request.method == 'GET':
        if current_user.role == 'job-seeker':
            return render_template("job_seek_upload.html")
        return render_template("recruiter_home.html")


@views.route("/jobseek-result", methods=['GET', 'POST'])
@login_required
def jobseek_result():
    return render_template("job_seek_result.html")