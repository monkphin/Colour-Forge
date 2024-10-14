import os
from flask import Flask, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask_login import LoginManager
from mailjet_rest import Client

if os.path.exists("env.py"):
    import env  # noqa


app = Flask(__name__)


# Add config - secret keys/DB details etc
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if os.environ.get("DEVELOPMENT") == "True":
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
else:
    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri  # Use the modified URI

# Cloudinary config
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

# Mailjet config
api_key = os.environ.get('MJ_APIKEY_PUBLIC')
api_secret = os.environ.get('MJ_APIKEY_PRIVATE')
mailjet = Client(auth=(api_key, api_secret))


db = SQLAlchemy(app)


# Handle Logins
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


from colourforge.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Blueprint routes
from colourforge.routes import routes  # noqa
from colourforge.auth import auth    # noqa
from colourforge.admin import admin    # noqa


app.register_blueprint(routes)
app.register_blueprint(auth) 
app.register_blueprint(admin) 


# Global 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Global 500 error handler
@app.errorhandler(500)
def special_exception_handler(error):
    return render_template('500.html'), 500