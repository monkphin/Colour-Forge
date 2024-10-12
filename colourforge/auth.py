# Third-Party Library Imports
from flask import (
    flash,
    render_template, 
    request, 
    redirect, 
    url_for,
    Blueprint
)

auth = Blueprint('auth', __name__)