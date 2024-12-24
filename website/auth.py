from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import JobSeeker, Recruiter, User
from . import db # from __init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .views import redirect_home

auth_views =  Blueprint('auth_views', __name__)

@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_home()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Login Success', category="login-success")

                login_user(user, remember=True)
                return redirect_home()
            else:
                flash('Login Failed, wrong password', category="login-error")
        else:
            flash('Login Failed, invalid email', category="login-error")

    return render_template("login.html")

@auth_views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.landing'))

@auth_views.route('/j-sign-up', methods=['GET', 'POST'])
def j_sign_up():
    if current_user.is_authenticated:
        return redirect_home()
    
    if request.method == "POST":
        
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        about = request.form.get('about')
        profile_pic = request.form.get('profilePic')
        dob = request.form.get('dob')
        role = "job-seeker"

        user = User.query.filter_by(email=email).first()
        if user:
            flash("This email is already used by another user", category="sign-up-error")
            return redirect(url_for('views.landing'))

        new_user = User(name=name, email=email, phone=phone, address=address, dob=dob, role=role, password=generate_password_hash(password, method="scrypt"))

        new_jobseeker = JobSeeker(user= new_user, about=about, profile_pic="test")
        db.session.add(new_user)
        db.session.add(new_jobseeker)

        db.session.commit()

        flash("account created", category="sign-up-success")
        login_user(new_user, remember=True)
        return redirect_home()

    return render_template("JSignUp.html")

@auth_views.route('/r-sign-up', methods=['GET', 'POST'])
def r_sign_up():
    if current_user.is_authenticated:
        return redirect_home()
    
    if request.method == "POST":
        
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        company = request.form.get('company')
        dob = request.form.get('dob')
        role = "recruiter"

        user = User.query.filter_by(email=email).first()
        if user:
            flash("This email is already used by another user", category="sign-up-error")
            return redirect(url_for('views.landing'))

        new_user = User(name=name, email=email, phone=phone, address=address, dob=dob, role=role, password=generate_password_hash(password, method="scrypt"))
        
        new_recruiter = Recruiter(user = new_user, about_company=company)
        db.session.add(new_user)
        db.session.add(new_recruiter)

        db.session.commit()

        flash("account created", category="sign-up-success")
        login_user(new_user, remember=True)
        return redirect_home()

    return render_template("RSignUp.html")

@auth_views.route('/recruiter-or-jobseeker', methods=['GET'])
def recruiter_or_jobseeker():
    if current_user.is_authenticated:
        return redirect_home()
    
    return render_template('RecruiterOrJobseeker.html')