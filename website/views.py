from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file, abort
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from .models import JobSeekerScoringWeights, Job, RecruiterJobScoringWeights, JobSeekerResult, Recruiter, User, JobApplication, JobPostResult, JobSeeker
from . import db
from .jobseeker_scoring import calculate_resume_results
from datetime import datetime

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
            upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\uploaded_resumes')
            os.makedirs(upload_folder, exist_ok=True)

            # Secure the filename and save the file
            filename = secure_filename(resume_file.filename)
            resume_file_path = os.path.join(upload_folder, filename)
            resume_file.save(resume_file_path)
            #modify to correct path after saving to store in database
            resume_file_path = resume_file_path.replace("\website\..","")
            resume_file_path = resume_file_path.replace("\\","/")
            #resume_file_path = "file:///".join(resume_file_path)

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
            
            #store results in DB
            res = calculate_resume_results(resume_file_path, job_description, scoring_weights)
            jobseeker_results = JobSeekerResult(
                jobseeker_id = current_user.user_id,
                scores = res['section_scores'],
                recommendations = res['recommendations'],
                resume_file_path = resume_file_path
            )
            db.session.add(jobseeker_results)
            db.session.commit()

            return redirect(url_for('views.jobseek_result', result_id=jobseeker_results.result_id, jobseek_id=current_user.user_id))
        
            
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('views.jobseek_upload'))

    # GET request - render the upload form
    if request.method == 'GET':
        if current_user.role == 'job-seeker':
            return render_template("job_seek_upload.html")
        return render_template("recruiter_home.html")


@views.route("/jobseek-result", methods=['GET'])
@login_required
def jobseek_result():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))

    return render_template("job_seek_result.html")

@views.route('/get-j-result', methods=['GET'])
@login_required
def get_jobseek_results():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))
    
    result_id = request.args.get('result_id')
    jobseek_id = request.args.get('jobseek_id')
    download = request.args.get('download', 'false').lower() == 'true'  # Check if 'download' is true

    # Query the database for the result
    result = JobSeekerResult.query.filter_by(result_id=result_id, jobseeker_id=jobseek_id).first()

    if not result:
        flash("No results found for the given parameters.", "danger")
        return redirect(url_for('views.job_seeker_home'))

    # Get the resume file path
    resume_file_path = result.resume_file_path

    # If `download` is True, return the PDF file directly
    if download:
        if not resume_file_path or not os.path.exists(resume_file_path):
            abort(404, description="Resume file not found.")
        return send_file(resume_file_path, as_attachment=False, mimetype='application/pdf')

    # Otherwise, return JSON response
    return jsonify({
        "resume_file_path": resume_file_path,
        "recommendations": result.recommendations,
        "scores": result.scores
    })


#post job 
@views.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'recruiter':
        flash("Access denied.", "error")
        return redirect(url_for('views.job_seeker_home'))

    if request.method == 'POST':
        try:
            # Extract form data
            job_title = request.form.get('job_title')
            company_name = request.form.get('company_name')
            location = request.form.get('location')
            job_type = request.form.get('job_type')
            salary_min = request.form.get('salary_min', type=int)
            salary_max = request.form.get('salary_max', type=int)
            deadline = request.form.get('deadline')
            job_description = request.form.get('job_description')

            # Convert deadline to date object
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")

            # Validate required fields
            if not (job_title and company_name and location and job_type and job_description and deadline):
                flash("All required fields must be filled!", "error")
                return redirect(url_for('views.post_job'))

            # Create Job entry
            new_job = Job(
                title=job_title,
                company=company_name,
                location=location,
                job_type=job_type,
                salary_min=salary_min,
                salary_max=salary_max,
                deadline=deadline_date,
                description=job_description,
                recruiter_id=current_user.user_id
            )
            db.session.add(new_job)
            db.session.commit()  # Commit to generate job_id

            # Get job ID after committing
            job_id = new_job.job_id

            # Get the form data

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

            # Create the JobSeekerScoringWeights object
            scoring_weights = RecruiterJobScoringWeights(
                job_id = job_id,
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

                db.session.add(scoring_weights)
                db.session.commit()
                flash("Job posted successfully!", "success")
                
                #calculate_resume_score(resume_file_path, job_description, scoring_weights)

                return redirect(url_for('views.recruiter_home'))
                  
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for('views.post_job'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error posting job: {str(e)}", "error")
            return redirect(url_for('views.post_job'))

    return render_template('post_a_job.html')


@views.route('/view-my-job', methods=['GET'])
@login_required
def view_recruiter_job():
    if current_user.role != 'recruiter':
        flash("Access denied.", "error")
        return redirect(url_for('views.job_seeker_home'))
    
    return render_template('recruiter_job_posts.html')
    

@views.route('/get-r-jobs', methods=['GET'])
@login_required
def get_r_jobs():
    if current_user.role != 'recruiter':
        flash("Access denied.", "error")
        return redirect(url_for('views.job_seeker_home'))
    
    recruiter_id = current_user.user_id
    title = request.args.get("title", "")
    location = request.args.get("location", "")
    company = request.args.get("company", "")
    salary_min = request.args.get("salary_min", type=int, default=0)
    salary_max = request.args.get("salary_max", type=int, default=999999)
    page = request.args.get("page", type=int, default=1)
    per_page = 6  # Number of jobs per page

    query = Job.query.filter(Job.recruiter_id == recruiter_id)

    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    query = query.filter(
        Job.salary_max >= salary_min,  # Ensure the job's max salary is at least the requested min_salary
        Job.salary_min <= salary_max   # Ensure the job's min salary is at most the requested max_salary
    )

    jobs = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "jobs": [{"id": job.job_id, "title": job.title, "company": job.company, "location": job.location, "salary": [job.salary_min, job.salary_max]} for job in jobs.items],
        "total_pages": jobs.pages,
        "current_page": jobs.page
    })

@views.route('/get-all-jobs', methods=['GET'])
@login_required
def get_all_jobs():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))
    
    title = request.args.get("title", "")
    location = request.args.get("location", "")
    company = request.args.get("company", "")
    salary_min = request.args.get("salary_min", type=int, default=0)
    salary_max = request.args.get("salary_max", type=int, default=999999)
    page = request.args.get("page", type=int, default=1)
    per_page = 6  # Number of jobs per page

    query = Job.query
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    query = query.filter(
        Job.salary_max >= salary_min,  # Ensure the job's max salary is at least the requested min_salary
        Job.salary_min <= salary_max   # Ensure the job's min salary is at most the requested max_salary
    )

    jobs = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "jobs": [{"id": job.job_id, "title": job.title, "company": job.company, "location": job.location, "salary": [job.salary_min, job.salary_max]} for job in jobs.items],
        "total_pages": jobs.pages,
        "current_page": jobs.page
    })

@views.route('/view-all-job', methods=['GET'])
@login_required
def view_all_job():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))
    
    return render_template('all_job_posts.html')

@views.route('/view-job', methods=['GET'])
@login_required
def view_job():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.job_seeker_home'))
    
    job_id = request.args.get("job_id", "")
    
    return render_template('view_job.html', job_id=job_id)

@views.route('/get-job-data', methods=['GET'])
@login_required
def get_job():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))

    job_id = request.args.get('job_id')

    if not job_id:
        return jsonify({"error": "Job ID is required."}), 400

    # Query Job with recruiter and user details
    job = db.session.query(Job, Recruiter, User).\
        join(Recruiter, Job.recruiter_id == Recruiter.user_id).\
        join(User, Recruiter.user_id == User.user_id).\
        filter(Job.job_id == job_id).first()

    if not job:
        return jsonify({"error": "Job not found."}), 404
    
    query = JobApplication.query.filter(JobApplication.job_id == job_id,JobApplication.jobseeker_id == current_user.user_id)
    result = query.first()
    status = False
    if result:
        status=True

    job_data = {
        "job_id": job.Job.job_id,
        "title": job.Job.title,
        "company": job.Job.company,
        "location": job.Job.location,
        "job_type": job.Job.job_type,
        "salary_min": job.Job.salary_min,
        "salary_max": job.Job.salary_max,
        "deadline": job.Job.deadline.strftime("%Y-%m-%d"),
        "description": job.Job.description,
        "date_posted": job.Job.date_posted.strftime("%Y-%m-%d %H:%M:%S"),
        "recruiter": {
            "name": job.User.name,
            "email": job.User.email,
            "about_company": job.Recruiter.about_company
        },
        "status": status
    }

    return jsonify(job_data)

@views.route('/store-application', methods=['POST'])
@login_required
def store_application():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))

    job_id = request.form.get('job_id')
    resume_file = request.files.get('resume')

    if not job_id or not resume_file:
        return jsonify({"error": "Missing job ID or resume file."}), 400

    # Define the upload folder
    upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\uploaded_resumes')
    os.makedirs(upload_folder, exist_ok=True)

    # Secure the filename and save the file
    filename = secure_filename(resume_file.filename)
    resume_file_path = os.path.join(upload_folder, filename)
    resume_file.save(resume_file_path)

    # Modify the path for database storage
    resume_file_path = resume_file_path.replace("\\website\\..", "").replace("\\", "/")

    # Store the application in the database
    application = JobApplication(
        job_id=job_id,
        jobseeker_id=current_user.user_id,
        resume_file_path=resume_file_path
    )
    db.session.add(application)
    db.session.commit()

    #score the application
    # Query the Job description
    job = Job.query.filter_by(job_id=job_id).first()

    # Get the description
    job_description = job.description if job else None

    # Query the RecruiterJobScoringWeights for this job
    scoring_weights = RecruiterJobScoringWeights.query.filter_by(job_id=job_id).first()

    res = calculate_resume_results(resume_file_path, job_description, scoring_weights)

    total_score = sum(res['section_scores'].values())
    job_post_results = JobPostResult(
        jobseeker_id = current_user.user_id,
        job_id = job_id,
        scores = res['section_scores'],
        total_score = total_score,
        recommendations = res['recommendations'],
        resume_file_path = resume_file_path
    )
    db.session.add(job_post_results)
    db.session.commit()

    # Since we're using fetch() to send data to your Flask server, Flask’s redirect won't work automatically 
    #return redirect(url_for('views.jobseek_result', result_id=job_post_results.result_id, jobseek_id=current_user.user_id))
    redir_url = url_for('views.job_post_result', result_id=job_post_results.result_id, jobseek_id=current_user.user_id)

    return jsonify({"redirect_url": redir_url })


@views.route("/job-post-result", methods=['GET'])
@login_required
def job_post_result():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))

    return render_template("job_post_result.html")

@views.route('/get-job-post-result', methods=['GET'])
@login_required
def get_job_post_results():
    if current_user.role != 'job-seeker':
        flash("Access denied.", "error")
        return redirect(url_for('views.recruiter_home'))
    
    result_id = request.args.get('result_id')
    jobseek_id = request.args.get('jobseek_id')
    download = request.args.get('download', 'false').lower() == 'true'  # Check if 'download' is true

    # Query the database for the result
    result = JobPostResult.query.filter_by(result_id=result_id, jobseeker_id=jobseek_id).first()

    if not result:
        flash("No results found for the given parameters.", "danger")
        return redirect(url_for('views.job_seeker_home'))

    # Get the resume file path
    resume_file_path = result.resume_file_path

    # If `download` is True, return the PDF file directly
    if download:
        if not resume_file_path or not os.path.exists(resume_file_path):
            abort(404, description="Resume file not found.")
        return send_file(resume_file_path, as_attachment=False, mimetype='application/pdf')

    # Otherwise, return JSON response
    return jsonify({
        "resume_file_path": resume_file_path,
        "recommendations": result.recommendations,
        "scores": result.scores
    })

@views.route('/get-job-candidates', methods=['GET'])
def job_candidates():
    job_id = request.args.get('job_id', type=int)  # Get job_id from request

    download = request.args.get('download', 'false').lower() == 'true'  # Check if 'download' is true
    

    if not job_id:
        return jsonify({"error": "Job ID is required"}), 400

    # Query JobPostResult filtered by job_id
    results = (
        db.session.query(
            JobPostResult.result_id,
            JobPostResult.total_score,
            JobPostResult.resume_file_path,
            User.name,
            User.email,
            User.phone
        )
        .join(JobSeeker, JobPostResult.jobseeker_id == JobSeeker.user_id)
        .join(User, JobSeeker.user_id == User.user_id)
        .filter(JobPostResult.job_id == job_id)  # Filter by job_id
        .order_by(JobPostResult.total_score.desc())  # Sort highest score first
        .all()
    )

    # Convert results to JSON
    results_data = [
        {
            "result_id": result.result_id,
            "name": result.name,
            "email": result.email,
            "phone": result.phone,
            "total_score": result.total_score,
            "resume_file_path": result.resume_file_path
        }
        for result in results
    ]

    # If `download` is True, return the PDF file directly
    if download:
        result_id = request.args.get('result_id',"")
        matching_result = next((item for item in results_data if item["result_id"] == result_id), None)
        print(result_id)

        if matching_result:
            if not matching_result.resume_file_path or not os.path.exists(matching_result.resume_file_path):
                abort(404, description="Resume file not found.")
            return send_file(matching_result.resume_file_path, as_attachment=False, mimetype='application/pdf')
        else:
            print("No matching result found.")
        

    return jsonify(results_data)  # Return as JSON

@views.route('/view-job-candidates', methods=['GET'])
def view_job_candidates():
    job_id = request.args.get("job_id", "")

    return render_template('view_candidates.html', job_id=job_id)