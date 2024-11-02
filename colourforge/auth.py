"""
Module: auth.py

Description:
------------
This module handles the authentication Blueprint for the Colourforge
Application.
It deals with user authentication functionalities, including user registration,
login, logout, account management (such as changing email and resetting
password), and account deletion.
All routes within this Blueprint are prefixed with '/auth' and manage
user-related operations ensuring secure access and data integrity.

Functions:
----------
- logout(): Logs the user out and redirects them to the home page.
- register(): Handles user registration, including validation and sending
welcome emails.
- login(): Authenticates users and manages login sessions.
- account(): Renders the user's account page.
- change_email(): Allows users to change their email addresses with password
confirmation.
- reset_password(): Enables users to reset their passwords securely.
- delete_account(): Allows users to delete their accounts after password
verification.

Notes:
----------
 - Many of the routes defined in this module are restricted to logged in users.
"""
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
from colourforge.mail import (
    welcome_email,
    account_deletion,
    email_change,
    password_change
)


auth = Blueprint('auth', __name__)


@auth.route('/logout')
@login_required
def logout():
    """
    This view function logs out the currently authenticated user using
    Flask-Login's `logout_user` function. After logging out, it flashes a
    success message and redirects the user to the home page.

    Returns:
        Response:
            - Redirects the user to the home page with a success message.
    """
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('routes.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration by validating input data, creating a new user
    in the database, initializing default user data, logging the user in, and
    sending a welcome email. On a GET request, it renders the registration
    page.

    Returns:
        Response:
            - On GET: Renders the registration HTML template.
            - On POST:
                - Redirects to the home page upon successful registration.
                - Redirects back to the registration page with error messages
                if validation fails.
    """
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Check to see if user exists
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('User already exists', category='error')
        elif len(username) < 4:
            flash(
                'Username must be at least four characters.',
                category='error'
                )
        elif len(email) < 4:
            flash('Email must be at least four characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(
                    password1,
                    method='pbkdf2:sha512'
                    )
                )
            db.session.add(new_user)
            db.session.commit()

            create_default_recipe(new_user)
            login_user(new_user, remember=True)
            welcome_email(new_user.email, new_user.username)
            flash('Account created!', category='success')
            return redirect(url_for('routes.home'))

    return render_template("register.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user authentication by verifying the provided username/email and
    password.
    On successful authentication, logs the user in and redirects them to the
    home page.
    On a GET request, it renders the login page.

    Args:
        None

    Returns:
        Response:
            - On GET: Renders the login HTML template.
            - On POST:
                - Redirects to the home page upon successful login.
                - Redirects back to the login page with error messages if
                authentication fails.
    """
    if request.method == 'POST':
        user_input = request.form.get('login')
        password = request.form.get('password')

        if not user_input or not password:
            flash(
                'Please enter both username/email and password',
                category='error'
                )
            return redirect(url_for('routes.home'))

        user = User.query.filter_by(email=user_input).first()

        # Check that user exists
        if not user:
            user = User.query.filter_by(username=user_input).first()

        # Ensure password is correct for the user.
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Successfully Logged in!', category='success')
                return redirect(url_for('routes.home'))
            else:
                flash('Incorrect password, try again', category='error')
                return redirect(url_for('routes.home'))

        else:
            flash('User not found', category='error')
            return redirect(url_for('routes.home'))

    else:
        # For GET requests, render the login page
        return render_template("login.html")


@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    This view function displays the authenticated user's account page, allowing
    them to manage their account settings such as changing email, resetting
    password, or deleting their account. Access to this page is restricted to
    logged-in users.

    Returns:
        Response:
            - On GET: Renders the account HTML template with the current user's
            information.
            - On POST: Currently, POST requests are not handled here and will
            default to rendering the account page.
    """
    return render_template("account.html", user=current_user)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    """
    Allows a logged-in user to update their email address by providing a new
    email and confirming their current password. Ensures that the new email is
    unique and different from the existing one. Upon successful change, sends
    an email notification to the user.

    Args:
        None

    Returns:
        Response:
            - On GET: Renders the account HTML template with the current user's
            information.
            - On POST:
                - Redirects to the account page with success message upon
                successful email change.
                - Redirects back to the account page with error messages if
                validation fails.
    """
    if request.method == 'POST':
        new_email = request.form.get('email')
        password = request.form.get('password-email')

        # Make sure user has entered an email
        if not new_email:
            flash('Please enter the new email address to change this.',
                  category='error'
                  )
            return redirect(url_for('auth.account'))

        # Make sure the user has entered a password
        elif not password:
            flash('Please enter your current password to change your email.',
                  category='error'
                  )
            return redirect(url_for('auth.account'))

        # Make sure password is correct
        elif not check_password_hash(current_user.password, password):
            flash('Incorrect password, try again', category='error')
            return redirect(url_for('auth.account'))

        # Make sure the email address isn't already being used.
        elif User.query.filter_by(email=new_email).first():
            flash('This email address is already in use', category='error')
            return redirect(url_for('auth.account'))

        # Make sure the new email isn't the same as the users existing email
        elif new_email == current_user.email:
            flash(
                """The new email address must be different from the existing
                one.""",
                category='error'
            )
            return redirect(url_for('auth.account'))

        # Proceed to update the email address.
        else:
            old_email = current_user.email
            current_user.email = new_email
            db.session.commit()
            email_change(new_email, old_email, current_user.username)
            flash(
                'Your email has been successfully changed.',
                category='success'
            )

        return redirect(url_for('auth.account'))

    return render_template("account.html", user=current_user)


@auth.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    """
    Allows a logged-in user to reset their password by providing their current
    password and entering a new password twice for confirmation. Ensures that
    the new password meets security requirements and is different from the
    current password. Upon successful password reset, sends a notification
    email to the user.

    Returns:
        Response:
            - On GET: Renders the account HTML template with the current user's
            information.
            - On POST:
                - Redirects to the account page with a success message upon
                successful password change.
                - Redirects back to the account page with error messages if
                validation fails.
    """
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        current_password = request.form.get('password-reset')
        current_password_hash = current_user.password

        # Check for password in password field
        if not current_password:
            flash(
                'Please enter your current password to change your password.',
                category='error'
            )
            return redirect(url_for('auth.account'))

        # Make sure current password is correct
        elif not check_password_hash(current_user.password, current_password):
            flash('Incorrect current password, try again', category='error')
            return redirect(url_for('auth.account'))

        # Make sure both new password fields match
        elif password1 != password2:
            flash('New passwords don\'t match!', category='error')
            return redirect(url_for('auth.account'))

        # Make sure the new password is not the same as the old password
        elif check_password_hash(current_password_hash, password1):
            flash("""Your new password cannot be the same as your current
                  password.""",
                  category='error'
                  )
            return redirect(url_for('auth.account'))

        # Make sure password is greater than 7 characters.
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
            return redirect(url_for('auth.account'))

        # Change password.
        else:
            password = generate_password_hash(
                                            password1,
                                            method='pbkdf2:sha512'
                                            )
            current_user.password = password
            db.session.commit()
            password_change(current_user.email, current_user.username)
            flash(
                'Your password has been successfully changed',
                category='success'
            )
            return redirect(url_for('auth.account'))

        return redirect(url_for('auth.account'))

    return render_template("account.html", user=current_user)


@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """
    Allows a logged-in user to delete their account by providing their current
    password. Ensures that administrators cannot delete their own accounts to
    ensure at least one admin exists. Upon successful deletion, sends an
    account deletion notification email, logs the user out, and redirects them
    to the home page.

    Returns:
        Response:
            - On POST:
                - Redirects to the home page with a success message upon
                successful deletion.
                - Redirects back to the account page with error messages if
                validation fails.
            - On GET: Redirects to the account page.
    """
    if request.method == 'POST':
        current_password = request.form.get('password-delete')

        # Make sure password was entered
        if not current_password:
            flash(
                'Please enter your current password to delete your account.',
                category='error'
            )

        # Make sure the password is correct
        elif not check_password_hash(current_user.password, current_password):
            flash('Incorrect current password, try again', category='error')
            return redirect(url_for('auth.account'))

        # Make sure the admin isn't deleting themselves.
        elif current_user.is_admin:
            flash(
                """You are an admin user so cannot delete your own
                account, please message another admin to do this or
                to demote you so you can do this yourself.
                """,
                category="error"
            )
            return redirect(url_for('auth.account'))

        # Proceed to delete account only if password is correct
        else:
            user = current_user
            account_deletion(current_user.email, current_user.username)
            db.session.delete(user)
            db.session.commit()

            flash('Your account has been deleted.', category='success')
            logout_user()
            return redirect(url_for('routes.home'))

    return redirect(url_for('auth.account'))
