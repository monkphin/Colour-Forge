"""
Module: admin.py

Description:
----------
This module handles the admin blueprint for the Colourforge Application.
It provides administrative functionalities such as user management and recipe
moderation.

Functions:
----------
- restricted_access(): Restricts access to admin routes to authenticated admin
users.
- admin_dash(): Renders the admin dashboard displaying user details.
- change_email(user_id): Allows admins to change a user's email address.
- reset_password(user_id): Allows admins to reset a user's password.
- toggle_admin(user_id): Toggles a user's admin status.
- delete_account(user_id): Deletes a user account.
- recipe_admin(): Renders the admin recipes page.
- user_search(): Searches for users based on a query.
- recipe_search(): Searches for recipes based on a query.
- confirm_edit(recipe_id): Confirms admin password before editing a recipe.
- confirm_delete(recipe_id): Confirms admin password before deleting a recipe.

Notes:
------
- Access to routes defined in this module is restricted to admin users.

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
from math import ceil

# Local imports
from colourforge import db, cloudinary
from colourforge.models import (
                                User,
                                Recipe,
                                RecipeStage,
                                RecipeImage,
                                EntityTag
                            )
from colourforge.helpers import remove_recipe
from colourforge.mail import (
                            admin_account_deletion,
                            admin_password_change,
                            admin_email_change
                            )

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
    This function retrieves all users from the database, paginates them,
    and renders the admin dashboard template. The dashboard provides
    administrators list of all registered users and their details.

    Returns:
        Response: The rendered admin dashboard HTML page.
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
    Allows an administrator to change the email address of a user.
    The admin must provide their own password to authorize this change.

    An email notification is sent to the new address to inform the user
    of the update.

    Args:
        user_id (int): The unique identifier of the user whose email is to be
        updated.

    Returns:
        Response: A redirect to the admin dashboard with a success or error
        message.
    """

    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))

    user = User.query.get_or_404(user_id)
    admin_password = request.form.get('password-email')
    new_email = request.form.get('email')

    # Validate the new email input.
    if new_email == '':
        flash('Please enter the new email address.', category='error')
        return redirect(url_for('admin.admin_dash'))
    # Make sure the email is unique
    elif User.query.filter(
        User.email == new_email, User.id != current_user.id
    ).first():
        flash(
            """The new email address is already in use.
            Please check with the user.""",
            category='error'
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
        old_email = user.email
        user.email = new_email
        admin_email_change(new_email, old_email, user.username)
        db.session.commit()
        flash('Email has been successfully updated!', category='success')
    return redirect(url_for('admin.admin_dash'))


@admin.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    """
    Enables an administrator to reset the password of a user.
    The admin must provide a new password (twice for confirmation) and
    their own password for authentication.

    An email notification is sent to the user's email address to inform
    them of the password change.

    Args:
        user_id (int): The unique identifier of the user whose password is to
        be reset.

    Returns:
        Response: A redirect to the admin dashboard with a success or error
        message.
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
            """The new password cannot be the same as the user\'s
            current password""",
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
        admin_password_change(user.email, user.username)
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
    Allows an administrator to promote or demote a user to or from admin.
    The admin must provide their own password to authorize this change.
    Self-demotion is prohibited to prevent an admin from accidentally
    removing their own privileges.

    Args:
        user_id (int): The unique identifier of the user whose admin status is
        to be toggled.

    Returns:
        Response: A redirect to the admin dashboard with a success or error
        message.
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
            """Please enter your admin password to change the users admin
            status
            """,
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
    Enables an administrator to delete a user's account from the
    database.
    The admin must provide their own password to authorize the deletion.
    Self-deletion is prohibited to ensure that the site has at least one
    functioning admin user and prevent accidental self deletion.

    An email notification is sent to the user's address to inform the user
    of the update.

    Args:
        user_id (int): The unique identifier of the user account to be deleted.

    Returns:
        Response: A redirect to the admin dashboard with a success or error
        message.
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
    admin_account_deletion(user.email, user.username)
    db.session.delete(user)
    db.session.commit()

    flash(f'Account for {user.username} has been deleted.', category='success')

    return redirect(url_for('admin.admin_dash'))


@admin.route('/recipe_admin', methods=['GET', 'POST'])
@login_required
def recipe_admin():
    """
    Retrieves all recipes from the database, paginates them, and renders the
    admin recipes template. This page allows administrators to oversee and
    manage all submitted recipes.

    Returns:
        Response: The rendered admin recipes HTML page.
    """
    recipes = Recipe.query.all()
    admin_password = request.form.get('recipe_admin')

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
    """
    Allows admins to search for users based on a username query.
    If no search term is provided or no users match the search, a message is
    displayed to advise of this.

    Returns:
        Response: The rendered search results page or a redirect to the admin
        dashboard.
    """
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
    """
    Enables administrators to search for recipes based on a recipe name query.
    If no search term is provided or no recipes match the search, a message is
    displayed to advise of this.

    Returns:
        Response: The rendered search results page or a redirect to the admin
        recipes page.
    """
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


@admin.route('/recipes/<int:recipe_id>/confirm_edit', methods=['POST'])
@login_required
def confirm_edit(recipe_id):
    """
    Validates the administrator's password before allowing them to edit a
    specific recipe.
    Ensures that only admins who are not the recipe owners can perform the
    edit.

    Args:
        recipe_id (int): The unique identifier of the recipe to be edited.

    Returns:
        Response:
            - Redirects to the recipe edit page if authentication is
            successful.
            - Redirects to the home page with an error message otherwise.
    """
    # Fetch the recipe or return 404 if not found
    recipe = Recipe.query.get_or_404(recipe_id)

    # Check if the user is an admin and not the owner of the recipe
    if not current_user.is_admin or recipe.user_id == current_user.id:
        flash(
            'You are not authorized to perform this action.',
            category='error'
        )
        return redirect(url_for('routes.home'))

    # Get the admin password from the form
    admin_password = request.form.get('recipe_admin')

    # Check if the admin password is provided
    if not admin_password:
        flash('Please enter your admin password.', category='error')
        return redirect(url_for('routes.home'))

    # Verify the admin password
    if not check_password_hash(current_user.password, admin_password):
        flash('Incorrect admin password.', category='error')
        return redirect(url_for('routes.home'))

    # Redirect to the recipe edit page
    return redirect(url_for('routes.edit_recipe', recipe_id=recipe_id))


@admin.route('/recipes/<int:recipe_id>/confirm_delete', methods=['POST'])
@login_required
def confirm_delete(recipe_id):
    """
    This function allows a logged in admin user to delete a users recipe
    after verifying their admin password.
    The deletion process involves removing the recipe and all its associated
    data using a helper function.

    Args:
        recipe_id (int): The unique identifier of the recipe to be deleted.

    Returns:
        Response:
            - Redirects to the admin recipes page with a success message upon
            successful deletion.
            - Redirects to the home page with an error message if the user is
            unauthorized or provides an incorrect password.
    """
    recipe = Recipe.query.get_or_404(recipe_id)

    # Ensure the current user has admin privileges
    if not current_user.is_admin:
        flash(
            'You are not authorized to perform this action.',
            category='error'
        )
        return redirect(url_for('routes.home'))

    # Retrieve and verify the admin password from the form
    admin_password = request.form.get('recipe_admin')
    if (
        not admin_password
        or not check_password_hash(current_user.password, admin_password)
    ):
        flash('Incorrect admin password.', category='error')
        return redirect(url_for('routes.home'))

    # Delete the recipe using a helper function
    remove_recipe(recipe)
    flash('Recipe has been successfully deleted.', category='success')
    return redirect(url_for('admin.recipe_admin'))
