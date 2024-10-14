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


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

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


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('login')
        password = request.form.get('password')
       
        if not user or not password:
            flash('Please enter both username/email and password', category='error')
            return redirect(url_for('routes.home'))

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
        return redirect(url_for('routes.home'))
    else:
        # For GET requests, render the login page
        return redirect(url_for('routes.home'))


@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template("account.html", user=current_user, tag_dict={})


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    if request.method == 'POST':
        new_email = request.form.get('email')

        if User.query.filter_by(email=new_email).first():
            flash('This email address is already in use', category='error')
        else:
            current_user.email = new_email
            db.session.commit()
            flash('Your email has been successfully changed', category='success')

        return redirect(url_for('auth.account'))

    return render_template("account.html", user=current_user, tag_dict={})


@auth.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        current_password_hash = current_user.password

        if password1 != password2: 
            flash('Passwords don\'t match!', category='error')
        elif check_password_hash(current_password_hash, password1):
            flash('Your new password cannot be the same as your current password', category='error')
        elif len(password1) <7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            password = generate_password_hash(password1, method='pbkdf2:sha512')
            current_user.password = password
            db.session.commit()
            flash('Your password has been successfully changed', category='success')

            return redirect(url_for('auth.account'))
        
        return redirect(url_for('auth.account'))

    return render_template("account.html", user=current_user, tag_dict={})


@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        user = current_user
        db.session.delete(user)  
        db.session.commit()

        flash('Your account has been deleted', category='success')
        logout_user()
        return redirect(url_for('routes.home', tag_dict={}))
    
    return redirect(url_for('auth.account'))