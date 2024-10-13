# Third-Party Library Imports
from flask import (
    flash,
    render_template, 
    request, 
    redirect, 
    url_for,
    Blueprint
)

from werkzeug.security import generate_password_hash, check_password_hash

# Local imports
from colourforge import app, db, cloudinary, cloudinary_url
from colourforge.models import (User, 
                                Recipe, 
                                RecipeStage, 
                                RecipeImage, 
                                RecipeTag, 
                                EntityTag)

auth = Blueprint('auth', __name__)

@auth.route('/logout')
def login():
    pass


@auth.route('/login')
def logout():
    pass


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password1: {password1}")
        print(f"Password2: {password2}")

        if len(username) < 4:
            flash('Username must be at least four characters.', category='error')
        elif len(email) < 4: 
            flash('Email must be at least four characters.', category='error')
        elif password1 != password2: 
            flash('Passwords don\'t match!', category='error')
        elif len(password1) <7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, user_name=username, password=generate_password_hash(password1, method='pbkdf2:sha512'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('home'))

    return render_template("register.html")