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


admin = Blueprint('admin', __name__)


@admin.route('/admin_dash', methods=['GET', 'POST'])
@login_required
def admin_dash():
    users = User.query.all()
    return render_template("admin.html", user=current_user, users=users, tag_dict={})


@admin.route('/change_email/<int:user_id>', methods=['POST'])
@login_required
def change_email(user_id):
    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))

    user = User.query.get_or_404(user_id)

    new_email = request.form.get('email')
    if new_email:
        user.email = new_email
        db.session.commit()
        flash('Email has been successfully updated!', category='success')
    else: 
        flash('There was an issue with updating the email',category='error')

    return redirect(url_for('admin.admin_dash'))


@admin.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))
    
    user = User.query.get_or_404(user_id)

    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    current_password_hash = user.password
    
    
    if not password1 or not password2: 
        flash('Both password fields are required', category='error')
    elif password1 != password2:
        flash('Passwords don\'t match!', category='error')
    elif len(password1) <7:
        flash('Password must be at least 7 characters.', category='error')
    elif check_password_hash(current_password_hash, password1):
        flash('Your new password cannot be the same as your current password', category='error')
    else:
        user.password = generate_password_hash(password1, method='pbkdf2:sha512')
        db.session.commit()
        flash('Your password has been successfully changed', category='success')

        return redirect(url_for('admin.admin_dash'))
    
    return redirect(url_for('admin.admin_dash'))


@admin.route('/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
        # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))

    user = User.query.get_or_404(user_id)

    # Make sure the admin isn't demoting themselves
    if user.id == current_user.id:
        flash("You cannot demote your own account, please message another admin to do this", category="error")
        return redirect(url_for('admin.admin_dash'))

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
    # Make sure current user is an admin.
    if not current_user.is_admin:
        flash("Unauthorized access.", category="error")
        return redirect(url_for('routes.home'))
    
    # Pull user details to be deleted. 
    user = User.query.get_or_404(user_id)

    # Make sure the admin isn't deleting themselves
    if user.id == current_user.id:
        flash("You cannot delete your own account, please message another admin to do this", category="error")
        return redirect(url_for('admin.admin_dash'))

    # Delete user. 
    db.session.delete(user)
    db.session.commit()

    flash(f'Account for {user.username} has been deleted.', category='success')

    return redirect(url_for('admin.admin_dash'))