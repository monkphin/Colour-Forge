import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
if os.path.exists("env.py"):
    import env # noqa


app = Flask(__name__)
# Add config - secret keys/DB details etc
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")

# Cloudinary config
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"), 
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

db = SQLAlchemy(app)

from colourforge import routes # noqa