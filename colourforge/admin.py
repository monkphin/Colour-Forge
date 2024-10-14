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


@admin.route('/change_email', methods=['GET', 'POST'])
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

        return redirect(url_for('auth.account', user=current_user, tag_dict={}))

    return render_template('account.html', user=current_user, tag_dict={})


@admin.route('/reset_password', methods=['GET', 'POST'])
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

            return redirect(url_for('auth.account', user=current_user, tag_dict={}))
        
        return render_template('account.html', user=current_user, tag_dict={})

    return render_template('account.html', user=current_user, tag_dict={})


@admin.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        user = current_user
        db.session.delete(user)  
        db.session.commit()

        flash('Your account has been deleted', category='success')
        logout_user()
        return redirect(url_for('routes.home', tag_dict={}))
    
    return render_template('account.html', user=current_user, tag_dict={})