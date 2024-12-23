from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import JobSeeker, Recruiter, User
from . import db # from __init__.py
from werkzeug.security import generate_password_hash, check_password_hash

auth_views =  Blueprint('auth_views', __name__)

@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Login Success', category="login-success")

                if user.role == "recruiter":
                    return redirect(url_for("views.recruiter_home"))
                elif user.role == "job-seeker":
                    return redirect(url_for("views.job_seeker_home"))
            else:
                flash('Login Failed, wrong password', category="login-error")
        else:
            flash('Login Failed, invalid email', category="login-error")

    return render_template("login.html")

@auth_views.route('/logout')
def logout():
    return "<p>logout</p>"

@auth_views.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        phone = request.form.get('phone')
        company = request.form.get('company')
        address = request.form.get('address')
        about = request.form.get('about')
        profile_pic = request.form.get('profile-pic')
        dob = request.form.get('dob')
        role = request.form.get('role')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("This email is already used by another user", category="sign-up-error")
            return redirect(url_for('views.landing'))

        new_user = User(name=name, email=email, phone=phone, address=address, dob=dob, role=role, password=generate_password_hash(password, method="scrypt"))
        
        if role == "recruiter":
            new_recruiter = Recruiter(user = new_user, about_company=about)
            db.session.add(new_user)
            db.session.add(new_recruiter)
        elif role == "job-seeker":
            new_jobseeker = JobSeeker(user= new_user, about=about, profile_pic="test")
            db.session.add(new_user)
            db.session.add(new_jobseeker)

        db.session.commit()

        flash("account created", category="sign-up-success")
        return redirect(url_for('views.landing'))



    return render_template("sign-up.html")