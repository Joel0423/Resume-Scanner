from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

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

    from .models import JobSeeker
    with app.app_context():
            db.create_all()

    
    return app


def create_database(app):
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()