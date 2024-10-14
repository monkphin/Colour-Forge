# Third-Party Library Imports
from flask import (
    flash,
    render_template, 
    request, 
    redirect, 
    url_for,
    Blueprint
)
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# Local imports
from colourforge import db
from colourforge.models import User
from colourforge.seed import create_default_recipe


auth = Blueprint('auth', __name__)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('routes.home'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('login')
        password = request.form.get('password')
       
        if not user or not password:
            flash('Please enter both username/email and password', category='error')
            return render_template('routes.home')

        user = User.query.filter_by(email=user).first() or User.query.filter_by(username=user).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Successfully Logged in!', category='success')
                return redirect(url_for('routes.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('User not found', category='error')

        # After flashing error messages, render login page again
        return render_template('home.html', user=current_user, tag_dict={}) 
    else:
        # For GET requests, render the login page
        return render_template('home.html', user=current_user, tag_dict={})


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

        # Check to see if user exists
        existing_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()

        if existing_user:
            flash('User already exists', category='error')
        elif len(username) < 4:
            flash('Username must be at least four characters.', category='error')
        elif len(email) < 4: 
            flash('Email must be at least four characters.', category='error')
        elif password1 != password2: 
            flash('Passwords don\'t match!', category='error')
        elif len(password1) <7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha512'))
            db.session.add(new_user)
            db.session.commit()

            create_default_recipe(new_user)

            login_user(new_user, remember=True)
            flash('Account created!', category='success')

            return redirect(url_for('routes.home'))


    return render_template("register.html", user=current_user, tag_dict={})

@auth.route('/account', methods=['GET', 'POST'])
def account():
    return render_template("account.html", user=current_user, tag_dict={})

@auth.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    pass

@auth.route('/admin', methods=['GET', 'POST'])
def admin():
    pass