from flask import Flask
from flask import render_template

def create_app():

    app = Flask(__name__)
    

    @app.route("/")
    def landing():
        return render_template("landing.html")
    
    return app