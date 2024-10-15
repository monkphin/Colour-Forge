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
    """
    Logs the user out and redirects them to the home page.

    Returns:
        Response: Redirects the logged out user to the home page.
    """
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('routes.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registers a new user account and logs them in on a POST request.
    Otherwise, renders the register page.
    If the user already exists, or the form data is invalid, the user is redirected to the register page.
    

    Returns:
        Response: The rendered register page.
    """
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

    return render_template("register.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in on a POST request. This shares the same page as the home page.
    Renders the home page on a GET request.

    Returns:
        Response: The rendered home page.
    """
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
    """
    Renders the account page.

    Returns:
        Renders: The account page.
    """
    return render_template("account.html", user=current_user)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    """
    Changes the user's email address on a POST request from the account page. 
    If the email is already in use, the user is redirected to the account page with an error message.

    Returns:
        Render: The account page.
    """
    if request.method == 'POST':
        new_email = request.form.get('email')

        if User.query.filter_by(email=new_email).first():
            flash('This email address is already in use', category='error')
        else:
            current_user.email = new_email
            db.session.commit()
            flash('Your email has been successfully changed', category='success')

        return redirect(url_for('auth.account'))

    return render_template("account.html", user=current_user)


@auth.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    """
    Resets the user's password on a POST request from the account page.
    If the passwords don't match, the user is redirected to the account page with an error message.
    If the new password is the same as the current password, the user is redirected to the account page with an error message.
    If the password is less than 7 characters, the user is redirected to the account page with an error message.
    
    Returns:
        Response: Redirects the user to the account page.
    """
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

    return render_template("account.html", user=current_user)


@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """
    Deletes the user's account on a POST request from the account page.
    This flashes a success message and logs the user out before redirecting them to the home page.

    Returns:
        Response: Redirects the user to the home page.
    """
    if request.method == 'POST':
        user = current_user
        db.session.delete(user)  
        db.session.commit()

        flash('Your account has been deleted', category='success')
        logout_user()
        return redirect(url_for('routes.home'))
    
    return redirect(url_for('auth.account'))