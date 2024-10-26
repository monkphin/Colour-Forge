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
from math import ceil

# Local imports
from colourforge import db
from colourforge.models import User, Recipe


admin = Blueprint('admin', __name__)


@admin.before_request
def restricted_access():
    if not current_user.is_authenticated:
        flash('Please log in to access the admin area!', category='error')
        return redirect(url_for('auth.login'))
    elif not current_user.is_admin:
        flash(
            'You are not authorised to access the admin area!',
            category='error'
        )
        return redirect(url_for('routes.home'))


@admin.route('/admin_dash', methods=['GET', 'POST'])
@login_required
def admin_dash():
    """
    Renders the admin dashboard page, with a list of all users and their
    details

    Returns:
        Response: The rendered admin dashboard page.
    """
    # Get all Users
    users = User.query.all()

    page = request.args.get('page', 1, type=int)
    per_page = 6  # users per page
    total = len(users)
    total_pages = ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = users[start:end]

    return render_template(
        "admin.html",
        user=current_user,
        users=paginated_users,
        page=page,
        total_pages=total_pages
    )


@admin.route('/change_email/<int:user_id>', methods=['POST'])
@login_required
def change_email(user_id):
    """
    Change the email of a selected user on the admin page.

    Args:
        user_id (int): The ID of the user to change the email of.

    Returns:
        Response: Redirects the user to the admin dashboard.
    """
    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))

    user = User.query.get_or_404(user_id)
    admin_password = request.form.get('password-email')
    new_email = request.form.get('email')

    # Make sure an email address has been entered. 
    if new_email == '':
        flash('Please enter the new email address.', category='error')
        return redirect(url_for('admin.admin_dash'))
    # Make sure the email is unique
    elif User.query.filter(User.email == new_email, User.id != User.id).first():
        flash(
            """The new email address is already in use.
            Please check with the user."""
            , category='error'
        )
        return redirect(url_for('admin.admin_dash'))
    # Make sure the admin password has been entered. 
    elif not admin_password: 
        flash(
            'Please enter your admin password to change the users email.', 
            category='error'
        )
        return redirect(url_for('admin.admin_dash'))
    # Make sure the admin password is correct
    elif not check_password_hash(current_user.password, admin_password):
        flash('Incorrect admin password, try again', category='error')
        return redirect(url_for('admin.admin_dash'))
    else:
        user.email = new_email
        db.session.commit()
        flash('Email has been successfully updated!', category='success')
    return redirect(url_for('admin.admin_dash'))


@admin.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    """
    Reset the password of a selected user on the admin page.

    Args:
        user_id (int): The ID of the user to reset the password of.

    Returns:
        Response: Redirects the user to the admin dashboard.
    """
    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))

    user = User.query.get_or_404(user_id)

    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    admin_password = request.form.get('password-reset')
    admin_password_hash = current_user.password

    # Make sure an admin password is entered. 
    if not admin_password:
        flash(
            'Please enter your admin password to change the users password',
            category='error'
        )
        return redirect(url_for('admin.admin_dash'))
    # Make sure entered password matches the admin users password. 
    elif not check_password_hash(current_user.password, admin_password):
        flash('Incorrect admin password, try again', category='error')
        return redirect(url_for('admin.admin_dash'))
    # Make sure both password fields are filled to prevent errors. 
    elif not password1 or not password2:
        flash('Both password fields are required', category='error')
        return redirect(url_for('admin.admin_dash'))
    # Make sure both fields match. 
    elif password1 != password2:
        flash('Passwords don\'t match!', category='error')
        return redirect(url_for('admin.admin_dash'))
    # Make sure password entered is at least 7 characters. 
    elif len(password1) < 7:
        flash('Password must be at least 7 characters.', category='error')

    # Check if new password is the same as the users current password
    elif check_password_hash(user.password, password1):
        flash(
        'The new password cannot be the same as the user\'s current password',
        category='error'
        )
        return redirect(url_for('admin.admin_dash'))
    # Check if new password is the same as admin's password
    elif check_password_hash(admin_password_hash, password1):
        flash(
            'The new password cannot be the same as your own password',
            category='error'
            )
        return redirect(url_for('admin.admin_dash'))
    else:
        user.password = generate_password_hash(
            password1,
            method='pbkdf2:sha512'
        )
        db.session.commit()
        flash(
            'The user\'s password has been successfully changed',
            category='success'
        )

        return redirect(url_for('admin.admin_dash'))

    return redirect(url_for('admin.admin_dash'))


@admin.route('/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    """
    A toggle to set a specific user as an admin or not.

    Args:
        user_id (int): The ID of the user to toggle admin status of.
    """
    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))

    user = User.query.get_or_404(user_id)
    admin_password = request.form.get('toggle_password') 

    # Make sure the admin isn't demoting themselves.
    if user.id == current_user.id:
        flash(
            """You cannot demote your own account, please message another admin
            to do this""",
            category="error"
            )
        return redirect(url_for('admin.admin_dash'))
    # Check for admins password.
    elif not admin_password:
        flash(
            'Please enter your admin password to change the users admin status',
            category='error'
        )
        return redirect(url_for('admin.admin_dash'))
    # Make sure correct password is entered.
    elif not check_password_hash(current_user.password, admin_password):
        flash('Incorrect admin password, try again', category='error')
        return redirect(url_for('admin.admin_dash'))

    # Toggle status between admin/none admin.     
    if user.is_admin:
        user.is_admin = False
        db.session.commit()
        flash('User is no longer an admin!', category='success')
    else:
        user.is_admin = True
        db.session.commit()
        flash('User has been promoted to an admin!', category='success')

    return redirect(url_for('admin.admin_dash'))


@admin.route('/delete_account/<int:user_id>', methods=['POST'])
@login_required
def delete_account(user_id):
    """
    Delete a specified user account from the admin dashboard.

    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        Response: Redirects the user to the admin dashboard.
    """
    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))

    # Pull user details to be deleted.
    user = User.query.get_or_404(user_id)
    admin_password = request.form.get('delete_user_password') 

    # Make sure an admin password has been entered. 
    if not admin_password:
        flash(
            'Please enter your password to delete the account',
            category='error'
        )
        return redirect(url_for('admin.admin_dash'))
    # Make sure correct password is entered.
    elif not check_password_hash(current_user.password, admin_password):
        flash('Incorrect admin password, try again', category='error')
        return redirect(url_for('admin.admin_dash'))
    # Make sure the admin isn't deleting themselves. 
    elif user.id == current_user.id:
        flash(
            "You cannot delete your own account, "
            "please message another admin to do this",
            category="error"
        )
        return redirect(url_for('admin.admin_dash'))

    # Delete user.
    db.session.delete(user)
    db.session.commit()

    flash(f'Account for {user.username} has been deleted.', category='success')

    return redirect(url_for('admin.admin_dash'))


@admin.route('/recipe_admin', methods=['GET', 'POST'])
@login_required
def recipe_admin():
    """
    Renders the admin level recipes page, with a list of all recipes and their
    details

    Returns:
        Response: The rendered admin recipes page.
    """
    recipes = Recipe.query.all()

    page = request.args.get('page', 1, type=int)
    per_page = 6  # Recipes per page
    total = len(recipes)
    total_pages = ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_recipes = recipes[start:end]

    return render_template(
        "recipe_admin.html",
        recipes=paginated_recipes,
        page=page,
        total_pages=total_pages,
        user=current_user
    )


@admin.route('/user_search', methods=['GET'])
@login_required
def user_search():
    search = request.args.get('user_search')
    if not search:
        flash("Please enter a search term.", category="error")
        return redirect(url_for('admin.admin_dash'))

    matching_users = User.query.filter(
        User.username.ilike(f"%{search}%")
    ).all()

    if not matching_users:
        flash(
            f"No users found that match your search: { search }",
            category="info"
        )

    return render_template(
        'admin_user_search_results.html',
        users=matching_users,
        search=search
    )


@admin.route('/recipe_search', methods=['GET'])
@login_required
def recipe_search():
    search = request.args.get('recipe_search')
    if not search:
        flash("Please enter a search term.", category="error")
        return redirect(url_for('admin.recipe_admin'))

    # Perform the recipe search
    matching_recipes = Recipe.query.filter(
        Recipe.recipe_name.ilike(f"%{search}%")
    ).all()

    if not matching_recipes:
        flash(
            f"No recipes found that match your search: { search }",
            category="info"
        )

    return render_template(
        'admin_recipe_search_results.html',
        recipes=matching_recipes,
        search=search
    )
