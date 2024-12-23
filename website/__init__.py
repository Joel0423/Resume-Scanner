from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "resume_scanner_db"
DB_USERNAME = "root"
DB_PASSWORD = "pass123"



def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = "Joe nd Maha"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@localhost/{DB_NAME}'
    db.init_app(app)
    
    # views for the application
    from .views import views
    from .auth import auth_views
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth_views, url_prefix="/")

    # create database

    from .models import User
    with app.app_context():
            db.create_all()

    login_manager = LoginManager()
    # if user is not logged in, and login is req. where should flask redirect-
    login_manager.login_view = 'auth_views.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
         return User.query.get(int(user_id))

    
    return app


def create_database(app):
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()