import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

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

# SendGrid config
app.config["SENDGRID_API_KEY"] = os.environ.get("SENDGRID_API_KEY")

db = SQLAlchemy(app)

from colourforge import routes  # noqa
